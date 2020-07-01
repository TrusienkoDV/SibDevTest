from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.cache import cache
from deals.models import Deal
from django.db.models import Sum
from collections import defaultdict
from deals.serializers import DealSerializer
import csv


class DealsView(APIView):

    @transaction.atomic
    def get(self, request):
        cache_version = cache.get('version')
        cache_data = cache.get('deals_get_data', version=cache_version)
        if cache_data is not None:
            return Response(data={'response': cache_data})
        deals_spent_money = Deal.objects \
                                .values('customer') \
                                .annotate(spent_money=Sum('total')) \
                                .order_by('-spent_money')[0:5]
        customers = [deal['customer'] for deal in deals_spent_money]
        customer_to_spent_money = {deal['customer']: deal['spent_money'] for deal in deals_spent_money}
        deals_item = Deal.objects.filter(customer__in=customers).values('customer', 'item')
        items_all = defaultdict(set)
        customer_to_items = defaultdict(set)
        for deal in deals_item:
            customer_to_items[deal['customer']].add(deal['item'])
            items_all[deal['item']].add(deal['customer'])
        data = [
            {
                'username': customer,
                'spent_money': customer_to_spent_money[customer],
                'gems': [item for item in customer_to_items[customer] if len(items_all[item]) >= 2]
            } for customer in customers
        ]
        cache.set('deals_get_data', data, version=cache_version)
        return Response(data={'response': data})

    @transaction.atomic
    def post(self, request):
        csv_file = request.FILES.get('deals')
        if csv_file is None:
            return Response({'deals': 'file is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
        except csv.Error:
            return Response({'deals': 'invalid csv file'}, status=status.HTTP_400_BAD_REQUEST)
        deals_to_create = []
        for row in data:
            deal = DealSerializer(data=row)
            deal.is_valid(True)
            deals_to_create.append(Deal(**row))
        Deal.objects.all().delete()
        Deal.objects.bulk_create(deals_to_create)
        cache.incr('version')
        return Response()
