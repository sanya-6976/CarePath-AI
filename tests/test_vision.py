"""Tests for Medical Computer Vision API and DICOM engine."""
import io
from PIL import Image


def create_sample_chest_xray_image() -> bytes:
    """Generate a synthetic chest image byte payload."""
    img = Image.new("RGB", (256, 256), color=(100, 100, 100))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_vision_analyze_endpoint(client):
    img_bytes = create_sample_chest_xray_image()
    files = {"file": ("chest_xray.png", img_bytes, "image/png")}
    response = client.post("/api/v1/vision/analyze", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "chest_xray.png"
    assert "primary_finding" in data
    assert "confidence" in data
    assert "gradcam_heatmap_base64" in data
    assert len(data["gradcam_heatmap_base64"]) > 0
