from django.http import JsonResponse
from mongoengine import Q

from omnisight.models import Marketplace, Order, OrderItems
from omnisight_v2.helpers import (
    get_amazon_ae_orders,
    get_amazon_catalog,
    get_amazon_inventory_data,
    save_amazon_ae_orders,
    get_noon_ae_orders,
    save_noon_ae_orders,
    get_or_create,
)


def sync_amazon_noon_order_data():
    """
    saves details about both amazon and noon
    """

    # common required data's
    # 1. market place
    # 2. catalog
    # 3. inventory

    # market place
    amazon_marketplace_doc, _ = get_or_create(Marketplace, name="amazon")
    noon_marketplace_doc, _ = get_or_create(Marketplace, name="noon")

    # gets the required data
    amazon_data = get_amazon_ae_orders()
    noon_data = get_noon_ae_orders()

    # get the token
    amazon_access_token = amazon_data.get("access_token")
    noon_access_token = noon_data.get("access_token")

    # saves the required data
    save_amazon_ae_orders(
        amazon_data,
        amazon_marketplace_doc,
        amazon_access_token,
    )

    # save_noon_ae_orders(noon_data, noon_marketplace_doc, noon_access_token)

    return JsonResponse({"message": "Orders synced successfully"})


def order_list(
    page=1, page_size=24, search=None, filters=None, sort_by="order_date", sort_order=-1
):
    print(filters,search, sort_by, sort_order )
    filters = filters or {}
    filters = {k: v for k, v in (filters or {}).items() if k is not None and k != ""}

    query = Q()

    if "marketplace" in filters:
        marketplaces = filters["marketplace"]
        if marketplaces:  # only filter if not empty string / None
            if not isinstance(marketplaces, list):
                marketplaces = [marketplaces]
            query &= Q(marketplace__in=marketplaces)

    if "status" in filters:
        statuses = filters["status"]
        if not isinstance(statuses, list):
            statuses = [statuses]
        query &= Q(order_status__in=statuses)

    # if "date_range" in filters:
    #     start_date, end_date = filters["date_range"]
    #     query &= Q(order_date__gte=start_date, order_date__lte=end_date)

    # --- Search on order_id or customer_name ---
    if search:
        search = search.strip()
        query &= Q(purchase_order_id__icontains=search) | Q(
            customer_name__icontains=search
        )

    # --- Sorting ---
    sort_prefix = "-" if sort_order == -1 else ""
    sort_expr = f"{sort_prefix}{sort_by}"

    # --- Pagination ---
    skip = (page - 1) * page_size
    orders_qs = Order.objects(query).order_by(sort_expr).skip(skip).limit(page_size)
    total_count = Order.objects(query).count()

    # --- Transform to response dict ---
    data = []
    for order in orders_qs:
        order_id = getattr(order, "purchase_order_id", None) or getattr(
            order, "OrderId", None
        )
        marketplace = getattr(order, "marketplace", None) or getattr(
            order, "Platform", None
        )
        order_date = getattr(order, "order_date", None) or getattr(
            order, "created_date", None
        )
        customer_name = getattr(order, "customer_name", None) or getattr(
            order, "OrderDetails", {}
        ).get("customer_name", "")
        status = getattr(order, "order_status", None) or getattr(
            order, "OrderStatus", {}
        ).get("Status", "")
        total_amount = getattr(order, "order_total", None) or getattr(
            order, "Pricing", {}
        ).get("ItemPrice", {}).get("Amount", 0)
        currency = getattr(order, "currency", None) or getattr(
            order, "Pricing", {}
        ).get("ItemPrice", {}).get("CurrencyCode", "")
        items_count = getattr(order, "items_order_quantity", None) or getattr(
            order, "ProductDetails", {}
        ).get("QuantityOrdered", 0)
        shipping_price = getattr(order, "shipping_price", 0)
        sync_status = getattr(order, "shipstation_synced", False)

        data.append(
            {
                "order_id": order_id,
                "marketplace": marketplace,
                "order_date": order_date,
                "customer_name": customer_name,
                "status": status,
                "total_amount": total_amount,
                "currency": currency,
                "items_count": items_count,
                "shipping_price": shipping_price,
                "sync_status": sync_status,
                "actions": ["View", "Edit"],
            }
        )

    return {"data": data, "page": page, "page_size": page_size, "total": total_count}


