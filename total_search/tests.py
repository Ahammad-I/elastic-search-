import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "total_search.settings")
django.setup()

from products.infrastructure.elastic_client import elastic

if elastic.check_connection():
    print("✅ Phase 1 SUCCESS — Elasticsearch is connected!")
else:
    print("❌ Phase 1 FAILED — Check your .env file and make sure ES is running.")
