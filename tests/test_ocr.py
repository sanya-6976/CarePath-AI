"""Tests for OCR processing pipeline and API endpoints."""
import io
from PIL import Image, ImageDraw, ImageFont


def create_sample_prescription_image() -> bytes:
    """Generate a synthetic prescription image for testing OCR."""
    img = Image.new("RGB", (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    text = "PRESCRIPTION\nRx: Amoxicillin 500mg twice daily\nHemoglobin 14.5 g/dL (Ref: 12.0-16.0) NORMAL"
    draw.text((20, 20), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_ocr_extract_endpoint(client):
    img_bytes = create_sample_prescription_image()
    files = {"file": ("prescription.png", img_bytes, "image/png")}
    response = client.post("/api/v1/ocr/extract", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "prescription.png"
    assert "document_type" in data
    assert "confidence_score" in data
    assert data["confidence_score"] > 0
