"""
Backend para el prototipo web del proyecto de servicio
becario: Toma de Desciciones con Algoritmos Geneticos

Juan Sebastian Gonzalez A01644942

Comando de ejecucion:
# dev
uvicorn main:app --reload
# Production
python3 main.py
uvicorn main:app --ssl-keyfile key.pem --ssl-certfile cert.pem
"""

import logging
import traceback
from typing import Any, Awaitable, Callable

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import texts

# API

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.middleware("http")
async def exception_middleware(request: Request, call_next: Callable[[Request], Awaitable[Any]]):
    """TODO"""
    try:
        return await call_next(request)
    except Exception as e: # pylint: disable=broad-except
        exc_traceback = traceback.format_exception(type(e), value=e, tb=e.__traceback__)
        logging.error('\n'.join(exc_traceback) + "\n - END OF EXCEPT -")
        return JSONResponse(content=str(e), status_code=500)

app.include_router(texts.router)

@app.get("/")
async def root() -> dict[str, str]:
    """Root de la api"""
    return {"response":"root"}

# Logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("errors.log"),
    ]
)

# SSL

SSL_ENABLED = False
SSL_CERT = "cert.pem"
SSL_KEY = "key.pem"

if __name__ == "__main__":
    if SSL_ENABLED:
        uvicorn.run(app, host="127.0.0.1", port=8000, ssl_certfile=SSL_CERT, ssl_keyfile=SSL_KEY)
    else:
        uvicorn.run(app, host="127.0.0.1", port=8000)
