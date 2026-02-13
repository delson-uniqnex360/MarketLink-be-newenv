from mongoengine.queryset.visitor import Q
from mongoengine import DoesNotExist

from omnisight.models import Product


def product_list(
    page=1,
    page_size=24,
    search=None,
    filters=None,
    sort_by="created_at",
    sort_order=-1,
):
    filters = filters or {}
    filters = {k: v for k, v in filters.items() if k}

    query = Q()

    # --- Search filter (ASIN, SKU, Product Title) ---
    if search:
        search = search.strip()
        search_query = (
            Q(asin__icontains=search)
            | Q(sku__icontains=search)
            | Q(product_title__icontains=search)
        )
        query = query & search_query

    total_count = Product.objects(query).count()

    reverse = sort_order == -1
    sort_prefix = "-" if sort_order == -1 else ""

    # --- Computed field sorting (if needed) ---
    if sort_by in ["net_profit", "total_cogs"]:
        products_list = list(Product.objects(query))

        products_list.sort(
            key=lambda p: getattr(p, sort_by, 0),
            reverse=reverse,
        )

        start = (page - 1) * page_size
        end = start + page_size
        products_list = products_list[start:end]

    else:
        products_qs = Product.objects(query).order_by(sort_prefix + sort_by)
        skip = (page - 1) * page_size
        products_list = list(products_qs.skip(skip).limit(page_size))

    # --- Transform response ---
    data = []

    for product in products_list:
        data.append(
            {
                "id": str(product.id),
                "asin": getattr(product, "asin", None),
                "sku": getattr(product, "sku"),
                "product_title": getattr(product, "product_title"),
                "price": getattr(product, "price", 0),
                "currency": getattr(product, "currency", ""),
                "quantity": getattr(product, "quantity", 0),
                "net_profit": getattr(product, "net_profit", 0),
                "cogs": getattr(product, "cogs", 0),
                "total_cogs": round(getattr(product, "total_cogs", 0), 2),
                "page_views": getattr(product, "page_views", 0),
                "sessions": getattr(product, "sessions", 0),
                "listing_quality_score": getattr(product, "listing_quality_score", 0),
                "new_product": getattr(product, "new_product", False),
                "is_duplicate": getattr(product, "is_duplicate", False),
                "created_at": getattr(product, "created_at", None),
            }
        )

    return {
        "data": data,
        "page": page,
        "page_size": page_size,
        "total": total_count,
    }



def product_detail(product_id: str) -> dict:
    """
    Fetch a product from MongoDB via MongoEngine and return a structured detail for frontend.
    """
    try:
        product = Product.objects.get(id=product_id)
    except DoesNotExist:
        return {"error": "Product not found"}

    # Flatten product data
    product_info = {
        "id": str(product.id),
        "asin": getattr(product, "asin", None),
        "sku": getattr(product, "sku", None),
        "product_title": getattr(product, "product_title", ""),
        "product_description": getattr(product, "product_description", ""),
        "price": getattr(product, "price", 0),
        "currency": getattr(product, "currency", ""),
        "quantity": getattr(product, "quantity", 0),
        "net_profit": getattr(product, "net_profit", 0),
        "total_cogs": round(getattr(product, "total_cogs", 0), 2),
        "new_product": getattr(product, "new_product", False),
        "is_duplicate": getattr(product, "is_duplicate", False),
        "brand_name": getattr(product, "brand_name", ""),
        "category": getattr(product, "category", ""),
        "pack_size": getattr(product, "pack_size", 0),
        "will_ship_internationally": getattr(
            product, "will_ship_internationally", False
        ),
        "fullfillment_by_channel": getattr(product, "fullfillment_by_channel", False),
        "channel_fee": getattr(product, "channel_fee", 0),
        "image_url": getattr(product, "image_url", ""),
        "product_created_date": getattr(product, "product_created_date", None),
        "producted_last_updated_date": getattr(
            product, "producted_last_updated_date", None
        ),
    }

    return product_info
