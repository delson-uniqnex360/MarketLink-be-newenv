from django.urls import path
from omnisight_v2.views import (
    syncOrders,
    customerOrderList,
    orderList,
    dashboardKPIMetrics,
)


urlpatterns = [
    path("syncOrders/", syncOrders, name="syncOrders"),
    # customer
    path("customer/customerOrderList/", customerOrderList, name="customerOrderList"),
    # order
    path("order/orderList/", orderList, name="orderList"),
    # dashboard
    path(
        "dashboard/dashboardKPIMetrics/",
        dashboardKPIMetrics,
        name="dashboardKPIMetrics",
    ),
]
