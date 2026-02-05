from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.openapi.docs import get_swagger_ui_html
import httpx
import os

app = FastAPI(title="Neuron Platform Gateway")

AUTH_URL = os.getenv("AUTH_SERVICE_URL", "http://auth:8002")
INFERENCE_URL = os.getenv("INFERENCE_SERVICE_URL", "http://inference:8001")


async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized: No token provided")

    token = authorization.split(" ")[1]
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{AUTH_URL}/verify", params={"token": token})
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")
        return resp.json()


@app.post("/v1/llm/respond", tags=["Production"])
async def proxy_inference(request: Request, user=Depends(verify_token)):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{INFERENCE_URL}/predict", json=body)
        return resp.json()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Unified Docs",
        swagger_ui_parameters={
            "urls": [
                {"url": "/openapi.json", "name": "Gateway (Public)"},
                {"url": "http://localhost:8001/openapi.json", "name": "Inference (Internal)"},
                {"url": "http://localhost:8002/openapi.json", "name": "Auth (Internal)"},
            ]
        }
    )
