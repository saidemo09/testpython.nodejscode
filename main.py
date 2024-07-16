from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import FastAPI, Depends, status, WebSocket, WebSocketDisconnect, Request
from passlib.context import CryptContext
from datetime import timedelta, datetime
from typing import Annotated
from models import User, productAssistantChatRequest ,imageAssistantChatRequest   
import json
import auth
import os
from auth import get_current_user, create_access_token
import uvicorn
import openai
from  question_generator import question_generator
from enterprise_knowledge_management import ekm
from product_assistant import chat_agent
from image_RAG import image_RAG_bot
from saic import saic
from video_transcribe import video_transcribe



import warnings
import logging
import yaml
import models
from dotenv import load_dotenv

import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable

# Auto-trace LLM calls in-context
client = wrap_openai(openai.Client())

warnings.filterwarnings("ignore", message="error reading bcrypt version", module="passlib.handlers.bcrypt")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)
logging.basicConfig()

def setup_logging(default_path='log_conf.yaml', default_level=logging.INFO, env_key='LOG_CFG'):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
        logging.info(f"logging set successfully")
    else:
        logging.basicConfig(level=default_level)
        logging.info(f"logging set without yaml log file")

setup_logging()

app = FastAPI()
app.include_router(auth.router)
app.include_router(question_generator.router)
app.include_router(chat_agent.router)
app.include_router(ekm.router)
app.include_router(image_RAG_bot.router)
app.include_router(saic.router)
app.include_router(video_transcribe.router)

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated=['auto'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost"], 
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def get_db():
    with open("db.json", "r+") as file:
        data = json.load(file)
    return data

def save_db(data):
    with open("db.json", "w") as file:
        json.dump(data, file, indent=4)

@app.post("/login")
def login(user: User):
    db = get_db()
    user_dict = user.dict(exclude_unset=True)
    found_user = next((u for u in db if u['username'] == user_dict['username']), None)

    if not found_user:
        return JSONResponse(status_code=404, content={"message": "User not found", "status_code": "404"})

    if not bcrypt_context.verify(user_dict['password'], found_user['password']):
        return JSONResponse(status_code=401, content={"message": "Incorrect username or password", "status_code": "401"})

    if not found_user.get("is_active", False):
        return JSONResponse(status_code=403, content={"message": "User is inactive", "status_code": "403"})

    access_token = create_access_token(found_user['username'], timedelta(minutes=20))

    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "access": found_user.get("access", []),
        "is_active": found_user.get("is_active", False),
        "message": "Login successful",
        "status_code": "200"
    }

@app.get("/websocket_ekm")
async def get_websocket_test_ekm():
    try:
        # file_path = "R:/Work/Asoft/AI_DEMO_HUB/demohub-ai/backend/enterprise_knowledge_management/websocket_test.html"
        file_path = "enterprise_knowledge_management/websocket_test.html"
        logging.info(f"Trying to read file: {file_path}")
        with open(file_path, "r") as file:
            html_content = file.read()
        logging.info("Successfully read the file")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logging.error(f"Error reading websocket_test.html: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal server error"})

@app.websocket("/ws/enterprise_knowledge_management")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response = ekm.websocket_chat_with_agent(data)
            async for chunk in response:
                await websocket.send_text(chunk)
    except WebSocketDisconnect:
        logging.info("Client disconnected")

@app.get("/websocket_saic")
async def get_websocket_test_saic():
    try:
        file_path = "saic/websocket_test.html"
        logging.info(f"Trying to read file: {file_path}")
        with open(file_path, "r") as file:
            html_content = file.read()
        logging.info("Successfully read the file")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logging.error(f"Error reading websocket_test.html: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal server error"})

@app.websocket("/ws/saic")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response = saic.websocket_chat_with_saic(data)
            async for chunk in response:
                await websocket.send_text(chunk)
    except WebSocketDisconnect:
        logging.info("Client disconnected")

@app.get("/websocket_chat_agent")
async def get_websocket_test_pa():
    try:
        file_path = "product_assistant/websocket_test_pa.html"
        logging.info(f"Trying to read file: {file_path}")
        with open(file_path, "r") as file:
            html_content = file.read()
        logging.info("Successfully read the file")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logging.error(f"Error reading websocket_test.html: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal server error"})

@app.websocket("/ws/product_assistant")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            chat_request = productAssistantChatRequest.parse_raw(data)
            async for message in chat_agent.websocket_chat_with_agent(chat_request):
                await websocket.send_text(message)
    except WebSocketDisconnect:
        logging.info("Client disconnected")
    except Exception as e:
        logging.exception(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/websocket_image_RAG")
async def get_websocket_test_pa():
    try:
        file_path = "image_RAG/websocket_test_imageRAG.html"
        logging.info(f"Trying to read file: {file_path}")
        with open(file_path, "r") as file:
            html_content = file.read()
        logging.info("Successfully read the file")
        return HTMLResponse(content=html_content)
    except Exception as e:
        logging.error(f"Error reading websocket_test.html: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal server error"})

@app.websocket("/ws/image_RAG")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            chat_request = imageAssistantChatRequest.parse_raw(data)
            async for message in image_RAG_bot.chat_with_imageRAG(chat_request):
                await websocket.send_text(message)
    except WebSocketDisconnect:
        logging.info("Client disconnected")
    except Exception as e:
        logging.exception(f"WebSocket error: {e}")
    finally:
        await websocket.close()

async def main():
    try:
        config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user (CTRL+C). Exiting...")
    except Exception as e:
        logger.exception("Unexpected error: ", exc_info=e)
    finally:
        logger.info("Application shutdown complete.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())