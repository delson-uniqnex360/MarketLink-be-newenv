from omnisight.models import Order


def list_unique_customers(
    page=1,
    page_size=24,
    search=None,
    filters=None,
    sort_by="total_purchase_amount",
    sort_order=-1,
):
    """
    List unique customers with stats like total orders, items, purchase amount.
    Includes debug logs to inspect why certain marketplaces like Amazon may be missing.
    Supports search, filters (marketplace, date range, order status), pagination, and sorting.
    """

    collection = Order._get_collection()

    # -------------------------
    # Build base match stage
    # -------------------------
    match_stage = {}

    if filters:
        # Date range filter
        if filters.get("date_from") and filters.get("date_to"):
            match_stage["order_date"] = {
                "$gte": filters["date_from"],
                "$lte": filters["date_to"],
            }
        # Order status filter
        if filters.get("order_status"):
            match_stage["order_status"] = filters["order_status"]

    # Search by customer name or email
    if search:
        match_stage["$or"] = [
            {"customer_name": {"$regex": search, "$options": "i"}},
            {"customer_email_id": {"$regex": search, "$options": "i"}},
        ]

    # Remove empty customers
    base_match = {
        "$and": [
            match_stage,
            {
                "$or": [
                    {"customer_name": {"$nin": [None, ""]}},
                    {"customer_email_id": {"$nin": [None, ""]}},
                ]
            },
        ]
    }

    pipeline = []

    # -------------------------
    # Initial match
    # -------------------------
    pipeline.append({"$match": base_match})

    # -------------------------
    # Lookup Marketplace
    # -------------------------
    pipeline.append(
        {
            "$lookup": {
                "from": "marketplace",  # must match your collection name
                "localField": "marketplace_id",
                "foreignField": "_id",
                "as": "marketplace_data",
            }
        }
    )
    pipeline.append(
        {"$unwind": {"path": "$marketplace_data", "preserveNullAndEmptyArrays": True}}
    )

    # Filter by marketplace name (after unwind) - case-insensitive
    if filters and filters.get("marketplace"):
        pipeline.append(
            {
                "$match": {
                    "marketplace_data.name": {
                        "$regex": f"^{filters['marketplace']}$",
                        "$options": "i",
                    }
                }
            }
        )

    # -------------------------
    # Debug: Preview first 10 orders after match + lookup
    # -------------------------
    debug_preview_stage = [
        {"$limit": 10},
        {
            "$project": {
                "customer_name": 1,
                "customer_email_id": 1,
                "marketplace_id": 1,
                "marketplace_data": 1,
            }
        },
    ]

    # -------------------------
    # Group by customer + marketplace
    # -------------------------
    # Unwind order_details
    pipeline.append(
        {"$unwind": {"path": "$order_details", "preserveNullAndEmptyArrays": True}}
    )

    # Unwind items inside order_details
    pipeline.append(
        {
            "$unwind": {
                "path": "$order_details.items",
                "preserveNullAndEmptyArrays": True,
            }
        }
    )

    # Group by customer + marketplace
    pipeline.append(
        {
            "$group": {
                "_id": {
                    "customer_name": "$customer_name",
                    "customer_email_id": "$customer_email_id",
                    "marketplace_id": "$marketplace_id",
                    "marketplace_name": "$marketplace_data.name",
                },
                "total_orders": {"$sum": 1},
                "total_order_items": {
                    "$sum": {"$ifNull": ["$order_details.items.quantity", 1]}
                },
                "total_purchase_amount": {"$sum": "$order_total"},
                "first_order_date": {"$min": "$order_date"},
                "last_order_date": {"$max": "$order_date"},
            }
        }
    )

    # -------------------------
    # Calculate average order value
    # -------------------------
    pipeline.append(
        {
            "$addFields": {
                "avg_order_value": {
                    "$cond": [
                        {"$gt": ["$total_orders", 0]},
                        {"$divide": ["$total_purchase_amount", "$total_orders"]},
                        0,
                    ]
                }
            }
        }
    )

    # -------------------------
    # Flatten output
    # -------------------------
    pipeline.append(
        {
            "$project": {
                "_id": 0,
                "customer_name": "$_id.customer_name",
                "customer_email_id": "$_id.customer_email_id",
                "marketplace_id": {"$toString": "$_id.marketplace_id"},
                "marketplace_name": "$_id.marketplace_name",
                "total_orders": 1,
                "total_order_items": 1,
                "total_purchase_amount": 1,
                "avg_order_value": 1,
                "first_order_date": 1,
                "last_order_date": 1,
            }
        }
    )

    # -------------------------
    # Get total count before pagination
    # -------------------------
    count_pipeline = pipeline.copy()
    count_pipeline.append({"$count": "total"})
    total_result = list(collection.aggregate(count_pipeline))
    total = total_result[0]["total"] if total_result else 0

    # -------------------------
    # Sorting + pagination
    # -------------------------
    pipeline.append({"$sort": {sort_by: sort_order}})
    pipeline.append({"$skip": (page - 1) * page_size})
    pipeline.append({"$limit": page_size})

    # -------------------------
    # Execute final pipeline
    # -------------------------
    data = list(collection.aggregate(pipeline))

    return {
        "data": data,
        "page": page,
        "page_size": page_size,
        "total": total,
    }
