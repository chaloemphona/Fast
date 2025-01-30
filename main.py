import os
from fastapi import FastAPI
from fastapi import FastAPI, HTTPException, Request, Depends, Header, Query
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from zipfile import ZipFile
from pydantic import BaseModel
from typing import Any, Optional, List
import geojson
import requests
import json
import os
import duckdb
import h3
import redis
import asyncio
import aiohttp
import geopandas as gpd
import pandas as pd
from fastapi.responses import StreamingResponse

#โทเค็น
from uuid import uuid4
from typing import Dict
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import Security

#ssl
import ssl
import uvicorn

#Docs
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

#sql
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.future import select
from typing import List
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
from geoalchemy2 import WKTElement
from sqlalchemy import func
from sqlalchemy.types import Float
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks
import asyncio
import aiofiles
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.sql import text
import logging 

app = FastAPI()
security = HTTPBearer()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT
    uvicorn.run(app, host="0.0.0.0", port=port)


class StandardResponse(BaseModel):
    status: str = "success"  
    message: str  
    data: Optional[Any] = None  
    metadata: Optional[dict] = None 

def create_response(
        status: str, 
        message: str, 
        data: Optional[dict] = None, 
        metadata: Optional[dict] = None):
    response = {
        "status": status,
        "message": message,
        "data": data or {},
        "metadata": metadata or {}
    }
    return response

class Feature:
    type: str
    properties: dict
    geometry: dict

class GeoJSONResponse:
    type: str
    features: list[Feature]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], #allow_methods=["GET"],
    allow_headers=["*"],
)

@app.on_event("startup")
def add_security_definitions():
    if app.openapi_schema:
        app.openapi_schema["components"] = app.openapi_schema.get("components", {})
        app.openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
            }
        }
        for path in app.openapi_schema["paths"].values():
            for method in path.values():
                method["security"] = [{"bearerAuth": []}]



#Error handle
# custom handler เมื่อ URL ไม่ถูก
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "status": "error 404 ",
            "message": f"Invalid endpoint '{request.url.path}'. Please check the URL and try again. .+_+.",
        },
    )
# handler เมื่อ Validation Error องค์ประกอบไม่ครบ
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error 422",
            "message": "422 Validation error occurred. .$_$.",
            "details": exc.errors(),
        },
    )
# 500 Handler (Internal Server Error) server ล่ม
@app.exception_handler(500)
async def custom_500_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error 500",
            "message": "An unexpected error occurred. Please try again later. .-_-.",
        },
    )
# 403 Handler (Forbidden Error) ไม่ได้ใส่ Token
@app.exception_handler(403)
async def custom_403_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=403,
        content={
            "status": "error 403",
            "message": f"Access forbidden to the endpoint '{request.url.path}'. You do not have permission to access this resource. Please enter Token .*_*.",
        },
    )
# 401 Handler (Unauthorized Error) Token หมดอายุ หรือ ใส่ Token ผิด
@app.exception_handler(401) 
async def custom_401_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=401,
        content={
            "status": "error 401",
            "message": f"Unauthorized access to the endpoint '{request.url.path}'. You need to be authenticated to access this resource. Token is invalid or expired. .T_T.",
        },
    )


@app.get("/api/v1", tags=["Docs"])
async def message():
    """
    Test that the domain is valid and the endpoint is working.
    """
    return { "H e l l o  W o r l d "}
