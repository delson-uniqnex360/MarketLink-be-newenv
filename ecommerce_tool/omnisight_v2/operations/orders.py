from django.http import JsonResponse

from omnisight.models import Marketplace
from omnisight_v2.helpers import (
    get_amazon_ae_orders,
    get_amazon_catalog,
    get_amazon_inventory_data,
    save_amazon_ae_orders,
    get_noon_ae_orders,
    save_noon_ae_orders,
    get_or_create,
)


def sync_amazon_noon_order_data():
    """
    saves details about both amazon and noon
    """

    # common required data's
    # 1. market place
    # 2. catalog
    # 3. inventory

    # market place
    amazon_marketplace_doc, _ = get_or_create(Marketplace, name="amazon")
    noon_marketplace_doc, _ = get_or_create(Marketplace, name="noon")

    # gets the required data
    amazon_data = get_amazon_ae_orders()
    noon_data = get_noon_ae_orders()

    # get the token
    amazon_access_token = amazon_data.get("access_token")
    noon_access_token = noon_data.get("access_token")

    # saves the required data
    save_amazon_ae_orders(
        amazon_data,
        amazon_marketplace_doc,
        amazon_access_token,
    )

    # save_noon_ae_orders(noon_data, noon_marketplace_doc, noon_access_token)

    return JsonResponse({"message": "Orders synced successfully"})
