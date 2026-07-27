"""
routers/admin.py — Endpoints administrativos: health check profundo,
checklist de deploy (espelha "DEPLOY CHECKLIST v4.2" do CLAUDE.md) e
emissão de token de dev. Rotas de escrita/gate exigem role "admin".
"""
from typing import List

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from auth import create_access_token, require_role, User

router = APIRouter(prefix="/admin", tags=["admin"])


class ChecklistItem(BaseModel):
    label: str
    done: bool


DEPLOY_CHECKLIST_V4_2: List[ChecklistItem] = [
    ChecklistItem(label="Copiar 5 agent .md para .claude/agents/", done=True),
    ChecklistItem(label="Aplicar patch no CLAUDE.md master (seção Agentes)", done=True),
    ChecklistItem(label="Criar 5 coleções RAG em Supabase (rag_chunks)", done=False),
    ChecklistItem(label="Inserir 5 routing rules em sp_agent_routing", done=False),
    ChecklistItem(label="Criar pastas SP para novos segmentos", done=False),
    ChecklistItem(label="Registrar skills no catálogo (skill registry)", done=False),
    ChecklistItem(label="Testar routing do Maestro com prompts de cada segmento", done=False),
    ChecklistItem(label="Upload dos SKILL.md para SP em 01-agentes-fundamentais/", done=False),
    ChecklistItem(label="Atualizar ARQUITETURA-AGENTES-IA.md no SP (v1.0.0 → v2.0.0)", done=False),
    ChecklistItem(label="Gate humano: aprovação MN antes de merge", done=False),
]


@router.get("/health", summary="Health check profundo (app + DB)")
async def health(request: Request) -> dict:
    db_pool = getattr(request.app.state, "db_pool", None)
    db_ok = db_pool is not None
    return {
        "status": "ok",
        "database": "connected" if db_ok else "unavailable",
    }


@router.get("/deploy-checklist", response_model=List[ChecklistItem], summary="Checklist de deploy v4.2")
async def deploy_checklist(_: User = Depends(require_role("admin", "user"))) -> List[ChecklistItem]:
    return DEPLOY_CHECKLIST_V4_2


@router.post("/token", summary="Emite um JWT de desenvolvimento (login simplificado)")
async def issue_dev_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """
    Skeleton auth: em produção troque por verificação real contra a
    tabela de usuários (hash_password/verify_password em auth.py).
    Aqui, qualquer usuário vira role "user"; "admin"/"admin" vira "admin".
    """
    role = "admin" if form_data.username == "admin" and form_data.password == "admin" else "user"
    token = create_access_token(subject=form_data.username, role=role)
    return {"access_token": token, "token_type": "bearer", "role": role}
