from ecommerce_tool.crud import DatabaseModel
from omnisight.models import Product
from bson import ObjectId
import re
import json
import os
from mongoengine import connect
from datetime import datetime

def connect_to_mongodb():
    try:
        connect(
            db=os.getenv('DATABASE_NAME'),
            host=os.getenv('DATABASE_HOST'),
            port=int(os.getenv('DATABASE_PORT', 27017)),
            alias='default'
        )
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise

def is_valid_asin(asin: str) -> bool:
    if not asin or not isinstance(asin, str):
        return False
    asin = asin.strip().upper()
    return bool(re.match(r'^B[A-Z0-9]{9}$', asin))

def get_product_identifier(product: dict) -> str:
    asin = product.get('asin')
    if asin and is_valid_asin(asin):
        return asin.strip().upper()

    identifiers = [
        product.get('upc'),
        product.get('gtin'),
        product.get('ean'),
        product.get('model_number'),
        product.get('sku'),
        product.get('product_id') 
    ]

    for identifier in identifiers:
        if identifier and str(identifier).strip():
            return str(identifier).strip()

    return ""

def update_product_with_identifier(product_id: str, identifier: str) -> bool:
    try:
        result = DatabaseModel.update_documents(
            Product.objects,
            {"_id": ObjectId(product_id)},
            {"product_id": identifier}
        )
        return True
    except Exception as e:
        print(f"Error updating product {product_id}: {str(e)}")
        return False

def log_products_without_identifiers(products: list) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"products_without_identifiers_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(products, f, indent=2)

    print(f"Saved list of {len(products)} products without identifiers to {filename}")

def find_products_to_update():
    pipeline1 = [
        {
            "$match": {
                "product_id": {"$exists": False},
                "$or": [
                    {"asin": {"$exists": True, "$ne": ""}},
                    {"upc": {"$exists": True, "$ne": ""}},
                    {"gtin": {"$exists": True, "$ne": ""}},
                    {"ean": {"$exists": True, "$ne": ""}},
                    {"model_number": {"$exists": True, "$ne": ""}},
                    {"sku": {"$exists": True, "$ne": ""}}
                ]
            }
        },
        {"$limit": 1000} 
    ]

    pipeline2 = [
        {
            "$match": {
                "product_id": {"$in": ["", None]},
                "$or": [
                    {"asin": {"$exists": True, "$ne": ""}},
                    {"upc": {"$exists": True, "$ne": ""}},
                    {"gtin": {"$exists": True, "$ne": ""}},
                    {"ean": {"$exists": True, "$ne": ""}},
                    {"model_number": {"$exists": True, "$ne": ""}},
                    {"sku": {"$exists": True, "$ne": ""}}
                ]
            }
        },
        {"$limit": 1000}
    ]

    products = []
    for pipeline in [pipeline1, pipeline2]:
        try:
            batch = list(Product.objects.aggregate(*pipeline))
            products.extend(batch)
            print(f"Found {len(batch)} products in this batch")
        except Exception as e:
            print(f"Error executing pipeline: {str(e)}")
            continue

    return products

def update_products_with_missing_ids():
    try:
        connect_to_mongodb()

        products = find_products_to_update()
        print(f"Total products to process: {len(products)}")

        if not products:
            print("No products found that need updating")
            return 0

        updated_count = 0
        no_identifier_count = 0
        products_without_identifiers = []

        for product in products:
            product_id = str(product['_id'])
            identifier = get_product_identifier(product)

            if identifier:
                if update_product_with_identifier(product_id, identifier):
                    updated_count += 1
                    print(f"Updated product {product_id} with product_id: {identifier}")
                else:
                    print(f"Failed to update product {product_id}")
            else:
                no_identifier_count += 1
                products_without_identifiers.append({
                    "product_id": product_id,
                    "product_title": product.get('product_title', ''),
                    "available_identifiers": {
                        "asin": product.get('asin'),
                        "upc": product.get('upc'),
                        "gtin": product.get('gtin'),
                        "ean": product.get('ean'),
                        "model_number": product.get('model_number'),
                        "sku": product.get('sku')
                    }
                })

        print(f"\nUpdate complete:")
        print(f"- Successfully updated {updated_count} products with identifiers")
        print(f"- Found {no_identifier_count} products with no valid identifiers")

        if products_without_identifiers:
            log_products_without_identifiers(products_without_identifiers)

        return updated_count

    except Exception as e:
        print(f"Process failed: {str(e)}")
        return 0

if __name__ == '__main__':
    print("Starting product ID update process")
    start_time = datetime.now()
    try:
        updated_count = update_products_with_missing_ids()
        print(f"Process completed successfully. Updated {updated_count} products.")
    except Exception as e:
        print(f"Process failed: {str(e)}")
    finally:
        duration = datetime.now() - start_time
        print(f"Process took {duration.total_seconds():.2f} seconds")