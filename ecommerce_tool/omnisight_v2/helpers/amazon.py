from urllib.parse import quote_plus
from datetime import datetime
from django.conf import settings

from omnisight.models import (
    Order,
    Marketplace,
    Product,
    ProductDetails,
    Pricing,
    Money,
    OrderItems,
    OrderStatus,
)
from omnisight_v2.helpers.common import (
    get_platform_access_token,
    get_or_create,
)
from omnisight_v2.helpers.http import make_http_request


def get_amazon_ae_orders():
    """
    fetch the order details from amazon api

    STEP: 1 -> get amazon access_token
    STEP: 2 -> calls the api and return the reponse
    """
    # required credenticls
    base_url = settings.PLATFORM_BASE_URL
    amazon_api_key = settings.AMAZON_API_KEY
    amazon_secret_key = settings.AMAZON_SECRET_KEY

    amazon_access_token = get_platform_access_token(
        base_url, amazon_api_key, amazon_secret_key
    ).get("access_token")

    amazon_order_data: dict = make_http_request(
        "GET", "/amazon-ae/orders/", base_url, amazon_access_token
    )

    amazon_order_data["access_token"] = amazon_access_token

    return amazon_order_data


def get_amazon_catalog(amazon_access_token: str) -> dict:

    # required credenticls
    base_url = settings.PLATFORM_BASE_URL

    amazon_catalog_data: dict = make_http_request(
        "GET", "/amazon-ae/catalog/items/", base_url, amazon_access_token
    )

    return amazon_catalog_data


def get_amazon_inventory_data(amazon_access_token: str) -> dict:

    # required credenticls
    base_url = settings.PLATFORM_BASE_URL

    amazon_catalog_data: dict = make_http_request(
        "GET", "/amazon-ae/fba/inventory/", base_url, amazon_access_token
    )

    return amazon_catalog_data


def get_amazon_catalog_item(amazon_access_token: str, asin: str) -> dict:
    """returns single catalog response"""

    base_url = settings.PLATFORM_BASE_URL
    catalog_data = make_http_request(
        "GET",
        "amazon-ae/catalog/items/",
        base_url,
        amazon_access_token,
        params={"asin": asin},
    )

    return catalog_data


def save_amazon_ae_orders(
    amazon_order_data: dict,
    marketplace_doc: Marketplace,
    amazon_access_token: str,
) -> None:
    base_url = settings.PLATFORM_BASE_URL
    order_data: list[dict] = amazon_order_data.get("payload", {}).get("Orders", [])

    print(f"[INFO] Total orders fetched: {len(order_data)}")

    for data in order_data:
        amazon_order_id = data.get("AmazonOrderId")
        order_status = data.get("OrderStatus")
        purchase_date = data.get("PurchaseDate")
        buyer_info = data.get("BuyerInfo", {})
        order_total = float(data.get("OrderTotal", {}).get("Amount", 0.0))
        currency = data.get("OrderTotal", {}).get("CurrencyCode", "")

        print(
            f"[INFO] Processing order: {amazon_order_id}, Status: {order_status}, Total: {order_total}"
        )

        # Create or fetch the high-level Order document
        order_doc, _ = get_or_create(
            Order,
            purchase_order_id=amazon_order_id,
            defaults={
                "order_status": order_status,
                "order_total": order_total,
                "currency": currency,
                "customer_email_id": buyer_info.get("BuyerEmail", ""),
                "customer_name": buyer_info.get("BuyerName", ""),
                "order_date": (
                    datetime.strptime(purchase_date, "%Y-%m-%dT%H:%M:%SZ")
                    if purchase_date
                    else None
                ),
            },
        )

        # Fetch order items from API
        order_items_response: dict = make_http_request(
            "GET",
            f"/amazon-ae/orders/{quote_plus(amazon_order_id)}/orderItems/",
            base_url,
            amazon_access_token,
        )

        items: list[dict] = order_items_response.get("payload", {}).get(
            "OrderItems", []
        )
        print(f"[INFO] Found {len(items)} items for order {amazon_order_id}")

        saved_order_items = []
        order_details_items = []

        for item in items:
            asin: str = item.get("ASIN")
            order_item_id = item.get("OrderItemId", asin)
            quantity_ordered = int(item.get("QuantityOrdered", 0))
            item_price = float(item.get("ItemPrice", {}).get("Amount", 0.0))
            item_currency = item.get("ItemPrice", {}).get("CurrencyCode", "$")

            print(
                f"[DEBUG] Item: {order_item_id}, ASIN: {asin}, Quantity: {quantity_ordered}, Price: {item_price}"
            )

            # Fetch catalog data
            catalog_items = (
                get_amazon_catalog_item(amazon_access_token, asin)
                .get("payload", {})
                .get("items", [])
            )
            catalog_data = catalog_items[0] if catalog_items else {}
            product_sku = catalog_data.get("sku", item.get("SellerSKU", asin))
            product_title = catalog_data.get(
                "title", item.get("Title", "Unknown Product")
            )

            # Create or fetch the Product document
            product_doc, _ = get_or_create(
                Product,
                asin=asin,
                defaults={
                    "sku": product_sku,
                    "product_title": product_title,
                    "product_description": catalog_data.get("description", ""),
                    "brand_name": catalog_data.get("brand"),
                    "category": catalog_data.get("category"),
                    "price": float(catalog_data.get("price", item_price)),
                    "currency": catalog_data.get("currency", item_currency),
                    "quantity": catalog_data.get("quantity", 0),
                    "image_url": catalog_data.get("image_url"),
                    "marketplace_id": marketplace_doc,
                    "total_cogs": float(catalog_data.get("total_cogs", 0.0)),
                    "product_cost": float(catalog_data.get("product_cost", 0.0)),
                    "pack_size": catalog_data.get("pack_size"),
                },
            )

            # Create OrderItems document
            order_item_doc = OrderItems(
                OrderId=amazon_order_id,
                Platform="Amazon-AE",
                created_date=datetime.utcnow(),
                document_created_date=datetime.utcnow(),
            )

            order_item_doc.ProductDetails = ProductDetails(
                product_id=product_doc,
                Title=product_title,
                SKU=product_sku,
                ASIN=asin,
                QuantityOrdered=quantity_ordered,
                QuantityShipped=int(item.get("QuantityShipped", 0)),
            )

            order_item_doc.Pricing = Pricing(
                ItemPrice=Money(CurrencyCode=item_currency, Amount=item_price)
            )

            order_item_doc.Fulfillment = None
            order_item_doc.OrderStatus = OrderStatus(
                Status=order_status,
                StatusDate=(
                    datetime.strptime(purchase_date, "%Y-%m-%dT%H:%M:%SZ")
                    if purchase_date
                    else datetime.utcnow()
                ),
            )

            order_item_doc.BuyerInfo = None
            order_item_doc.TaxCollection = None

            order_item_doc.save()
            saved_order_items.append(order_item_doc)

            # Add to order_details items
            order_details_items.append(
                {
                    "item_id": str(order_item_doc.id),
                    "sku": product_sku,
                    "name": product_title,
                    "quantity": quantity_ordered,
                    "price": {"total_price": item_price},
                }
            )

        # Build full order_details
        order_details_list = [
            {
                "order_nr": amazon_order_id,
                "order_date": (
                    datetime.strptime(purchase_date, "%Y-%m-%dT%H:%M:%SZ").isoformat()
                    if purchase_date
                    else datetime.utcnow().isoformat()
                ),
                "status": order_status,
                "customer": {
                    "first_name": (
                        buyer_info.get("BuyerName", "").split(" ")[0]
                        if buyer_info.get("BuyerName")
                        else ""
                    ),
                    "last_name": (
                        " ".join(buyer_info.get("BuyerName", "").split(" ")[1:])
                        if buyer_info.get("BuyerName")
                        else ""
                    ),
                },
                "payment": {"total": {"value": order_total}},
                "items": order_details_items,
            }
        ]

        print(
            f"[INFO] Saving order_details for order {amazon_order_id}: {order_details_list}"
        )

        # Link everything and save
        order_doc.order_items = saved_order_items
        order_doc.marketplace_id = marketplace_doc
        order_doc.marketplace = "amazon"
        order_doc.order_details = order_details_list
        order_doc.save()

        print(
            f"[INFO] Order {amazon_order_id} saved successfully with {len(order_details_items)} items"
        )
