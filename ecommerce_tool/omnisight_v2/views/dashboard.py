from django.views.decorators.csrf import csrf_exempt
from omnisight_v2.operations import dashboard_kpi_metrics


@csrf_exempt
def dashboardKPIMetrics(request):
    """api returns details for dashboard page"""

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    marketplaces = request.GET.get("marketplaces[]")

    response = dashboard_kpi_metrics(marketplaces, start_date, end_date, )
    return response
