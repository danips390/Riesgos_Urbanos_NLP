"""
Contiene los endpoint relacionados a los usuarios
"""
from pydantic import BaseModel
from fastapi import APIRouter, Body
from texts.texts_storage import assert_user_storage, del_user_storage
from texts.process_text import process_text_storage
from fastapi.responses import HTMLResponse

router = APIRouter(
    prefix="/user",
    tags=["user"],
)
# Modelo para recibir los datos del usuario

assert_user_storage()

class TextPayload(BaseModel):
    text: str

@router.post("/process", response_class=HTMLResponse)
async def process_text(payload: TextPayload) -> HTMLResponse:
    """Procesa el texto enviado y retorna las entidades extraídas"""
    print(payload.text)
    html_content = process_text_storage(payload.text)
    return HTMLResponse(content=html_content)

