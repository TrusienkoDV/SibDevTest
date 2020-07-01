from django.contrib import admin
from django.urls import path
from rest_framework import routers
from deals.views import DealsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DealsView.as_view())
]
