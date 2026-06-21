from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import ChatRequest, ChatResponse
from app.services.llm_service import llm_service
from app.services.context_service import context_service

router = APIRouter(prefix="/chat", tags=["AI决策助手"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    context = context_service.build_full_context(db)
    reply = llm_service.ask(req.message, context)
    return ChatResponse(
        reply=reply,
        conversation_id=req.conversation_id or "default",
    )


@router.post("/ecology")
def chat_ecology(message: str = Body(...), db: Session = Depends(get_db)):
    context = context_service.build_full_context(db)
    reply = llm_service.ask(message, context)
    return {"reply": reply}


@router.post("/fire")
def chat_fire(message: str = Body(...), db: Session = Depends(get_db)):
    context = context_service.build_full_context(db)
    reply = llm_service.ask(message, context)
    return {"reply": reply}


@router.post("/risk")
def chat_risk(message: str = Body(...), db: Session = Depends(get_db)):
    context = context_service.build_full_context(db)
    reply = llm_service.ask(message, context)
    return {"reply": reply}


@router.post("/resource")
def chat_resource(message: str = Body(...), db: Session = Depends(get_db)):
    context = context_service.build_full_context(db)
    reply = llm_service.ask(message, context)
    return {"reply": reply}
