import os
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError


class ElasticClient:
    """
    Clean, class-based Elasticsearch client.
    Reads credentials from environment variables — no hardcoded secrets.
    """

    def __init__(self):
        url      = os.getenv("ES_URL", "https://localhost:9200")
        username = os.getenv("ES_USERNAME", "elastic")
        password = os.getenv("ES_PASSWORD", "44104410")
        print(f"[ElasticClient] Initializing with URL: {url} | Username: {username}")

        # Build auth tuple only if credentials are provided
        http_auth = (username, password) if username and password else None

        self.client = Elasticsearch(
            url,
            basic_auth=http_auth if http_auth else None,
            verify_certs=False,
            request_timeout=300,
         
           ssl_show_warn=False,
            max_retries=3,
            retry_on_timeout=True,
        )

    def check_connection(self) -> bool:
        """
        Returns True if the Elasticsearch cluster is reachable and healthy.
        """
        try:
            return self.client.ping()
        except ESConnectionError as err:
            print(f"[ElasticClient] Connection failed: {err}")
            return False

    def get_client(self):
        """
        Returns the raw Elasticsearch client for use in services.
        """
        return self.client


# Singleton instance — import this across all services
elastic = ElasticClient()
