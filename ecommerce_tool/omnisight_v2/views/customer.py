from django.views.decorators.csrf import csrf_exempt
from omnisight_v2.operations import list_unique_customers



@csrf_exempt
def customerOrderList(request):

    page = request.GET.get("page", 1)
    search = request.GET.get("search")
    marketplace = request.GET.get("marketplace")
    sortKey = request.GET.get("sortKey", "total_purchase_amount")
    sortOrder = request.GET.get("sortOrder", -1)

    response = list_unique_customers(
        page=int(page),
        search=search,
        filters={"marketplace": marketplace},
        sort_by=sortKey,
        sort_order=int(sortOrder),
    )
    return response
