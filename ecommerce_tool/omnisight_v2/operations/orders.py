from django.http import JsonResponse
from mongoengine import Q, DoesNotExist

from omnisight.models import Marketplace, Order, OrderItems
from omnisight_v2.helpers import (
    get_amazon_ae_orders,
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

    save_noon_ae_orders(noon_data, noon_marketplace_doc, noon_access_token)

    return JsonResponse({"message": "Orders synced successfully"})



def order_list(
    page=1, page_size=24, search=None, filters=None, sort_by="order_date", sort_order=-1
):
    filters = filters or {}
    filters = {k: v for k, v in filters.items() if k is not None and k != ""}

    query = Q()

    # --- Marketplace filter ---
    if "marketplace" in filters:
        marketplaces = filters["marketplace"]
        if marketplaces:
            if not isinstance(marketplaces, list):
                marketplaces = [marketplaces]
            query &= Q(marketplace__in=marketplaces)

    # --- Status filter ---
    if "status" in filters:
        statuses = filters["status"]
        if not isinstance(statuses, list):
            statuses = [statuses]
        query &= Q(order_status__in=statuses)

    # --- Search filter ---
    if search:
        search = search.strip()
        query &= Q(purchase_order_id__icontains=search) | Q(
            customer_name__icontains=search
        )

    total_count = Order.objects(query).count()

    # --- Determine sort ---
    reverse = sort_order == -1
    sort_prefix = "-" if sort_order == -1 else ""

    # --- Case: computed fields ---
    if sort_by in ["items_count", "total_amount"]:
        # Fetch all matching orders and sort in Python before pagination
        orders_list = list(Order.objects(query))
        if sort_by == "items_count":
            orders_list.sort(
                key=lambda o: getattr(o, "items_order_quantity", 0)
                or getattr(o, "ProductDetails", {}).get("QuantityOrdered", 0),
                reverse=reverse,
            )
        elif sort_by == "total_amount":
            orders_list.sort(
                key=lambda o: getattr(o, "order_total", 0)
                or getattr(o, "Pricing", {}).get("ItemPrice", {}).get("Amount", 0),
                reverse=reverse,
            )
        # --- Apply pagination after sorting ---
        start = (page - 1) * page_size
        end = start + page_size
        orders_list = orders_list[start:end]

    else:
        # --- Regular DB sort (case-insensitive for customer_name) ---
        orders_qs = Order.objects(query)
        if sort_by == "customer_name":
            orders_qs = orders_qs.order_by(sort_prefix + "customer_name").collation(
                {"locale": "en", "strength": 2}
            )
        else:
            orders_qs = orders_qs.order_by(sort_prefix + sort_by)
        skip = (page - 1) * page_size
        orders_list = list(orders_qs.skip(skip).limit(page_size))

    # --- Transform to response dict ---
    data = []
    for order in orders_list:
        id = str(order.id)
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
                "id": id,
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


def order_detail(order_id: str) -> dict:
    """
    Fetch order from MongoDB via MongoEngine and return structured detail for frontend.
    """
    try:
        order = Order.objects.get(id=order_id)
    except DoesNotExist:
        return {"error": "Order not found"}

    # Structure the response
    order_info = {
        "order_id": str(order.id),
        "purchase_order_id": order.purchase_order_id,
        "status": order.order_status,
        "order_total": order.order_total,
        "currency": order.currency,
        "customer_name": order.customer_name,
        "geo": order.geo,
        "shipping_cost": order.shipping_price or 0,
        "items_order_quantity": order.items_order_quantity or 0,
        "order_date": order.order_date.isoformat() if order.order_date else None,
        "items": [],
    }

    # Flatten items from order_details
    for detail in order.order_details or []:
        for item in detail.get("items", []):
            order_info["items"].append(
                {
                    "item_id": item.get("item_id"),
                    "sku": item.get("sku"),
                    "name": item.get("name"),
                    "quantity": item.get("quantity"),
                    "total_price": item.get("price", {}).get("total_price"),
                }
            )

    return order_info
