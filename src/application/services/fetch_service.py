from typing import Optional, Dict, Any
from src.infrastructure.database.repositories.delivery import DeliveryRepository


class FetchService:
    def __init__(self):
        self.delivery_repo = DeliveryRepository()

    def get_results(self, schema_key: str, source_url: str) -> Optional[Dict[str, Any]]:
        return self.delivery_repo.get_by_schema_and_url(schema_key, source_url)
