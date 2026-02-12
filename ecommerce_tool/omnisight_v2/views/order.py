from django.views.decorators.csrf import csrf_exempt
from omnisight_v2.operations import order_list


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
