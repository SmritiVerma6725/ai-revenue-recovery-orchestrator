from backend.services.razorpay_service import RazorpayService


def test_razorpay_service_client_configuration_without_keys() -> None:
    service = RazorpayService()
    assert service.client is None
    assert service.retry_payment("TX-1")["status"] == "scheduled"
    assert service.send_payment_link("TX-1", 15000)["status"] == "sent"


def test_razorpay_service_fallback_payload() -> None:
    service = RazorpayService()
    result = service.send_payment_link("TX-42", 2500)
    assert result["transaction_id"] == "TX-42"
    assert result["action"] == "payment_link"
    assert "₹" in result["message"]
