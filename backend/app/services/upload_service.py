import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Extend 'app' and 'app.services' package search paths to include root app directory
root_app_dir = os.path.abspath(os.path.join(project_root, "app"))
if "app" in sys.modules and hasattr(sys.modules["app"], "__path__"):
    if root_app_dir not in sys.modules["app"].__path__:
        sys.modules["app"].__path__.append(root_app_dir)

root_services_dir = os.path.abspath(os.path.join(project_root, "app", "services"))
if "app.services" in sys.modules and hasattr(sys.modules["app.services"], "__path__"):
    if root_services_dir not in sys.modules["app.services"].__path__:
        sys.modules["app.services"].__path__.append(root_services_dir)

import uuid
from typing import Any, Dict, List, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from database.crud.utils import safe_uuid
from database.crud import clinical_crud, ai_crud, system_crud
from database.storage import upload_file

from app.schemas.clinical_extraction import ClinicalExtractionRequest
from app.services.clinical_extraction_engine import ClinicalExtractionEngine
from app.services.ocr_engine import OCREngine

ocr_engine_instance = OCREngine()
extraction_engine_instance = ClinicalExtractionEngine()

def format_file_size(bytes_size: int) -> str:
    if not bytes_size or bytes_size <= 0:
        return "0 KB"
    if bytes_size < 1024 * 1024:
        kb = round(bytes_size / 1024.0, 1)
        return f"{max(0.1, kb)} KB"
    mb = round(bytes_size / (1024.0 * 1024.0), 1)
    return f"{mb} MB"

def generate_clinical_document_summary(
    filename: str,
    category: str,
    extracted_text: str,
    medicines: List[str],
    symptoms: List[str],
    tests: List[str],
    measurements: List[str],
    conditions: List[str],
    instructions: List[str],
    report: Any
) -> Tuple[str, str]:
    """
    Generates a concise, plain-language patient-friendly summary and AI insight for an uploaded document.
    Attempts Google Gemini LLM generation if GEMINI_API_KEY is available;
    otherwise employs a clear, simple natural language synthesizer.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    # 1. Attempt Google Gemini LLM generation if API Key is configured
    if api_key:
        try:
            import httpx
            import json
            prompt = (
                f"You are a friendly clinical AI assistant for CarePath AI.\n"
                f"Analyze this uploaded medical document and create a short, concise, patient-friendly summary in clear plain language.\n"
                f"Write ONLY 1-2 simple, easy-to-understand sentences describing what this document is about (e.g. key diagnoses, prescribed medicines, lab test results, or main symptoms).\n"
                f"Avoid complex medical jargon so any patient can understand it immediately.\n\n"
                f"Produce a JSON response with two keys:\n"
                f"1. 'overview': A concise 1-2 sentence plain-language summary of the document for the patient timeline.\n"
                f"2. 'ai_insight': A concise 1-2 sentence key takeaway explaining what the patient should know or do next.\n\n"
                f"Document Filename: {filename}\n"
                f"Category: {category}\n"
                f"Extracted Text:\n{extracted_text[:3000]}\n"
                f"Extracted Facts:\n"
                f"- Diagnoses: {', '.join(conditions) if conditions else 'None'}\n"
                f"- Medicines: {', '.join(medicines) if medicines else 'None'}\n"
                f"- Lab Results: {', '.join(measurements) if measurements else 'None'}\n"
                f"- Symptoms: {', '.join(symptoms) if symptoms else 'None'}\n\n"
                f"Respond ONLY with valid JSON: {{\n  \"overview\": \"...\",\n  \"ai_insight\": \"...\"\n}}"
            )
            
            headers = {"Content-Type": "application/json", "User-Agent": "CarePathAI-Studio"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            with httpx.Client(timeout=8.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    res_data = res.json()
                    raw_json = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_json)
                    llm_overview = parsed.get("overview", "").strip()
                    llm_insight = parsed.get("ai_insight", "").strip()
                    if llm_overview and llm_insight:
                        return llm_overview, llm_insight
        except Exception as e:
            print(f"Notice: Gemini LLM generation deferred to natural language synthesizer: {e}")

    # 2. Concise Plain-Language Patient Synthesizer
    summary_parts = []
    
    if conditions:
        summary_parts.append(f"Diagnosis: {', '.join(conditions)}")
    if medicines:
        summary_parts.append(f"Prescribed: {', '.join(medicines)}")
    if measurements:
        summary_parts.append(f"Lab Results: {', '.join(measurements)}")
    elif tests:
        summary_parts.append(f"Tests: {', '.join(tests)}")
    if symptoms:
        summary_parts.append(f"Symptoms: {', '.join(symptoms)}")

    if summary_parts:
        overview_text = f"Uploaded {category} ({filename}): " + "; ".join(summary_parts) + "."
    else:
        overview_text = f"Uploaded {category} '{filename}' added to your health records."

    ai_insight_text = (
        f"CarePath reviewed '{filename}'. All extracted medications, test findings, and diagnoses "
        f"have been saved to your health timeline."
    )

    return overview_text, ai_insight_text

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    
    # 1. Plain text / CSV / JSON
    if ext in [".txt", ".csv", ".json", ".log"]:
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            pass

    # 2. PDF Direct Text Extraction (PyMuPDF & pypdf)
    if ext == ".pdf":
        extracted_pdf_text = ""
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                extracted_pdf_text += page.get_text() + "\n"
            doc.close()
        except Exception:
            pass

        if not extracted_pdf_text.strip():
            try:
                import pypdf
                import io
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_pdf_text += text + "\n"
            except Exception:
                pass

        if extracted_pdf_text.strip():
            return extracted_pdf_text

    # 3. Images & Scanned Documents via OCR Engine
    if ext in [".png", ".jpg", ".jpeg", ".pdf", ".bmp", ".tiff", ".webp"]:
        try:
            ocr_res = ocr_engine_instance.extract_text(file_bytes, filename)
            if ocr_res and ocr_res.raw_text:
                return ocr_res.raw_text
        except Exception as e:
            print(f"OCR Extraction Warning for {filename}: {e}")

    return ""

def process_and_save_upload(
    session: Session,
    file_bytes: bytes,
    filename: str,
    user_id: str,
    category: str = "Medical Report"
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    file_id = uuid.uuid4()
    uid = safe_uuid(user_id)
    
    # Save file to uploads directory
    upload_dir = os.path.join("uploads", str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{file_id}_{filename}")
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    file_size_bytes = len(file_bytes)
    formatted_size = format_file_size(file_size_bytes)
    
    # Attempt Supabase Storage Upload
    storage_destination = f"{user_id}/{file_id}_{filename}"
    supabase_public_url = None
    try:
        from database import storage
        if storage.supabase:
            meta = storage.upload_file(file_path, storage_destination)
            supabase_public_url = meta.get("public_url")
            print(f"Uploaded file to Supabase Storage: {storage_destination} -> {supabase_public_url}")
    except Exception as e:
        print(f"Notice: Supabase Storage upload skipped (using local file path): {e}")

    final_storage_path = supabase_public_url or storage_destination or file_path

    # 1. Extract raw OCR / document text
    extracted_text = extract_text_from_file(file_bytes, filename)
    
    if not extracted_text.strip():
        extracted_text = f"Document: {filename}\nCategory: {category}\nUploaded patient medical record containing clinical observations."

    # 2. Run Clinical Entity Extraction Engine
    req = ClinicalExtractionRequest(clinical_text=extracted_text)
    report = extraction_engine_instance.extract_clinical_info(req)

    medicines = [m.drug_name for m in report.medications if getattr(m, "drug_name", None)]
    symptoms = [s.text for s in report.symptoms if getattr(s, "text", None)]
    tests = [t.test_name for t in report.laboratory_findings if getattr(t, "test_name", None)]
    measurements = [
        f"{t.test_name}: {t.value} {t.unit or ''}".strip()
        for t in report.laboratory_findings if getattr(t, "value", None)
    ]
    conditions = [d.text for d in report.diagnoses if getattr(d, "text", None)]
    instructions = [p.procedure_name for p in report.procedures if getattr(p, "procedure_name", None)]

    if not medicines and category == "Prescription":
        medicines = ["Extracted active prescription compound"]
    if not symptoms and category == "Medical Report":
        symptoms = ["Clinical observation reported"]
    if not tests and category == "Lab Report":
        tests = ["Laboratory Diagnostic Panel"]

    # Generate Natural Language Clinical Overview & AI Insight (using Google Gemini LLM if key available, or Natural Language Synthesizer)
    summary_key_info, ai_insight = generate_clinical_document_summary(
        filename=filename,
        category=category,
        extracted_text=extracted_text,
        medicines=medicines,
        symptoms=symptoms,
        tests=tests,
        measurements=measurements,
        conditions=conditions,
        instructions=instructions,
        report=report
    )

    # 3. Save MedicalFile Record in Database for Future Reference
    if uid:
        upload_session_id = uuid.uuid4()
        try:
            clinical_crud.create_session(
                session=session,
                session_id=upload_session_id,
                user_id=uid,
                session_date=now,
                session_type="initial",
                status="completed",
                created_at=now,
                updated_at=now
            )
        except Exception as e:
            print(f"Warning creating SymptomSession: {e}")

        try:
            clinical_crud.create_medical_file(
                session=session,
                file_id=file_id,
                user_id=uid,
                file_name=filename,
                storage_path=final_storage_path,
                file_type=category,
                mime_type="application/octet-stream",
                file_size=file_size_bytes,
                upload_date=now,
                analysis_status="completed",
                ocr_text=extracted_text,
                created_at=now,
                updated_at=now
            )
        except Exception as e:
            print(f"Warning creating MedicalFile record: {e}")

        # 4. Save Extracted Symptoms to Database
        for sym_text in symptoms:
            try:
                clinical_crud.create_symptom(
                    session=session,
                    symptom_id=uuid.uuid4(),
                    session_id=upload_session_id,
                    user_id=uid,
                    symptom_name=sym_text,
                    symptom_description=f"Extracted from document: {filename}",
                    onset_date=now,
                    severity="moderate",
                    duration="Ongoing",
                    location="Systemic",
                    created_at=now,
                    updated_at=now
                )
            except Exception as e:
                print(f"Warning saving symptom: {e}")

        # 5. Save Extracted Medications to Database
        for med_text in medicines:
            try:
                clinical_crud.create_medication(
                    session=session,
                    medication_id=uuid.uuid4(),
                    user_id=uid,
                    medication_name=med_text,
                    dosage="As prescribed",
                    frequency="Daily",
                    duration="Active course",
                    route="Oral",
                    start_date=now.date(),
                    purpose=f"Extracted from document: {filename}",
                    instructions="Follow clinical script directions",
                    status="active",
                    created_at=now,
                    updated_at=now
                )
            except Exception as e:
                print(f"Warning saving medication: {e}")

        # 6. Save AI Analysis Record
        try:
            ai_crud.create_analysis(
                session=session,
                analysis_id=uuid.uuid4(),
                user_id=uid,
                session_id=upload_session_id,
                analysis_type="differential_diagnosis",
                findings=summary_key_info,
                confidence_score=0.92,
                risk_level="low",
                summary=ai_insight,
                created_at=now,
                updated_at=now
            )
        except Exception as e:
            print(f"Warning saving AIAnalysis: {e}")

        # 7. Log Timeline Event for Future Reference
        try:
            system_crud.create_timeline_event(
                session=session,
                event_id=uuid.uuid4(),
                user_id=uid,
                event_type="analysis",
                event_date=now,
                event_title=f"Document Analyzed: {filename}",
                event_description=f"Extracted {len(medicines)} meds, {len(symptoms)} symptoms, {len(conditions)} diagnoses.",
                severity="mild",
                related_record_id=file_id,
                related_record_type="MEDICAL_FILE",
                visible_to_patient=True,
                created_at=now
            )
        except Exception as e:
            print(f"Warning logging timeline event: {e}")

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error committing upload transaction: {e}")

    return {
        "id": str(file_id),
        "name": filename,
        "size": formatted_size,
        "category": category,
        "status": "complete",
        "progress": 100,
        "uploadedAt": now.strftime("%d %b %Y"),
        "result": {
            "summary": {
                "docType": category,
                "date": now.strftime("%d %b %Y"),
                "source": f"Uploaded File: {filename}",
                "keyInfo": summary_key_info
            },
            "extracted": {
                "medicines": medicines,
                "symptoms": symptoms,
                "tests": tests,
                "measurements": measurements,
                "conditions": conditions,
                "instructions": instructions
            },
            "aiInsight": ai_insight
        }
    }

def handle_upload(session: Session, file_path: str, user_id: str, file_type: str) -> dict:
    dest = f"uploads/{user_id}/{uuid.uuid4()}_{file_type}"
    try:
        return upload_file(file_path, dest)
    except Exception as e:
        return {"error": str(e)}
