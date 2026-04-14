from django.core.management.base import BaseCommand
from products.infrastructure.elastic_client import elastic
class Command(BaseCommand):
    help="Create Elasticsearch index for products"
    def handle(self,*args,**kwargs):
        if not elastic.check_connection():
           print("connected failed in while indexing")
           return 
        index_name = "products"         
        if elastic.client.indices.exists(index=index_name):
           print(f"index{index_name} already exists") 
           return 
        
        mappings = {
            "mappings": {
                "properties": {
                    "variant_handle":  {"type": "keyword"},
                    "name":            {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "description":     {"type": "text"},
                    "brand":           {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "category":        {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "price":           {"type": "float"},
                    "color":           {"type": "keyword"},
                    "material":        {"type": "keyword"},
                    "is_active":       {"type": "boolean"},
                    "image_url":       {"type": "keyword", "index": False},
                 
                }
            }
        }

        elastic.client.indices.create(index=index_name, body=mappings)
        self.stdout.write(self.style.SUCCESS(
            f"Index '{index_name}' created successfully."
        ))   

