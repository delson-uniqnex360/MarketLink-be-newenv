from omnisight_v2.operations import sync_amazon_noon_order_data


def syncOrders(request):

    sync_amazon_noon_order_data()
    return {"message": "success"}
