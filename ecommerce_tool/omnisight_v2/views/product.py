from django.views.decorators.csrf import csrf_exempt
from omnisight_v2.operations import product_list, product_detail


@csrf_exempt
def productListAPI(request):

    page = request.GET.get("page", 1)
    search = request.GET.get("search")
    sortKey = request.GET.get("sortKey", "order_date")
    sortOrder = request.GET.get("sortOrder", 1)

    response = product_list(
        page=int(page),
        search=search,
        sort_by=sortKey,
        sort_order=int(sortOrder),
    )

    return response


@csrf_exempt
def productDetail(request, product_id: str):

    response = product_detail(product_id)
    return response
