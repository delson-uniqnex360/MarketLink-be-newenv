from mongoengine import (
    Document,
    EmbeddedDocument,
    StringField,
    FloatField,
    DateTimeField,
    EmbeddedDocumentField,
    ListField,
    IntField,
    DictField,
)


class BuyerInfo(EmbeddedDocument):
    """
    Buyer information for an order.

    Fields mapping:
    - Amazon:
        - email: BuyerInfo.BuyerEmail
        - name: BuyerInfo.BuyerName
    - Noon:
        - email: customer.email (if exists)
        - name: customer.first_name + " " + customer.last_name
    """

    email = StringField()
    name = StringField()


class OrderTotal(EmbeddedDocument):
    """
    Total amount of the order.

    Fields mapping:
    - Amazon:
        - currency_code: OrderTotal.CurrencyCode
        - amount: OrderTotal.Amount
    - Noon:
        - currency_code: optional, default to "AED" (or marketplace default)
        - amount: payment.total.value
    """

    currency_code = StringField()
    amount = FloatField()


class OrderItem(EmbeddedDocument):
    """
    Single item in an order.

    Fields mapping (mainly Noon, since Amazon example has no items):
    - item_id: unique item identifier (Noon: item_id)
    - sku: product SKU
    - name: product name
    - quantity: quantity ordered
    - total_price: total price for this item
    """

    item_id = StringField()
    sku = StringField()
    name = StringField()
    quantity = IntField()
    total_price = FloatField()


class Order(Document):
    """
    Unified order model for multiple marketplaces (Amazon, Noon, Choice).

    Fields:
    - marketplace: "amazon", "noon", or "choice"
    - order_id: Marketplace order ID (Amazon: AmazonOrderId, Noon: order_nr)
    - order_date: Date of order creation/purchase (Amazon: PurchaseDate, Noon: order_date)
    - status: Order status
        - Amazon: OrderStatus ("Processing", "Shipped", etc.)
        - Noon: status ("confirmed", "shipped", etc.)
    - buyer_info: Embedded document containing buyer email and name
    - order_total: Embedded document containing total amount and currency
    - items: List of EmbeddedDocument for order items (Noon has items; Amazon optional)
    - raw_data: Optional raw payload from marketplace for reference/debugging
    """

    meta = {"collection": "orders"}  # Mongo collection name

    marketplace = StringField(
        required=True,
        choices=["amazon", "noon", "choice"],
        help_text="Marketplace source of the order",
    )
    order_id = StringField(
        required=True, help_text="Unique order identifier from the marketplace"
    )
    order_date = DateTimeField(
        help_text="Order creation date (PurchaseDate for Amazon, order_date for Noon)"
    )
    status = StringField(help_text="Order status (Amazon: OrderStatus, Noon: status)")
    buyer_info = EmbeddedDocumentField(BuyerInfo, help_text="Buyer email and name")
    order_total = EmbeddedDocumentField(
        OrderTotal, help_text="Order total with currency"
    )
    items = ListField(EmbeddedDocumentField(OrderItem), help_text="List of order items")
    raw_data = DictField(
        help_text="Raw payload from marketplace (optional, useful for debugging)"
    )
