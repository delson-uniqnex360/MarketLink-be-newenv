from django.views.decorators.csrf import csrf_exempt
from omnisight_v2.operations import product_list

@csrf_exempt
def productListAPI(request):
    
    return {}