import os
from datetime import datetime
from urllib.parse import quote_plus
from typing import List, Dict, Any

from django.conf import settings

from omnisight.models import (
    Order,
    OrderItems,
    Product,
    ProductDetails,
    Pricing,
    Money,
    Marketplace,
    OrderStatus,
)
from omnisight_v2.helpers.common import get_platform_access_token, get_or_create
from omnisight_v2.helpers.http import make_http_request


def get_noon_ae_orders():
    """
    fetch the order details from noon api

    STEP: 1 -> get noon access_token
    STEP: 2 -> calls the api and return the reponse
    STEP: 3 -> get noon access_token
    STEP: 4 -> call the noon api and return the response
    """
    # required credenticls
    base_url = os.getenv("PLATFORM_BASE_URL")

    noon_api_key = os.getenv("NOON_API_KEY")
    noon_secret_key = os.getenv("NOON_SECRET_KEY")

    noon_access_token = get_platform_access_token(
        base_url, noon_api_key, noon_secret_key
    ).get("access_token")

    noon_order_data: dict = make_http_request(
        "GET", "/noon-ae/orders/", base_url, noon_access_token
    )

    noon_order_data["access_token"] = noon_access_token

    return noon_order_data


def save_noon_ae_orders(
    noon_orders_response: Dict[str, Any],
    marketplace_doc: Marketplace,
    noon_access_token: str,
) -> None:
    """
    Saves Noon AE orders + items + products using the same schema as Amazon AE.
    """

    base_url = settings.PLATFORM_BASE_URL
    orders_list: List[Dict] = noon_orders_response.get("data", {}).get("orders", [])

    for order_data in orders_list:
        noon_order_id = order_data.get("order_nr")
        order_status = order_data.get("status")
        order_date_str = order_data.get("order_date")
        customer = order_data.get("customer", {})
        payment = order_data.get("payment", {})
        items = order_data.get("items", [])

        order_total = float(payment.get("total", {}).get("value", 0.0))
        currency = "AED"  # Noon AE → fixed currency

        # Parse date (example uses full ISO with timezone)
        order_date = None
        if order_date_str:
            try:
                order_date = datetime.fromisoformat(
                    order_date_str.replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass

        # 1. Create or get the high-level Order document
        order_doc, _ = get_or_create(
            Order,
            purchase_order_id=noon_order_id,
            defaults={
                "order_status": order_status,
                "order_total": order_total,
                "currency": currency,
                "customer_email_id": "",
                "customer_name": f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip(),
                "order_date": order_date,
                "marketplace_id": marketplace_doc,
            },
        )

        saved_order_items = []

        for item in items:
            noon_item_id = item.get("item_id")  # e.g. "N-ITEM-28"
            sku = item.get("sku")  # e.g. "UB-40009-X"
            quantity_ordered = item.get("quantity", 0)
            item_total_price = float(item.get("price", {}).get("total_price", 0.0))

            if not sku:
                continue  # skip items without SKU

            # 2. Fetch product details from Noon catalog/search
            product_response = make_http_request(
                "GET",
                f"/noon-ae/products/?search={quote_plus(sku)}",
                base_url,
                noon_access_token,
            )

            products_list = product_response.get("data", {}).get("products", [])
            product_data = products_list[0] if products_list else {}

            # 3. Create or get Product document
            product_doc, _ = get_or_create(
                Product,
                sku=sku,
                defaults={
                    "product_title": product_data.get("name", item.get("name", "")),
                    "brand_name": product_data.get("brand", ""),
                    "category": "",
                    "price": float(product_data.get("price", {}).get("value", 0.0)),
                    "currency": product_data.get("price", {}).get("currency", "AED"),
                    "quantity": int(product_data.get("stock", {}).get("quantity", 0)),
                },
            )

            # 4. Create OrderItems document
            order_item_doc = OrderItems(
                OrderId=noon_order_id,
                Platform="Noon-AE",
                created_date=datetime.utcnow(),
                document_created_date=datetime.utcnow(),
            )

            # 5. Fill embedded ProductDetails
            order_item_doc.ProductDetails = ProductDetails(
                product_id=product_doc,
                Title=product_data.get("name", item.get("name", "")),
                SKU=sku,
                ASIN="",
                QuantityOrdered=quantity_ordered,
                QuantityShipped=0,
            )

            # 6. Pricing
            order_item_doc.Pricing = Pricing(
                ItemPrice=Money(
                    CurrencyCode=currency,
                    Amount=item_total_price / max(quantity_ordered, 1),
                )
            )

            # 7. Optional fields (can be enriched from order details endpoint later)
            order_item_doc.Fulfillment = None
            order_item_doc.OrderStatus = OrderStatus(
                Status=order_status,
                StatusDate=order_date or datetime.utcnow(),
            )
            order_item_doc.BuyerInfo = None
            order_item_doc.TaxCollection = None
            order_item_doc.save()
            saved_order_items.append(order_item_doc)

        # 8. Link items back to order
        order_doc.order_items = saved_order_items
        order_doc.marketplace_id = marketplace_doc
        order_doc.marketplace = "noon"
        order_doc.save()

    # Optional: return count or list of processed order IDs
    return None
