from src.infrastructure.database.repositories.ingestion import ExtractionRepository
from src.infrastructure.database.repositories.delivery import DeliveryRepository


def test_repositories():
    ingestion = ExtractionRepository()
    delivery = DeliveryRepository()
    url = "https://example.com"
    input_data = {"phones": ["+7 495 123-45-67"], "emails": ["test@example.com"], "website": "https://example.com"}
    
    ingestion.save_contact_info(url, input_data)
    result = delivery.get_by_schema_and_url("contact", url)
    
    assert result["phones"] == input_data["phones"]
    assert result["emails"] == input_data["emails"]
    assert result["website"] == input_data["website"]
    print("Test passed: save and get work correctly")




if __name__ == "__main__":
    test_repositories()
    print("All tests passed")
