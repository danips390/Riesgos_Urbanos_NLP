"""
Contiene los endpoint relacionados a los usuarios
"""
from pydantic import BaseModel
from fastapi import APIRouter, Body
from texts.texts_storage import assert_user_storage, del_user_storage
from texts.process_text import process_text_storage

router = APIRouter(
    prefix="/user",
    tags=["user"],
)
# Modelo para recibir los datos del usuario

assert_user_storage()

class TextPayload(BaseModel):
    text: str

@router.post("/process")
async def process_text(payload: TextPayload) -> dict[str, bool]:
    """Procesa el texto enviado y retorna las entidades extraídas"""
    print(payload.text)
    results = process_text_storage(payload.text)
    return {"valid_text": results}
