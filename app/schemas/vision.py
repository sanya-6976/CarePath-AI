"""Medical Computer Vision Schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field


class DICOMHeaderMetadata(BaseModel):
    patient_id: Optional[str] = "ANONYMOUS"
    modality: str = "CR"  # e.g., CR, DX, CT, MR
    body_part_examined: Optional[str] = "CHEST"
    study_date: Optional[str] = None
    rows: Optional[int] = None
    columns: Optional[int] = None


class FindingScore(BaseModel):
    pathology: str
    confidence: float
    severity: str = Field(description="NORMAL, MILD, MODERATE, SEVERE")


class VisionAnalysisResult(BaseModel):
    filename: str
    is_dicom: bool
    modality: str
    dicom_metadata: Optional[DICOMHeaderMetadata] = None
    primary_finding: str
    confidence: float
    pathology_scores: List[FindingScore] = Field(default_factory=list)
    gradcam_heatmap_base64: Optional[str] = Field(None, description="Base64 encoded Grad-CAM diagnostic heatmap overlay")
    recommendation: str
    processing_time_seconds: float
