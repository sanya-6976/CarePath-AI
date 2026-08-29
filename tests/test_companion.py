import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_companion_router_is_registered():
    source = (ROOT / 'backend/app/main.py').read_text(encoding='utf-8')
    assert 'companion_router' in source
    assert 'app.include_router(companion_router' in source

def test_companion_uses_authenticated_identity_not_request_patient_id():
    source = (ROOT / 'backend/app/api/v1/endpoints/companion.py').read_text(encoding='utf-8')
    assert 'current_user=Depends(get_current_user)' in source
    assert 'retrieve_patient_context(db, current_user.user_id)' in source
    assert 'patient_id' not in source.split('class ChatRequest', 1)[1].split('class PreferenceRequest', 1)[0]

def test_companion_schema_is_valid_python_and_persists_memory_models():
    ast.parse((ROOT / 'backend/app/api/v1/endpoints/companion.py').read_text(encoding='utf-8'))
    models = (ROOT / 'database/models.py').read_text(encoding='utf-8')
    assert 'class CompanionConversation' in models
    assert 'class CompanionMessage' in models
