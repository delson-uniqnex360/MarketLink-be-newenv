from __future__ import annotations
from email.policy import default
from math import inf

from click import DateTime
from mongoengine import Document, StringField,DynamicField, FloatField,ObjectIdField, IntField, BooleanField, DictField, ListField, EmbeddedDocument, EmbeddedDocumentField,ReferenceField, DateTimeField
from mongoengine.errors import ValidationError
import re
import random
from datetime import datetime, timedelta
from bson import ObjectId
from ecommerce_tool.crud import DatabaseModel

class Marketplace(Document):
    name = StringField()  
    url = StringField()  
    image_url = StringField()  
    created_at = StringField()  
    updated_at = StringField()  
    country = ListField(StringField())

class Category(Document):
    name = StringField(required=True)  
    parent_category_id = ReferenceField('self', null=True)  
    marketplace_id = ReferenceField(Marketplace)  
    breadcrumb_path = ListField(StringField())  
    level = IntField()  
    created_at = StringField()  
    updated_at = StringField()  
    end_level = BooleanField(default=False)  

class Brand(Document):
    name = StringField()  
    description = StringField()  
    website = StringField()  
    marketplace_id = ReferenceField(Marketplace)  
    marketplace_ids = ListField(ReferenceField(Marketplace),default=[])  

class Manufacturer(Document):
    name = StringField()  
    description = StringField()  
    website = StringField()  
    marketplace_id = ReferenceField(Marketplace)  
    
class Product(Document):
    
    product_title = StringField()
    wpid = StringField()  
    net_profit=IntField(default=0)
    product_description = StringField()
    product_id = DynamicField()  
    product_id_type = StringField()
    price = FloatField(default=0.0)
    currency = StringField(default="$")
    quantity = IntField(default=0)
    quantity_unit = StringField()
    item_condition = StringField()
    item_note = StringField()  
    
    sku = StringField()
    master_sku = DynamicField()  
    parent_sku = StringField()  
    
    listing_id = StringField()  
    upc = StringField()  
    gtin = StringField()  
    asin = StringField()  
    model_number = StringField()
    
    image_url = StringField() 
    image_urls = ListField(StringField())  
    zshop_category = StringField()
    zshop_browse_path = StringField()
    
    delivery_partner = StringField()
    merchant_shipping_group = StringField()
    will_ship_internationally = BooleanField(default=False)
    expedited_shipping = BooleanField(default=False)
    zshop_shipping_fee = StringField()
    
    open_date = DateTimeField()
    availability = StringField()
    lifecycle_status = StringField()  
    published_status = StringField()
    unpublished_reasons = StringField()  
    
    variant_group_id = StringField()
    variant_group_info = DictField()
    
    zshop_storefront_feature = BooleanField(default=False)
    zshop_boldface = BooleanField(default=False)
    bid_for_featured_placement = BooleanField(default=False)
    
    add_delete = StringField()
    pending_quantity = IntField(default=0)
    is_duplicate = BooleanField(default=False)
    shelf_path = StringField()  
    product_type = StringField()  
    category = StringField()  
    attributes = DictField()  
    old_attributes = DictField()
    features = ListField(StringField())  
    brand_name = StringField()  
    brand_id = ReferenceField(Brand)  
    manufacturer_name = StringField()  
    manufacturer_id = ReferenceField(Manufacturer)  
    marketplace_id = ReferenceField(Marketplace)  
    created_at = DateTimeField(default=datetime.now())  
    updated_at = DateTimeField(default=datetime.now())  
    cogs = FloatField(default=0.0)  
    shipping_cost = FloatField(default=0.0)  
    page_views = IntField(default=0) 
    refund = IntField(default=0) 
    sessions = IntField(default=0) 
    listing_quality_score = FloatField(default=0.0)  
    product_url = StringField()  
    videos = ListField(StringField())  
    new_product = BooleanField(default=False)  
    
    fullfillment_by_channel = BooleanField(default=False)  
    channel_fee = FloatField(default=0.0)  
    fullfillment_by_channel_fee = FloatField(default=0.0)  
    vendor_funding = FloatField(default=0.0)  
    vendor_discount = FloatField(default=0.0)  
    marketplace_ids = ListField(ReferenceField(Marketplace),default=[])  
    product_cost = FloatField(default=0.0)  
    referral_fee = FloatField(default=0.0)  
    a_shipping_cost = FloatField(default=0.0)  
    total_cogs = FloatField(default=0.0)  
    product_created_date = DateTimeField(default=datetime.now())  
    producted_last_updated_date = DateTimeField(default=datetime.now())  
    w_product_cost = FloatField(default=0.0)
    walmart_fee = FloatField(default=0.0)  
    w_shiping_cost = FloatField(default=0.0)  
    w_total_cogs = FloatField(default=0.0)  
    pack_size = IntField(default=0)  
    meta = {
        'indexes': [
            'marketplace_id',
            'brand_id',
            'manufacturer_name',
            'sku',
            'asin',
            ['marketplace_id', 'brand_id'],
            ['marketplace_id', 'manufacturer_name']
        ]
    }
  
class CachedMetrics(Document):
    cache_hash = StringField(required=True, unique=True)
    marketplace_id = ReferenceField(Marketplace, null=True) 
    brand_ids = ListField(ReferenceField(Brand), default=[]) 
    product_ids = ListField(ReferenceField(Product), default=[])
    manufacturer_names = ListField(StringField(), default=[])
    fulfillment_channel = StringField(default=None) 
    from_date = DateTimeField(required=True)
    to_date = DateTimeField(required=True)
    gross_revenue = FloatField(default=0.0)
    net_profit = FloatField(default=0.0)
    total_orders = IntField(default=0)
    total_units = IntField(default=0)
    total_tax = FloatField(default=0.0)
    refund = IntField(default=0)
    margin = FloatField(default=0.0)
    total_cogs = FloatField(default=0.0)
    sku_count = IntField(default=0)
    sessions = IntField(default=0)
    page_views = IntField(default=0)
    unit_session_percentage = FloatField(default=0.0)
    roi = FloatField(default=0.0)
    last_updated = DateTimeField(default=datetime.utcnow)
    extra_data = DictField() 
    meta = {'indexes': [
        {'fields': ['cache_hash'], 'unique': True},
        {'fields': ['marketplace_id', 'from_date', 'to_date']},
        {'fields': ['brand_ids']}, 
        {'fields': ['last_updated'], 'expireAfterSeconds': 3600 * 24 * 7}
    ]}

class ignore_api_functions(Document):
    name = StringField()

class mail_template(Document):
    code = StringField()
    subject = StringField()
    default_template = StringField()
    cutomize_template = StringField()

class role(Document):
    name = StringField()
    description = StringField()
    priority = IntField()

class user(Document):
    first_name = StringField()
    last_name = StringField()
    username = StringField()
    email = StringField(required=True)
    password = StringField()
    age = IntField()
    date_of_birth = StringField()
    mobile_number = StringField()
    active = BooleanField(default=True)
    profile_image = StringField()
    role_id = ReferenceField(role)
    otp = IntField()
    is_verified = BooleanField(default=False)
    otp_generated_time = DateTimeField(default=datetime.now())
    last_login = DateTimeField(default=datetime.now())
    creation_date = DateTimeField(default=datetime.now())
    credentilas = ListField(DictField())
    updated_at = DateTimeField(default=datetime.utcnow)

class access_token(Document):
    user_id = ReferenceField(user)
    access_token_str = StringField()
    creation_time = DateTimeField(default=datetime.now())
    updation_time = DateTimeField(default=datetime.now())
    marketplace_id = ReferenceField(Marketplace)

class Money(EmbeddedDocument):
    CurrencyCode = StringField(required=True)
    Amount = FloatField(required=True,default=0.0)

class Pricing(EmbeddedDocument):
    ItemPrice = EmbeddedDocumentField(Money, required=True)
    ItemTax = EmbeddedDocumentField(Money, default=None)
    PromotionDiscount = EmbeddedDocumentField(Money, default=None)
    ShipPromotionDiscount=EmbeddedDocumentField(Money,default=None)

class ProductDetails(EmbeddedDocument):
    product_id = ReferenceField(Product)
    Title = StringField(required=True)
    SKU = StringField(required=True)
    ASIN = StringField(default=None)
    Condition = StringField(default=None)
    QuantityOrdered = IntField(required=True)
    QuantityShipped = IntField(required=True)

class Fulfillment(EmbeddedDocument):
    FulfillmentOption = StringField(default=None)
    ShipMethod = StringField(default=None)
    Carrier = StringField(default=None)
    TrackingNumber = StringField(default=None)
    TrackingURL = StringField(default=None)
    ShipDateTime = DateTimeField(default=None)

class OrderStatus(EmbeddedDocument):
    STATUS_CHOICES = ("Pending", "Shipped", "Delivered", "Canceled", "Returned")
    Status = StringField(required=True)
    StatusDate = DateTimeField(required=True)
    
class TaxCollection(EmbeddedDocument):
    Model = StringField(required=True)
    ResponsibleParty = StringField(required=True)

class BuyerInfo(EmbeddedDocument):
    Name = StringField(default=None)
    Email = StringField(default=None)
    Address = DictField(default=None)

class OrderItems(Document):
    OrderId = StringField()
    Platform = StringField()
    ProductDetails = EmbeddedDocumentField(ProductDetails, )
    Pricing = EmbeddedDocumentField(Pricing, )
    Fulfillment = EmbeddedDocumentField(Fulfillment, default=None)
    OrderStatus = EmbeddedDocumentField(OrderStatus, default=None)
    TaxCollection = EmbeddedDocumentField(TaxCollection, )
    IsGift = BooleanField()
    BuyerInfo = EmbeddedDocumentField(BuyerInfo, default=None)
    created_date = DateTimeField(default=datetime.now())
    document_created_date = DateTimeField()
    PromotionDiscount = FloatField(required=False)
    net_profit = FloatField(default=0.0)
    tax_checked=BooleanField(default=False)
    pricing_checked=BooleanField(default=False)
    updated_at = DateTimeField(default=datetime.utcnow)
    meta = {
        'indexes': [
            'ProductDetails.product_id',
            'created_date',
            ['created_date', 'ProductDetails.product_id']
        ]
    }
    
class Order(Document):
    
    purchase_order_id = StringField()  
    customer_order_id = StringField()  
    seller_order_id = StringField()  
    merchant_order_id = StringField()  
    geo = StringField()  
    channel = StringField() 
    shipstation_id=StringField()
    shipstation_synced=BooleanField(default=False)
    shipstation_sync_date=DateTimeField()
    shipping_rates_fetched=BooleanField(default=False)
    shipping_rates_date=DateTimeField()
    shipping_cost=FloatField(default=0.0)
    tracking_number=StringField()
    merchant_shipment_cost=FloatField()
    
    customer_email_id = StringField()  
    
    order_date = DateTimeField()  
    pacific_date = DateTimeField()  
    earliest_ship_date = DateTimeField()  
    latest_ship_date = DateTimeField()  
    last_update_date = DateTimeField()  
    
    shipping_information = DictField()  
    ship_service_level = StringField()  
    shipment_service_level_category = StringField()  
    automated_shipping_settings = DictField()  
    
    order_details = ListField(DictField())  
    order_items =  ListField(ReferenceField(OrderItems))  
    order_status = StringField()  
    number_of_items_shipped = IntField()  
    number_of_items_unshipped = IntField()  
    updated_at = DateTimeField(default=datetime.utcnow)
    
    fulfillment_channel = StringField()  
    sales_channel = StringField()  
    order_type = StringField()  
    is_premium_order = BooleanField()  
    is_prime = BooleanField()  
    has_regulated_items = BooleanField()  
    is_replacement_order = BooleanField()  
    is_sold_by_ab = BooleanField()  
    is_ispu = BooleanField()  
    is_access_point_order = BooleanField()  
    is_business_order = BooleanField()  
    
    marketplace = StringField()  
    marketplace_id = ReferenceField(Marketplace)  
    payment_method = StringField()  
    payment_method_details = StringField()  
    order_total = FloatField(default=0.0)  
    currency = StringField()  
    is_global_express_enabled = BooleanField()  
    customer_name = StringField()
    order_channel = StringField()  
    items_order_quantity = IntField(default=0)  
    shipping_price = FloatField(default=0.0)  
    meta = {
        'indexes': [
            'marketplace_id',
            'order_date',
            'fulfillment_channel',
            ['order_date', 'marketplace_id'],
            ['order_date', 'fulfillment_channel'],
            ['marketplace_id', 'order_date', 'fulfillment_channel'],
            'purchase_order_id',    
            'order_items'  
        ]
    }
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(Order, self).save(*args, **kwargs)
    
class ShippingRate(Document):
    order=ReferenceField(Order)
    carrier=StringField()
    service=StringField()
    rate=FloatField()
    delivery_days=IntField()
    rate_data=DictField()
    created_at=DateTimeField(default=datetime.now)
    shipment_type = StringField(choices=['combined', 'split'])  
    item_sku = StringField() 

class product_details(EmbeddedDocument):
    product_id = ReferenceField(Product)
    title = StringField(required=True)
    sku = StringField(required=True)
    unit_price = FloatField(default=0.0)
    quantity = IntField()
    quantity_price = FloatField(default=0.0)

class custom_order(Document):
    
    order_id = StringField()  
    customer_order_id = StringField()  
    ordered_products = ListField(EmbeddedDocumentField(product_details))  
    total_quantity = IntField()
    total_price = FloatField(default=0.0)
    currency = StringField()
    shipment_type = StringField()  
    channel = StringField()  
    order_status = StringField(default="Pending")
    
    multiple_shipments = BooleanField(default=False)  
    shipments = ListField(DictField())  
    shipment_type = StringField(choices=['combined', 'split'])  
    shipping_options = DictField()  
    recommended_shipping = StringField(choices=['combined', 'split'])     
    
    payment_status = StringField(default="Pending")  
    payment_mode = StringField()  
    invoice = StringField()  
    transaction_id = StringField()
    tax = FloatField(default=0.0)
    tax_amount = FloatField(default=0.0)
    discount = FloatField(default=0.0)
    discount_amount = FloatField(default=0.0)
    
    shipping_address = StringField()
    customer_name = StringField()
    supplier_name = StringField()
    mail = StringField()
    contact_number = StringField()
    customer_note = StringField()  
    tags= StringField()
    
    package_dimensions = StringField()  
    weight = FloatField(default=0.0)  
    weight_value = StringField()
    shipment_cost = FloatField(default=0.0)  
    shipment_speed = StringField()  
    shipment_mode = StringField()  
    carrier = StringField()  
    tracking_number = StringField()  
    shipping_label = StringField()  
    shipping_label_preview = StringField()  
    shipping_label_print = StringField()  
    
    channel_name = StringField()  
    channel_order_id = StringField()  
    fulfillment_type = StringField()  
    purchase_order_date = DateTimeField(default=datetime.now())
    expected_delivery_date = DateTimeField(default=datetime.now())
    
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(default=datetime.now())
    user_id = ReferenceField(user)



















            



            



            


            




class CacheConfiguration(Document):
    endpoint_name=StringField(required=True,unique=True,max_length=100)
    ttl_minutes=IntField(default=30)
    max_entries=IntField(default=1000)
    user_specific=BooleanField(default=False)
    date_sensitive=BooleanField(default=True)
    exclude_params=ListField(StringField(max_length=50),default=[])
    sensitive_params=ListField(StringField(max_length=50),default=[])
    created_at=DateTimeField(default=datetime.utcnow)
    updated_at=DateTimeField(default=datetime.utcnow)
    is_active=BooleanField(detault=True)
    meta={
        "collection":'cache_configuration',
        'indexes':[
            {'fields':['endpoint_name'],"unique":True},
            {'fields':['is_active']}
        ]
    }

class SyncStatus(Document):
    task_name=StringField(required=True,unique=True,max_length=50)
    status=StringField(choices=['running','completed','failed','pending'],default='pending')
    last_run=DateTimeField(default=datetime.utcnow)
    last_success=DateTimeField()
    run_count=IntField(default=0)
    success_count=IntField(default=0)
    failure_count=IntField(default=0)
    error_message=StringField(max_length=1000)
    affected_endpoints=ListField(StringField(max_length=100))
    meta={
        'collection':"sync_status",
        "indexes":[
            {"fields":['task_name'],"unique":True},
            {'fields':['status']},
            {'fields':['last_success']}
        ]   
    }
class authenticated_api(Document):
    name = StringField()
    allowed_roles = ListField(ReferenceField(role))
    created_at = DateTimeField()
class CityDetails(Document):
    city = StringField(max_length=100)
    city_ascii = StringField(max_length=100)
    state_id = StringField(max_length=10)
    state_name = StringField(max_length=100)
    county_fips = StringField(max_length=20)
    county_name = StringField(max_length=100)
    lat = FloatField(default=0.0)
    lng = FloatField(default=0.0)
    population = IntField()
    density = FloatField(default=0.0)
    source = StringField(max_length=100)
    military = BooleanField()
    incorporated = BooleanField()
    timezone = StringField(max_length=100)
    ranking = IntField()
    zips = StringField()  
    uid = IntField(unique=True)
class chooseMatrix(Document):
    name = StringField(max_length=100)
    select_all =  BooleanField()
    gross_revenue =  BooleanField()
    units_sold =  BooleanField()
    acos =  BooleanField()
    tacos =  BooleanField()
    refund_quantity =  BooleanField()
    net_profit =  BooleanField()
    profit_margin =  BooleanField()
    refund_amount =  BooleanField()
    roas =  BooleanField()
    orders =  BooleanField()
    ppc_spend =  BooleanField()
    total_cogs = BooleanField()
    business_value = BooleanField()
class notes_data(Document):
    product_id = ReferenceField(Product)
    date_f = DateTimeField(default=datetime.now())
    notes = StringField()
    user_id = ReferenceField(user)
class Fee(Document):
    marketplace = StringField()
    fee_type = StringField()
    amount = FloatField(default=0.0)
    date =  DateTimeField(default=datetime.now())
class Refund(Document):
    product_id = ReferenceField(Product)
    date =  DateTimeField(default=datetime.now())
    reason  = StringField()
class pageview_session_count(Document):
    product_id = ListField(ReferenceField(Product), default=[])
    date = DateTimeField(default=datetime.now())
    page_views = IntField(default=0)
    session_count = IntField(default=0)
    
    asin = StringField()
    
    units_ordered = IntField(default=0)
    units_ordered_b2b = IntField(default=0)
    ordered_product_sales_amount = FloatField(default=0.0)
    ordered_product_sales_currency_code = StringField(default="USD")
    ordered_product_sales_b2b_amount = FloatField(default=0.0)
    ordered_product_sales_b2b_currency_code = StringField(default="USD")
    total_order_items = IntField(default=0)
    total_order_items_b2b = IntField(default=0)
    
    browser_sessions = IntField(default=0)
    browser_sessions_b2b = IntField(default=0)
    mobile_app_sessions = IntField(default=0)
    mobile_app_sessions_b2b = IntField(default=0)
    sessions = IntField(default=0)
    sessions_b2b = IntField(default=0)
    browser_session_percentage = FloatField(default=0.0)
    browser_session_percentage_b2b = FloatField(default=0.0)
    mobile_app_session_percentage = FloatField(default=0.0)
    mobile_app_session_percentage_b2b = FloatField(default=0.0)
    session_percentage = FloatField(default=0.0)
    session_percentage_b2b = FloatField(default=0.0)
    browser_page_views = IntField(default=0)
    browser_page_views_b2b = IntField(default=0)
    mobile_app_page_views = IntField(default=0)
    mobile_app_page_views_b2b = IntField(default=0)
    page_views_b2b = IntField(default=0)
    browser_page_views_percentage = FloatField(default=0.0)
    browser_page_views_percentage_b2b = FloatField(default=0.0)
    mobile_app_page_views_percentage = FloatField(default=0.0)
    mobile_app_page_views_percentage_b2b = FloatField(default=0.0)
    page_views_percentage = FloatField(default=0.0)
    page_views_percentage_b2b = FloatField(default=0.0)
    buy_box_percentage = FloatField(default=0.0)
    buy_box_percentage_b2b = FloatField(default=0.0)
    unit_session_percentage = FloatField(default=0.0)
    unit_session_percentage_b2b = FloatField(default=0.0)
    meta = {
        'indexes': [
            'product_id',
            'date',
            ['date', 'product_id'],
            ['product_id', 'date']  
        ]
    }
class inventry_log(Document):
    date = DateTimeField(default=datetime.now())
    product_id = ReferenceField(Product)
    available = IntField(default=0)
    reserved = IntField(default=0)
    updated_at = DateTimeField(default=datetime.now())
class productPriceChange(Document):
    product_id = ReferenceField(Product)
    old_price = FloatField(default=0.0)
    new_price = FloatField(default=0.0)
    change_date = DateTimeField(default=datetime.now())
    reason = StringField(default="Price update")
