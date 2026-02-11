from django.urls import path
from omnisight_v2.views import syncOrders, customerOrderList


urlpatterns = [
    path("syncOrders/", syncOrders, name="syncOrders"),
    # customer
    path("customer/customerOrderList/", customerOrderList, name="customerOrderList"),
]
