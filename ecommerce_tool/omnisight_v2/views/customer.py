from omnisight_v2.operations import list_unique_customers
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def customerOrderList(request):

    page = request.GET.get("page", 1)
    search = request.GET.get("search")
    marketplace = request.GET.get("marketplace")

    response = list_unique_customers(
        page=int(page), search=search, filters={"marketplace": marketplace}
    )
    return response


# response = list_unique_customers(
#     page=1,
#     page_size=20,
#     search="john",
#     filters={
#         "marketplace_id": "65f1b2c4d5e6f7a8b9c01234",
#         "date_from": datetime(2025, 8, 1),
#         "date_to": datetime(2025, 8, 31),
#     },
#     sort_by="total_orders",
#     sort_order=-1,
# )
