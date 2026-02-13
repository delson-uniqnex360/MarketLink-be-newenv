from django.urls import path
from omnisight_v2.views import (
    syncOrders,
    customerOrderList,
    orderList,
    orderDetail,
    dashboardKPIMetrics,
    productListAPI,
)


urlpatterns = [
    path("syncOrders/", syncOrders, name="syncOrders"),
    # customer
    path("customer/customerOrderList/", customerOrderList, name="customerOrderList"),
    # order
    path("order/orderList/", orderList, name="orderList"),
    path("order/orderDetail/<str:order_id>/", orderDetail, name="orderDetail"),
    # dashboard
    path(
        "dashboard/dashboardKPIMetrics/",
        dashboardKPIMetrics,
        name="dashboardKPIMetrics",
    ),
    # product
    path(
        "product/productListAPI/",
        productListAPI,
        name="productListAPI",
    ),
]
