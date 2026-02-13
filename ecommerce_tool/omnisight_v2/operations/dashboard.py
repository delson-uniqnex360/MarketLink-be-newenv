from omnisight.models import Order
from datetime import datetime, timedelta
from typing import List, Optional


def get_daily_orders(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    marketplace: Optional[List[str]] = None,
):
    """
    Returns daily order counts for a given date range (or all orders if start_date/end_date is None),
    optionally filtered by marketplaces.

    Output format:
    [
        {'date': '2026-02-01', 'total_orders': 5, 'noon': 2, 'amazon': 3},
        {'date': '2026-02-02', 'total_orders': 8, 'noon': 5, 'amazon': 3},
        ...
    ]
    """
    if marketplace is None:
        marketplaces = ["noon", "amazon"]  # default marketplaces
    else:
        marketplaces = [marketplace]

    # Determine start and end dates
    if start_date is None or end_date is None:
        first_order = Order.objects.order_by("order_date").first()
        last_order = Order.objects.order_by("-order_date").first()
        if first_order and last_order:
            start_date = start_date or first_order.order_date
            end_date = end_date or last_order.order_date
        else:
            return []

    # Initialize daily counts
    num_days = (end_date - start_date).days + 1
    daily_counts = {}
    for i in range(num_days):
        day = start_date + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        daily_counts[day_str] = {"date": day_str, "total_orders": 0}
        for m in marketplaces:
            daily_counts[day_str][m] = 0

    # Build query
    query = {"order_date__gte": start_date, "order_date__lte": end_date}
    if marketplaces:
        query["marketplace__in"] = marketplaces

    orders = Order.objects(**query).only("order_date", "marketplace")

    # Count orders per day and per marketplace
    for order in orders:
        day_key = order.order_date.strftime("%Y-%m-%d")
        daily_counts[day_key]["total_orders"] += 1
        if order.marketplace in marketplaces:
            daily_counts[day_key][order.marketplace] += 1

    # Convert to sorted list
    result = [
        daily_counts[(start_date + timedelta(n)).strftime("%Y-%m-%d")]
        for n in range(num_days)
    ]
    return result


def calculate_revenue_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    marketplace: Optional[List[str]] = None,
):
    """
    Calculate revenue KPIs:
    - total revenue
    - revenue per marketplace
    - revenue per item
    - average order value
    """

    if marketplace is None:
        marketplaces = ["noon", "amazon"]
    else:
        marketplaces = [marketplace]

    # Determine start and end dates
    # If either date is missing, set default range from first/last order

    if start_date is None or end_date is None:
        first_order = Order.objects.order_by("order_date").first()
        last_order = Order.objects.order_by("-order_date").first()
        if not first_order or not last_order:
            return {
                "total_revenue": 0,
                "revenue_per_marketplace": {m: 0 for m in marketplaces},
                "revenue_per_item": {},
                "average_order_value": 0,
            }
        start_date = start_date or first_order.order_date
        end_date = end_date or last_order.order_date

    # Validate range
    if start_date > end_date:
        start_date, end_date = end_date, start_date  # swap or return empty

    # Build query
    query = {"order_date__gte": start_date, "order_date__lte": end_date}
    if marketplaces:
        query["marketplace__in"] = marketplaces

    orders = Order.objects(**query).only(
        "order_total", "marketplace", "order_details", "order_items"
    )

    total_revenue = 0
    revenue_per_marketplace = {m: 0 for m in marketplaces}
    revenue_per_item = {}  # sku: revenue
    total_orders_count = 0

    for order in orders:
        total_orders_count += 1
        total_revenue += order.order_total or 0
        if order.marketplace in marketplaces:
            revenue_per_marketplace[order.marketplace] += order.order_total or 0

        # Revenue per item
        if hasattr(order, "order_details") and order.order_details:
            for detail in order.order_details:
                items = detail.get("items", [])
                for item in items:

                    sku = item.get("name", "Unknown")
                    item_total = item.get("price", {}).get("total_price", 0)
                    revenue_per_item[sku] = revenue_per_item.get(sku, 0) + item_total

    average_order_value = (
        total_revenue / total_orders_count if total_orders_count > 0 else 0
    )

    return {
        "total_revenue": total_revenue,
        "revenue_per_marketplace": revenue_per_marketplace,
        "revenue_per_item": revenue_per_item,
        "average_order_value": average_order_value,
    }


def dashboard_kpi_metrics(marketplace=None, start_date=None, end_date=None):
    # Convert request strings to datetime

    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d")


    order_graph_data = get_daily_orders(start_date, end_date, marketplace)
    revenue_metrics = calculate_revenue_metrics(start_date, end_date, marketplace)

    return {
        "order_graph_data": order_graph_data,
        "revenue_metrics": revenue_metrics,
    }
