from django.views.decorators.csrf import csrf_exempt
from omnisight_v2.operations import order_list, order_detail


@csrf_exempt
def orderList(request):
    """api view for list order in admin page"""

    page = request.GET.get("page", 1)
    search = request.GET.get("search")
    marketplace = request.GET.get("marketplace")
    sortKey = request.GET.get("sortKey", "order_date")
    sortOrder = request.GET.get("sortOrder", 1)

    response = order_list(
        page=int(page),
        search=search,
        filters={"marketplace": marketplace},
        sort_by=sortKey,
        sort_order=int(sortOrder),
    )
    return response


@csrf_exempt
def orderDetail(request, order_id):

    response = order_detail(order_id)
    return response
