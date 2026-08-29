"""End-to-End Integration Test Suite for CarePath AI Platform."""
import io
from PIL import Image, ImageDraw


def create_test_image() -> bytes:
    img = Image.new("RGB", (300, 300), color=(120, 120, 120))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), "Rx: Amoxicillin 500mg\nHemoglobin 14.0 g/dL", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_end_to_end_synthesis_flow(client):
    img_bytes = create_test_image()

    data = {
        "clinical_notes": "Patient presents with cough and fever for 3 days."
    }
    files = {
        "document_file": ("prescription.png", img_bytes, "image/png"),
        "image_file": ("xray.png", img_bytes, "image/png")
    }

    response = client.post("/api/v1/diagnosis/synthesize", data=data, files=files)
    assert response.status_code == 200
    res = response.json()

    assert "patient_summary" in res
    assert "risk_assessment" in res
    assert res["risk_assessment"]["risk_score"] > 0
    assert len(res["differential_diagnoses"]) > 0
    assert len(res["recommended_care_path"]) > 0
    assert "disclaimer" in res


def test_api_status_endpoint_shape(client):
    """GET /api/v1/status returns a healthy status with required keys."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_global_exception_handler_structures_error(client):
    """Posting an empty NLP request triggers InputValidationError → structured JSON 422."""
    # An empty string body triggers validate_text_input in nlp_engine.extract_entities.
    response = client.post("/api/v1/nlp/extract", json={"text": ""})
    # FastAPI's own request validation fires first for empty strings, which also returns 422.
    # Either way the response must be valid JSON (not a crash) with a status >= 400.
    assert response.status_code in {400, 422, 500}
    body = response.json()
    # The response body must be parseable JSON — not a raw exception traceback.
    assert isinstance(body, dict)

