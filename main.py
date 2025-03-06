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
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from shapely.wkb import loads
import binascii
import json


from fastapi import FastAPI
import httpx
from shapely import wkb
from shapely.geometry import mapping
from pyproj import Transformer
from fastapi.responses import JSONResponse
from fastapi import FastAPI
import httpx
from shapely import wkb
from pyproj import Transformer
from fastapi.responses import JSONResponse
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
from shapely import wkt, wkb
from shapely.geometry import shape
from pyproj import Transformer

from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, select, func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from pydantic import BaseModel
from typing import Optional, Any
import logging
import json

from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from pydantic import BaseModel
from typing import Optional, Any
import logging
import json
from fastapi import FastAPI, Query
import asyncpg
import geojson
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
import geojson
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
import asyncpg

from fastapi import FastAPI, HTTPException, Query, Depends
from typing import Optional
import requests
import logging
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy import func 


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


app = FastAPI()
security = HTTPBearer()

# @app.get("/")
# def read_root():
#     return {"Welcome to the Chalo API. For questions, type /chalo-docs next."}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], #allow_methods=["GET"],
    allow_headers=["*"],
)

#-------------------------------------

# เพิ่ม Security Scheme สำหรับ Swagger UI
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


#-----------------------------------

def load_geojson_file(file_path):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"GeoJSON file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

try:
    with open("C:/Users/Areeya Bunma/Desktop/pandas/acc/heatmap-rvp-death.geojson", "r", encoding="utf-8") as f:
        geojson_data1 = json.load(f)
except FileNotFoundError:
    geojson_data1 = None

file_path2 = "C:/Users/Areeya Bunma/Desktop/pandas/acc/accident_grids_itic_dbscan_2022_2020.geojson"
try:
    geojson_data2 = load_geojson_file(file_path2)
except HTTPException as e:
    geojson_data2 = None
    

#---------------------------------------
##
###
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


templates = Jinja2Templates(directory="templates")
docs_url = "https://raw.githubusercontent.com/chaloemphona/Fast/refs/heads/main/docs.html"
openapi_url = "https://raw.githubusercontent.com/chaloemphona/Fast/refs/heads/main/openapi.json"

@app.get("/", response_class=HTMLResponse, tags=["Docs"])
async def read_docs():
    """
    The document describes information about Chalo.com APIs, including how to access data, usage, and related details.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(docs_url)
            response.raise_for_status() 
            return HTMLResponse(content=response.text, status_code=200)
    except httpx.HTTPStatusError as e:
        return f"Error loading docs.html: {e}"

@app.get("/chalo-api.json", response_class=HTMLResponse, tags=["Docs"])
async def custom_docs(request: Request):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(openapi_url)
            response.raise_for_status()  
            return HTMLResponse(content=response.text, status_code=200)
    except httpx.HTTPStatusError as e:
        return f"Error loading openapi.json: {e}"


#---------------------------------------
##
###
## ขอโทเค็น
# เก็บโทเค็น เเต่ถ้ามีฐานข้อมูลก็ใส่ได้เลย 
# tokens: Dict[str, str] = {}
tokens: Dict[str, dict] = {}

class TokenRequest(BaseModel):
    username: str

@app.post("/api/v1/token", tags=["Authentication"])
async def create_token(request: TokenRequest):
    token = str(uuid4())
    expiration_time = datetime.utcnow() + timedelta(minutes=180)
    tokens[token] = {
        "username": request.username,
        "expiration_time": expiration_time,
    }
    return {"status": "success", "token": token}
print(tokens)

async def verify_token(authorization: str = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Error 401 Missing or invalid Authorization token.",
        )
    
    token = authorization.replace("Bearer ", "").strip()
    if token not in tokens:
        raise HTTPException(
            status_code=401,
            detail="Error 401 Invalid token.",
        )
    print(tokens)

    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(
            status_code=401,
            detail="Error 401 Token has expired.",
        )
    return token_data["username"]



@app.get("/api/v1/protected", tags=["Authentication"])
async def protected_route(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """- ถ้าไม่ใส่โทเค็น เเล้วส่งคำขอเลยจะได้ **403**
       - ถ้าใส่โทเค็นผิด เเล้วส่งคำขอจะได้ **401** 
       - ถ้าใส่โทเค็นถูก เเล้วส่งคำขอจะได้ **200** กับ **500**"""
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    return {
        "status": "success",
        "message": f"สวัสดี, {token_data['username']}! การเข้าถึงได้รับอนุญาต",
    }


#------------------------------------
##
###
## ใช้งานจริง ตอนนี้
# @app.get("/api/v1/duckDBs/places/th/region", response_model=StandardResponse, status_code=200, tags=["DuckDBs"])
# async def get_data_in_duckdbs_region(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     limit: int = Query(default=1000, ge=1),  
#     offset: int = Query(default=0, ge=0),
#     region: str = Query(default=None, description="Filter by region (e.g., 'Bangkok')")  
# ):
#     """
#     Endpoint to fetch data from **DuckDB** table **places_th** in chunks as **GeoJSON**.
#     - **limit**: The number of records to return (default 1000)
#     - **offset**: The offset for pagination (default 0)
#     - **region**: Region filter (default None, fetches all regions)
#     """

#     token = credentials.credentials 
#     if token not in tokens:
#         raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
#     token_data = tokens[token]
#     if datetime.utcnow() > token_data["expiration_time"]:
#         del tokens[token]
#         raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"""
#             CREATE TABLE IF NOT EXISTS places_th AS
#             SELECT fsq_place_id, name, latitude, longitude, address, locality, region, country,
#                    date_created, date_refreshed, date_closed
#             FROM read_parquet([
#                     'D:\\parge\\in_parge\\places-00000.snappy.parquet',
#                     'D:\\parge\\in_parge\\places-00001.snappy.parquet',
#                     'D:\\parge\\in_parge\\places-00002.snappy.parquet'
#                     ])
#             WHERE country = 'TH'
#         """)
#         region_filter = f"WHERE region = '{region}'" if region else ""
#         query = f"""
#             SELECT * FROM places_th
#             {region_filter}
#             LIMIT {limit} OFFSET {offset}
#         """
#         rows = con.execute(query).fetchall()
#         column_headers = [desc[0] for desc in con.description]
#         features = []
#         for row in rows:
#             data = dict(zip(column_headers, row))
#             features.append({
#                 "type": "Feature",
#                 "properties": {
#                     key: value for key, value in data.items() if key not in ["latitude", "longitude"]
#                 },
#                 "geometry": {
#                     "type": "Point",
#                     "coordinates": [data["longitude"], data["latitude"]]
#                 }
#             })
#         geojson = {
#             "type": "FeatureCollection",
#             "features": features
#         }
#         count_query = f"SELECT COUNT(*) FROM places_th {region_filter}"
#         row_count = con.execute(count_query).fetchone()[0]
#         con.close()
#         metadata = {
#             "row_count": len(features),
#             "next_offset": offset + limit,
#             "Total_all_data": row_count,
#             "data for ": {token_data['username']}
#         }

#         return StandardResponse(
#             status="success",
#             message="Data fetched successfully as GeoJSON",
#             data=geojson,
#             metadata=metadata,
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error 500 Failed to fetch data from DuckDB: {str(e)}",
#         )
    


    

@app.get("/api/v1/pgDBs/places/th/hexagon", response_model=StandardResponse, status_code=200, tags=["postgres"])
def convert_gpdbs_to_h3(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    API region fetches data from the **DuckDB** service and converts the region data into **H3** format.
    """
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        raise HTTPException(status_code=401, detail="Error 401 Missing or invalid Authorization token.")
    token = authorization_header.split(" ")[1]  
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "skip-browser-warning"
    }
    
    response = requests.get("https://chalo.click/api/v1/pgDBs/places/th?limit=6000", headers=headers)
    
    geojson_data = response.json()
    if geojson_data.get("status") != "success":
        return {"status": "error", "message": "Failed to fetch data"}
    
    features = geojson_data["data"]["features"]
    h3_counts = {}

    for feature in features:
        geometry = feature.get("geometry")
        if geometry and geometry.get("type") == "Point":
            coordinates = geometry.get("coordinates")
            if coordinates and len(coordinates) == 2:
                lon, lat = coordinates 
                if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                    h3_index = h3.latlng_to_cell(lat, lon, 6)  
                    h3_counts[h3_index] = h3_counts.get(h3_index, 0) + 1
                else:
                    print(f"Skipping invalid coordinates: {coordinates}")
            else:
                print(f"Skipping malformed coordinates: {coordinates}")
        else:
            print(f"Skipping feature with invalid geometry: {geometry}")
    
    h3_features = []
    for h3_index, count in h3_counts.items():
        polygon_coords = h3.cell_to_boundary(h3_index)  # ค่าที่ได้เป็น (lat, lon)

        # สลับให้เป็น (lon, lat) ตามมาตรฐาน GeoJSON
        geojson_coords = [[lon, lat] for lat, lon in polygon_coords]

        # ปิด Polygon โดยเพิ่มจุดแรกเป็นจุดสุดท้าย
        if geojson_coords and geojson_coords[0] != geojson_coords[-1]:
            geojson_coords.append(geojson_coords[0])

        h3_features.append({
            "type": "Feature",
            "properties": {
                "h3_index": h3_index,
                "point_count": count
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [geojson_coords]
            }
        })
    
    result_geojson = {
        "type": "FeatureCollection",
        "features": h3_features
    }
    metadata = {
        "total_H3": len(h3_features),
        "data for": token_data['username']
    }
    return {
        "status": "success",
        "message": "Data converted to H3 successfully",
        "data": result_geojson,
        "metadata": metadata
    }



#------------------------------------------
##
###
# GitHub
@app.get("/api/v1/github/accident/heatmap-rvp-death", status_code=200, response_model=StandardResponse, tags=["Github"])
async def geojson_from_github_heatmap_rvp_death(limit: int = Query(default=None, ge=1), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Endpoint to fetch **GeoJSON** data from GITHUB `heatmap-rvp-death.geojson`, 
    it will include metadata about the file, mean total number to be awarded and prepare to return in **GeoJSON**."""

    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
    github_url = "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/heatmap-rvp-death.geojson" 
    try:
        response = requests.get(github_url)
        response.raise_for_status()  
        geojson_data = response.json()  
        feature_grids = len(geojson_data.get("features", []))

        features = geojson_data.get("features", [])
        if limit:
            features = features[:limit]

        limited_geojson = {**geojson_data, "features": features}

        return create_response(
            status="success",
            message="GeoJSON file fetched successfully",
            data=limited_geojson,
            metadata={"source": github_url, "feature_count": feature_grids}
        )
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"HTTP error occurred: {http_err}"
        )
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(
            status_code=500,
            detail=f"500 Request error occurred: {req_err}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"500 Unexpected error occurred: {str(e)}"
        )



#เเบบกำหนด ?no=.... / ?gid=.... / ?no=...&gid=...
@app.get("/api/v1/github/accident/itic-top200-all-road", status_code=200, response_model=StandardResponse, tags=["Github"])
async def geojson_from_github_select_id(no: Optional[int] = None, gid: Optional[int] = None , credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Endpoint to fetch **GeoJSON** data from **GITHUB** `itic-top200-all-road` with filtering by 'no' or 'gid'."""

    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
    github_url = "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/itic-top200-all-road.geojson"
    try:
        response = requests.get(github_url)
        response.raise_for_status()
        geojson_data = response.json()
        features = geojson_data.get("features", [])
        if no is not None:
            features = [feature for feature in features if feature["properties"].get("no") == no]
        if gid is not None:
            features = [feature for feature in features if feature["properties"].get("gid") == gid]
        geojson_data["features"] = features
        return create_response(
            status="success",
            message=f"GeoJSON file fetched successfully with {len(features)} matching features",
            data=geojson_data,
            metadata={
                "source": github_url,
                "feature_count": len(features),
                
            }
        )
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"HTTP error occurred: {http_err}"
        )
    except requests.exceptions.RequestException as req_err:
        raise HTTPException(
            status_code=500,
            detail=f"500 Request error occurred: {req_err}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"500 Unexpected error occurred: {str(e)}"
        )



#เงื่อนไขการเลือกจุดสิ้นสุด
@app.get("/api/v1/github/accident/data/select", status_code=200, response_model=StandardResponse, tags=["Github"])
async def github_selects_data_endpoint(file: str = Query(..., description="Name of the GeoJSON file"), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """จุดสิ้นสุดนี้เป็นการรับข้อมูล **GEOJSON** มาจาก **GITHUB** โดยสามารถเลือกไฟล์ที่จะเปิดจากพารามิเตอร์ **file** data_(select one number 0-9)"""

    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
    github_urls = {
        "data_0": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/accident_grids_itic_dbscan_2022_2020.geojson",
        "data_1": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/accident_grids_rvp_dbscan_2022_2020.geojson",
        "data_2": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/accident_grids_rvp_dbscan_2022_2020_death.geojson",
        "data_3": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/accident_grids_rvp_dbscan_2022_2020_injured.geojson",
        "data_4": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/thairsc-top200-injured-road.geojson",
        "data_5": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/heatmap-rvp-death.geojson",
        "data_6": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/heatmap-rvp.geojson",
        "data_7": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/itic-top200-all-road.geojson",
        "data_8": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/thairsc-top200-all-road.geojson",
        "data_9": "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/thairsc-top200-death-road.geojson"
    }
    if file not in github_urls:
        raise HTTPException(
            status_code=400,
            detail=f"File '{file}'. Please choose from {list(github_urls.keys())}'."
        )
    github_url = github_urls[file]
    try:
        response = requests.get(github_url)
        response.raise_for_status()  
        geojson_data = response.json()  
        feature_grids = len(geojson_data.get("features", []))
        return create_response(
            status="success",
            message="GeoJSON file fetched successfully",
            data=geojson_data,
            metadata={"source": github_url, "feature_count": feature_grids}
        )
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"HTTP error occurred: {http_err}"
        )
    except json.JSONDecodeError: 
        raise HTTPException(
            status_code=422,
            detail=f"422 Failed to parse the file: {github_url} as valid GeoJSON."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"500 Unexpected error occurred: {str(e)}"
        )



# ---------------------------------------------
##
###
#### เรียกข้อมมูลจาก ฐานข้อมูล ตาราง places_th
# DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/FSQ_DB"
# engine = create_async_engine(DATABASE_URL, echo=True)
# SessionLocal = sessionmaker(
#     bind=engine, 
#     class_=AsyncSession, 
#     expire_on_commit=False
#         )

DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_OQ7G9bfaekzV@ep-small-credit-a9tj4gjc-pooler.gwc.azure.neon.tech:5432/neondb"
engine = create_async_engine(DATABASE_URL, echo=True, connect_args={"ssl": True})
SessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
        )
        
Base = declarative_base()
        
class Place001(Base):
            __tablename__ = "places_th"
            id = Column(Integer, primary_key=True, index=True)
            fsq_place_id = Column(String, unique=True, index=True)  
            name = Column(String, index=True)
            address = Column(String)
            latitude = Column(String)
            longitude =Column(String)
            region = Column(String)
            country = Column(String)
            geometry = Column(Text) 

class StandardResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any] = None
    metadata: Optional[dict] = None

def fsqBB_to_dict(obj):
            return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

@app.get("/api/v1/pgDBs/places/th", status_code=200, response_model=StandardResponse, tags=["postgres"])
async def get_places(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = Query(1000, description="Number of records to retrieve", ge=1),
    offset: int = Query(0, description="Number of records to skip", ge=0),
    lat: Optional[float] = Query(None, description="Latitude of the user"),
    lon: Optional[float] = Query(None, description="Longitude of the user"),
    radius: int = Query(None, description="Search radius in meters", ge=1),
    region: Optional[str] = Query(None, description="Region to filter results")
):
    """Endpoint ค้นหาสถานที่รอบตัวฉันภายในรัศมีที่กำหนด พร้อมตัวกรอง region
    - **limit** จำกัดการเเสดงข้อมมูล เริ่มต้นที่ 1
    - **offset** เริ่มเเสดงข้อมูลตั้งเเต่ตัวที่กำหนด เริ่มต้นที่ 0
    - **lat** **lon** พิกัดที่ต้องการเป็นจุดศุนย์กลาง
    - **radius** รัศมีที่ต้องการให้ค้นหารอบตัว หน่วย เมตร
    - **region** ค้นหาเฉพาะสถานที่ใน region ที่กำหนด
    """
    
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")

    try:
        async with SessionLocal() as session:
            query = select(
                Place001.id, 
                Place001.fsq_place_id, 
                Place001.name, 
                Place001.address, 
                Place001.latitude,
                Place001.longitude,
                Place001.region, 
                Place001.country, 
                Place001.geometry
            ).limit(limit).offset(offset)

            # กรองตาม region
            if region:
                query = query.where(Place001.region == region)

            # กรองตามระยะทาง
            if lat is not None and lon is not None:
                query = query.where(
                    text(f"""
                        ST_DWithin(
                            geometry::geography,
                            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                            :radius
                        )
                    """)
                ).params(lon=lon, lat=lat, radius=radius)  

            result = await session.execute(query)
            places = result.all()

            if not places:
                raise HTTPException(status_code=404, detail="404 No places found within the specified radius or region")

            features = []
            for place in places:
                if place.latitude is None or place.longitude is None:
                    logging.warning(f"Skipping record {place.id} due to missing coordinates")
                    continue  

                try:
                    lon, lat = float(place.longitude), float(place.latitude)
                    if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                        logging.warning(f"Skipping invalid coordinate: {lon}, {lat} for record {place.id}")
                        continue 
                except ValueError:
                    logging.warning(f"Skipping record {place.id} due to invalid coordinate format")
                    continue  

                place_data = {
                    "id": place.id,
                    "fsq_place_id": place.fsq_place_id,
                    "name": place.name,
                    "address": place.address,
                    "region": place.region,
                    "country": place.country,
                    "geometry": place.geometry
                }
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        key: value for key, value in place_data.items() if key not in ["latitude", "longitude"]
                    }
                })
            geojson = {
            "type": "FeatureCollection",
            "features": features
            }

            total_count_result = await session.execute(select(func.count()).select_from(Place001))
            total_count = total_count_result.scalar()

            return StandardResponse(
                status="success",
                message="Data retrieved successfully",
                data=geojson,
                metadata={
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "radius": radius,
                    "region": region
                }
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="500 Internal Server Error")

    




# ---------------------------------------------
##
###
#### เรียกข้อมมูลจาก ฐานข้อมูล ตาราง places_h3_lv6
class PlaceH3Lv6(Base):
    __tablename__ = "places_h3_v6"
    id = Column(Integer, primary_key=True, index=True)
    h3_index = Column(String(255), index=True)
    point_count = Column(Integer)
    geometry = Column(Text)  

class StandardResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any] = None
    metadata: Optional[dict] = None 

@app.get("/api/v1/pgDBs/places/th/hexagon-lv6", status_code=200, response_model=StandardResponse, tags=["postgres"])
async def get_places(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = Query(10, description="Number of records to retrieve", ge=1),
    offset: int = Query(0, description="Number of records to skip", ge=0),
):
    """Endpoint นี้เป็นการเรียกข้อมูลจากตารางชื่อ **places_h3_lv6** มาเเสดง
        - **limit** จำกัดการเเสดงข้อมมูล เริ่มต้นที่ 1
        - **offset** เริ่มเเสดงข้อมูลตั้งเเต่ตัวที่กำหนด เริ่มต้นที่ 0
      """
    
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    try:
        if limit < 1:
            raise HTTPException(status_code=422, detail="Limit must be at least 1")
        if offset < 0:
            raise HTTPException(status_code=422, detail="Offset must be greater than or equal to 0")

        async with SessionLocal() as session:
            result = await session.execute(
                select(
                    PlaceH3Lv6.id,
                    PlaceH3Lv6.h3_index,
                    PlaceH3Lv6.point_count,
                    PlaceH3Lv6.geometry
                )
                .limit(limit)
                .offset(offset)
            )
            places = result.all()

            if not places:
                raise HTTPException(status_code=404, detail="404 No places found")

            features = []
            for place in places:
                place_data = {
                    "id": place.id,
                    "h3_index": place.h3_index,
                    "point_count": place.point_count,
                    "geometry": place.geometry
                }
                if not place.geometry:
                    logging.warning(f"Skipping record {place.id} due to missing geometry")
                    continue

                try:
                    geojson = {
                        "type": "Feature",
                        "properties": {
                            key: value for key, value in place_data.items() if key != "geometry"
                        },
                        "geometry": {
                            "type": "Polygon",  
                            "coordinates": place.geometry  
                        }
                    }
                    features.append(geojson)
                except Exception as e:
                    logging.warning(f"Skipping record {place.id} due to invalid geometry format: {e}")
                    continue

            total_count_result = await session.execute(select(func.count()).select_from(PlaceH3Lv6))
            total_count = total_count_result.scalar()

            return StandardResponse(
                status="success",
                message="Data retrieved successfully",
                data=features,
                metadata={
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                }
            )
    except HTTPException as e:
        raise e 
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="500 Internal Server Error")
            
            




# ---------------------------------------------
##
###
#### บันทึกข้อมมูลลง ฐานข้อมูล ตาราง places_th
class Place002(Base):
    __tablename__ = "places_thh"
    
    id = Column(Integer, primary_key=True, index=True)
    fsq_place_id = Column(String, unique=True, index=True)
    name = Column(String)
    address = Column(String)
    locality = Column(String)
    region = Column(String)
    country = Column(String)
    date_created = Column(String)
    date_refreshed = Column(String)
    date_closed = Column(String)
    latitude = Column(Float) 
    longitude = Column(Float) 
    geometry = Column(Geometry(geometry_type="POINT", srid=4326))


def convert_dataframe_to_dict(df):
    return df.to_dict(orient="records")

@app.post("/api/v1/pgDBs/places/th", status_code=200, response_model=StandardResponse, tags=["postgres"])
async def import_places(credentials: HTTPAuthorizationCredentials = Depends(security),):
    """Endpoint เป็นการอ่านไฟล์ **.parquet** เเลัวทำการบันทึกข้อมูลลงตาราง **places_th**"""
    
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    

    parquet_file_path = r"D:\parge\in_parge\places-00013.snappy.parquet"
    df = pd.read_parquet(parquet_file_path)

    places_data_filtered = [
        place for place in df.to_dict(orient="records") if place.get('country') == 'TH'
    ]

    async with SessionLocal() as session:
        try:
            for place in places_data_filtered:
                longitude = place.get('longitude')
                latitude = place.get('latitude')

                if longitude is None or latitude is None:
                    print(f"Skipping record due to missing coordinates: {place}")
                    continue
                if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
                    print(f"Skipping record due to invalid coordinates: {place}")
                    continue

                new_place = Place002(
                    fsq_place_id=place['fsq_place_id'],
                    name=place['name'],
                    address=place['address'],
                    locality=place['locality'],
                    region=place['region'],
                    country=place['country'],
                    date_created=place['date_created'],
                    date_refreshed=place['date_refreshed'],
                    date_closed=place['date_closed'],
                    latitude=latitude, 
                    longitude=longitude,
                    geometry=WKTElement(f"POINT({longitude} {latitude})", srid=4326) 
                )
                session.add(new_place)

            await session.commit()
            return StandardResponse(
                status="success",
                message="Data successfully imported into the database.",
                data=None,
                metadata={"total_count": len(places_data_filtered)}
            )
        except Exception as e:
            await session.rollback()
            return StandardResponse(
                status="error",
                message=f"An error occurred: {e}",
                data=None,
                metadata=None
            )





# ---------------------------------------------
##
###
#### ดึงข้อมูลจากฐานข้อมูลมา เเล้วบันทึกเป็นไฟล์ geojson 
# @app.get("/api/v1/pgDBs/export_geojson", status_code=200, response_model=StandardResponse, tags=["postgres"])
# async def export_geojson(background_tasks: BackgroundTasks ,credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """Endpoint เป็นการอ่านข้อมูลฝนตาราง **places_th** จากนั้นทำการบันทึกเป็ฯไฟล์ **Geojson** """
    
#     token = credentials.credentials  
#     if token not in tokens:
#         raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
#     token_data = tokens[token]
#     if datetime.utcnow() > token_data["expiration_time"]:
#         del tokens[token]
#         raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
#     async with SessionLocal() as session:
#         result = await session.execute(
#             select(
#                 Place001.id,
#                 Place001.fsq_place_id,
#                 Place001.name,
#                 Place001.address,
#                 Place001.latitude,
#                 Place001.longitude,
#                 Place001.region,
#                 Place001.country,
#                 Place001.geometry
#             )
#         )
#         places = result.all()

#         features = []
#         for place in places:
#             features.append({
#                 "type": "Feature",
#                 "properties": {
#                     "id": place.id,
#                     "fsq_place_id": place.fsq_place_id,
#                     "name": place.name,
#                     "address": place.address,
#                     "region": place.region,
#                     "country": place.country
#                 },
#                 "geometry": {
#                     "type": "Point",
#                     "coordinates": [float(place.longitude), float(place.latitude)]
#                 }
#             })

#         geojson_data = {
#             "type": "FeatureCollection",
#             "features": features
#         }

#         async def save_to_file():
#             async with aiofiles.open("places.geojson", "w", encoding="utf-8") as f:
#                 await f.write(json.dumps(geojson_data, indent=2, ensure_ascii=False))
#         background_tasks.add_task(save_to_file)
#     return {"status": "success", "message": "GeoJSON export started in background"}






# ---------------------------------------------
##
###
#### ดึงข้อมูลจากฐานข้อมูลมา เเล้วบันทึกเป็นไฟล์ geojson  เเลวนำไฟลืนั้นมาทำ H3 level 6 เเล้วส่งกลับไปยัง places_h3_lv6
# GEOJSON_FILE_PATH = r"C:\Users\Areeya Bunma\Desktop\pandas\FastAPI\places.geojson"

# @app.get("/api/v1/pgDBs/places/th/imhexagon", status_code=200, response_model=StandardResponse, tags=["postgres"])
# async def convert_geojson_to_h3(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """Endpoint เป็นการอ่านข้อมูลในไฟล์ **Geojson** เเล้วเเปลงเป็ฯ **H3** **level** **6** จากนั้นบันทึกลงตาราง **places_h3_lv6**"""
    
#     token = credentials.credentials  
#     if token not in tokens:
#         raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
#     token_data = tokens[token]
#     if datetime.utcnow() > token_data["expiration_time"]:
#         del tokens[token]
#         raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
#     try:
#         async with aiofiles.open(GEOJSON_FILE_PATH, mode="r", encoding="utf-8") as f:
#             geojson_str = await f.read()
#         geojson_data = json.loads(geojson_str)
#         features = geojson_data.get("features", [])
#         h3_counts = {}
#         for feature in features:
#             geometry = feature.get("geometry")
#             if not geometry or geometry.get("type") != "Point":
#                 continue  
#             coordinates = geometry.get("coordinates")
#             if not coordinates or len(coordinates) != 2:
#                 continue 
#             lon, lat = coordinates
#             if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
#                 continue
#             if lon == 0 and lat == 0:
#                 continue 
#             if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
#                 continue 
#             try:
#                 h3_index = h3.latlng_to_cell(lat, lon, 6)
#                 if h3_index in h3_counts:
#                     h3_counts[h3_index] += 1
#                 else:
#                     h3_counts[h3_index] = 1
#             except Exception as e:
#                 print(f"Skipping invalid H3 conversion: {coordinates}, Error: {e}")
#         async with SessionLocal() as session:
#             async with session.begin():
#                 for h3_index, count in h3_counts.items():
#                     polygon_coords = h3.cell_to_boundary(h3_index)
#                     polygon_wkt = f"POLYGON(({','.join(f'{lon} {lat}' for lon, lat in polygon_coords)}))"
#                     insert_query = text("""
#                         INSERT INTO places_h3_lv6 (h3_index, point_count, geometry)
#                         VALUES (:h3_index, :point_count, ST_GeomFromText(:geometry, 4326))
#                     """)
#                     await session.execute(insert_query, {
#                         "h3_index": h3_index,
#                         "point_count": count,
#                         "geometry": polygon_wkt
#                     })
#         h3_features = []
#         for h3_index, count in h3_counts.items():
#             polygon_coords = h3.cell_to_boundary(h3_index)
#             h3_features.append({
#                 "type": "Feature",
#                 "properties": {
#                     "h3_index": h3_index,
#                     "point_count": count
#                 },
#                 "geometry": {
#                     "type": "Polygon",
#                     "coordinates": [polygon_coords]
#                 }
#             })
#         result_geojson = {
#             "type": "FeatureCollection",
#             "features": h3_features
#         }
#         metadata = {
#             "total_H3": len(h3_features)
#         }
#         return {
#             "status": "success",
#             "message": "Data converted to H3 and saved to database successfully",
#             "data": result_geojson,
#             "metadata": metadata
#         }
#     except Exception as e:
#         return {"status": "error", "message": f"Failed to process data: {str(e)}"}



@app.get("/api/v1/opendeve/places/hospi", status_code=200, response_model=StandardResponse, tags=["opendevelopmentmekong"])
def get_hospital(
    limit: int = Query(10, ge=1),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):  
    """
    API ดึงข้อมูลโดยกำหนดจำนวน limit ตามที่ผู้ใช้ระบุ (ค่าเริ่มต้น = 10)
    - limit: จำนวนเรคคอร์ดที่ต้องการดึง (ค่าขั้นต่ำ 1, ค่าสูงสุด 1000)
    """
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")

    API_URL = "https://data.thailand.opendevelopmentmekong.net/th/api/3/action/datastore_search?resource_id=cfe757fb-69b6-4f82-92cd-e5dfca865eb5"
    params = {"limit": limit}
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        result = response.json().get("result", {})

        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [rec.get("Long"), rec.get("Lat")]
                    },
                    "properties": {
                        "_id": rec.get("_id"),
                        "ID": rec.get("ID"),
                        "Ministry": rec.get("Ministry"),
                        "Department": rec.get("Department"),
                        "Agency": rec.get("Agency"),
                        "Address": rec.get("Address")
                    }
                } for rec in result.get("records", [])
            ]
        }

        hapi_all = result.get("total", 0)
        hapi_count = len(geojson_data["features"])

        return {
            "status": "success",
            "message": "GeoJSON file fetched successfully",
            "data": geojson_data,
            "metadata": {"feature_count": hapi_count, "total": hapi_all}
        }
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}






@app.get("/api/v1/opendeve/places/excise_department", status_code=200, response_model=StandardResponse, tags=["opendevelopmentmekong"])
def get_excise_department(
    limit: int = Query(10, ge=1),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):  
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")

    API_URL = "https://catalog.excise.go.th/api/3/action/datastore_search?resource_id=e9afa2fa-dc06-49ad-88bd-f16fe9b7efd9"
    params = {"limit": limit}
    response = requests.get(API_URL,params=params)

    if response.status_code == 200:
        result = response.json().get("result", {})

        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [rec.get("BRANCH_LONG"), rec.get("BRANCH_LAT")]
                    },
                    "properties": {
                       "_id": rec.get("_id"),
                        "OFFCODE": rec.get("OFFCODE"),
                        "OFFNAME": rec.get("OFFNAME"),
                        "Department": rec.get("Department"),
                        "RESPONSE_DESC": rec.get("RESPONSE_DESC"),
                        "WEB_URL": rec.get("WEB_URL"),
                        "PROVINCE_NAME": rec.get("PROVINCE_NAME"),
                        "REGION": rec.get("REGION"),
                        "BRANCH_ADDRESS": rec.get("BRANCH_ADDRESS"),
                    }
                } for rec in result.get("records", [])
            ]
        }

        excise_all = result.get("total", 0)
        excise_count = len(geojson_data["features"])

        return {
            "status": "success",
            "message": "GeoJSON file fetched successfully",
            "data": geojson_data,
            "metadata": {"feature_count": excise_count, "total": excise_all}
        }
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}





@app.get("/api/v1/opendeve/places/reservoir", status_code=200, response_model=StandardResponse, tags=["opendevelopmentmekong"])
def get_reservoir(
    limit: int = Query(10, ge=1),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):  
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")

    API_URL = "https://gdcatalog.go.th/api/3/action/datastore_search?resource_id=668a16eb-f479-48f4-a737-91870efbf95e"
    params = {"limit": limit}
    response = requests.get(API_URL,params=params)

    if response.status_code == 200:
        result = response.json().get("result", {})

        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [rec.get("Longitude"), rec.get("Latitude")]
                    },
                    "properties": {
                        "_id": rec.get("_id"),
                        "province": rec.get("จังหวัด"),
                        "district": rec.get("อำเภอ"),
                        "subdistrict": rec.get("ตำบล"),
                        "reservoir": rec.get("อ่างเก็บน้ำ"),
                        "size reservoir": rec.get("ขนาดอ่างเก็บน้ำ"),
                    }
                } for rec in result.get("records", [])
            ]
        }

        reservoir_all = result.get("total", 0)
        reservoir_count = len(geojson_data["features"])

        return {
            "status": "success",
            "message": "GeoJSON file fetched successfully",
            "data": geojson_data,
            "metadata": {"feature_count": reservoir_count, "total": reservoir_all}
        }
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}





@app.get("/api/v1/opendeve/places/well_water", status_code=200, response_model=StandardResponse, tags=["opendevelopmentmekong"])
def get_well_water(
    limit: int = Query(10, ge=1),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):  
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")

    API_URL = "https://gdcatalog.go.th/api/3/action/datastore_search?resource_id=654585d7-e892-47d4-bf3d-62a76e440fc0"
    params = {"limit": limit}
    response = requests.get(API_URL,params=params)

    if response.status_code == 200:
        result = response.json().get("result", {})

        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [rec.get("Longitude"), rec.get("Latitude")]
                    },
                    "properties": {
                        "_id": rec.get("_id"),
                        "province": rec.get("ชื่อจังหวัด"),
                        "district": rec.get("ชื่ออำเภอ"),
                        "subdistrict": rec.get("ชื่อตำบล"),
                        "village no.": rec.get("หมู่ที่"),
                        "name village": rec.get("ชื่อหมู่บ้าน"),
                        "well number": rec.get("หมายเลขบ่อ"),
                        "well type": rec.get("ประเภทบ่อ"),
                        "depth": rec.get("ความลึกเจาะ"),
                        "evo depth": rec.get("ความลึกพัฒนา"),
                        "water volime": rec.get("ปริมาณน้ำ (ลบ.ม./ชม.)"),
                        "water level": rec.get("ระดับน้ำปกติ (เมตร)"),
                        "water receding": rec.get("ระยะน้ำลด (เมตร)"),
                    }
                } for rec in result.get("records", [])
            ]
        }

        reservoir_all = result.get("total", 0)
        reservoir_count = len(geojson_data["features"])

        return {
            "status": "success",
            "message": "GeoJSON file fetched successfully",
            "data": geojson_data,
            "metadata": {"feature_count": reservoir_count, "total": reservoir_all}
        }
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}


@app.get("/api/v1/opendeve/places/hospi", status_code=200, response_model=StandardResponse, tags=["opendevelopmentmekong"])
def get_hospital(
    limit: int = Query(10, ge=1),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):  
    """
    API ดึงข้อมูลโดยกำหนดจำนวน limit ตามที่ผู้ใช้ระบุ (ค่าเริ่มต้น = 10)
    - limit: จำนวนเรคคอร์ดที่ต้องการดึง (ค่าขั้นต่ำ 1, ค่าสูงสุด 1000)
    """
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")

    API_URL = "https://data.thailand.opendevelopmentmekong.net/th/api/3/action/datastore_search?resource_id=cfe757fb-69b6-4f82-92cd-e5dfca865eb5"
    params = {"limit": limit}
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        result = response.json().get("result", {})

        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [rec.get("Long"), rec.get("Lat")]
                    },
                    "properties": {
                        "_id": rec.get("_id"),
                        "ID": rec.get("ID"),
                        "Ministry": rec.get("Ministry"),
                        "Department": rec.get("Department"),
                        "Agency": rec.get("Agency"),
                        "Address": rec.get("Address")
                    }
                } for rec in result.get("records", [])
            ]
        }

        hapi_all = result.get("total", 0)
        hapi_count = len(geojson_data["features"])

        return {
            "status": "success",
            "message": "GeoJSON file fetched successfully",
            "data": geojson_data,
            "metadata": {"feature_count": hapi_count, "total": hapi_all}
        }
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}






@app.get("/api/v1/opendeve/places/excise_department", status_code=200, response_model=StandardResponse, tags=["opendevelopmentmekong"])
def get_excise_department(
    limit: int = Query(10, ge=1),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):  
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")

    API_URL = "https://catalog.excise.go.th/api/3/action/datastore_search?resource_id=e9afa2fa-dc06-49ad-88bd-f16fe9b7efd9"
    params = {"limit": limit}
    response = requests.get(API_URL,params=params)

    if response.status_code == 200:
        result = response.json().get("result", {})

        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [rec.get("BRANCH_LONG"), rec.get("BRANCH_LAT")]
                    },
                    "properties": {
                       "_id": rec.get("_id"),
                        "OFFCODE": rec.get("OFFCODE"),
                        "OFFNAME": rec.get("OFFNAME"),
                        "Department": rec.get("Department"),
                        "RESPONSE_DESC": rec.get("RESPONSE_DESC"),
                        "WEB_URL": rec.get("WEB_URL"),
                        "PROVINCE_NAME": rec.get("PROVINCE_NAME"),
                        "REGION": rec.get("REGION"),
                        "BRANCH_ADDRESS": rec.get("BRANCH_ADDRESS"),
                    }
                } for rec in result.get("records", [])
            ]
        }

        excise_all = result.get("total", 0)
        excise_count = len(geojson_data["features"])

        return {
            "status": "success",
            "message": "GeoJSON file fetched successfully",
            "data": geojson_data,
            "metadata": {"feature_count": excise_count, "total": excise_all}
        }
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}





@app.get("/api/v1/opendeve/places/reservoir", status_code=200, response_model=StandardResponse, tags=["opendevelopmentmekong"])
def get_reservoir(
    limit: int = Query(10, ge=1),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):  
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")

    API_URL = "https://gdcatalog.go.th/api/3/action/datastore_search?resource_id=668a16eb-f479-48f4-a737-91870efbf95e"
    params = {"limit": limit}
    response = requests.get(API_URL,params=params)

    if response.status_code == 200:
        result = response.json().get("result", {})

        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [rec.get("Longitude"), rec.get("Latitude")]
                    },
                    "properties": {
                        "_id": rec.get("_id"),
                        "province": rec.get("จังหวัด"),
                        "district": rec.get("อำเภอ"),
                        "subdistrict": rec.get("ตำบล"),
                        "reservoir": rec.get("อ่างเก็บน้ำ"),
                        "size reservoir": rec.get("ขนาดอ่างเก็บน้ำ"),
                    }
                } for rec in result.get("records", [])
            ]
        }

        reservoir_all = result.get("total", 0)
        reservoir_count = len(geojson_data["features"])

        return {
            "status": "success",
            "message": "GeoJSON file fetched successfully",
            "data": geojson_data,
            "metadata": {"feature_count": reservoir_count, "total": reservoir_all}
        }
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}





@app.get("/api/v1/opendeve/places/well_water", status_code=200, response_model=StandardResponse, tags=["opendevelopmentmekong"])
def get_well_water(
    limit: int = Query(10, ge=1),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):  
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")

    API_URL = "https://gdcatalog.go.th/api/3/action/datastore_search?resource_id=654585d7-e892-47d4-bf3d-62a76e440fc0"
    params = {"limit": limit}
    response = requests.get(API_URL,params=params)

    if response.status_code == 200:
        result = response.json().get("result", {})

        geojson_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [rec.get("Longitude"), rec.get("Latitude")]
                    },
                    "properties": {
                        "_id": rec.get("_id"),
                        "province": rec.get("ชื่อจังหวัด"),
                        "district": rec.get("ชื่ออำเภอ"),
                        "subdistrict": rec.get("ชื่อตำบล"),
                        "village no.": rec.get("หมู่ที่"),
                        "name village": rec.get("ชื่อหมู่บ้าน"),
                        "well number": rec.get("หมายเลขบ่อ"),
                        "well type": rec.get("ประเภทบ่อ"),
                        "depth": rec.get("ความลึกเจาะ"),
                        "evo depth": rec.get("ความลึกพัฒนา"),
                        "water volime": rec.get("ปริมาณน้ำ (ลบ.ม./ชม.)"),
                        "water level": rec.get("ระดับน้ำปกติ (เมตร)"),
                        "water receding": rec.get("ระยะน้ำลด (เมตร)"),
                    }
                } for rec in result.get("records", [])
            ]
        }

        reservoir_all = result.get("total", 0)
        reservoir_count = len(geojson_data["features"])

        return {
            "status": "success",
            "message": "GeoJSON file fetched successfully",
            "data": geojson_data,
            "metadata": {"feature_count": reservoir_count, "total": reservoir_all}
        }
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}






GRAPHOPPER_API_KEY = "ec221458-d6a0-4541-8119-225341d4bb20" 
async def get_db():
    async with SessionLocal() as session:
        yield session

@app.get("/api/v1/route_to_place", status_code=200, tags=["route"])
async def get_route_to_place(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    start_lat: Optional[float] = Query(None, description="Latitude จุดเริ่มต้น"),
    start_lon: Optional[float] = Query(None, description="Longitude จุดเริ่มต้น"),
    place_name: Optional[str] = Query(None, description="ชื่อร้านที่ต้องการไป"),
    end_lat: Optional[float] = Query(None, description="Latitude ปลายทาง"),
    end_lon: Optional[float] = Query(None, description="Longitude ปลายทาง"),
    session: AsyncSession = Depends(get_db),
):
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
        
    if not start_lat or not start_lon:
        raise HTTPException(status_code=400, detail="ต้องระบุพิกัดจุดเริ่มต้น")

    if place_name:
        query = select(
            Place001.latitude, Place001.longitude, Place001.name
        ).where(func.lower(Place001.name).like(f"%{place_name.lower()}%"))
        
        result = await session.execute(query)
        place = result.first()
        if not place:
            raise HTTPException(status_code=404, detail="ไม่พบสถานที่ที่ระบุ")
        end_lat, end_lon = place.latitude, place.longitude

    elif not end_lat or not end_lon:
        raise HTTPException(status_code=400, detail="ต้องระบุปลายทาง")

    # เรียกใช้ GraphHopper API
    url = "https://graphhopper.com/api/1/route"
    params = {
        "point": [f"{start_lat},{start_lon}", f"{end_lat},{end_lon}"],
        "profile": "car",
        "format": "json",
        "key": GRAPHOPPER_API_KEY,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching route")

    route_data = response.json()
    
    # ดึงระยะทางจาก API
    distance_meters = route_data["paths"][0]["distance"]  # ระยะทางเป็นเมตร
    distance_km = distance_meters / 1000  # แปลงเป็นกิโลเมตร

    return {
        "status": "success",
        "message": "Route calculated successfully",
        "start_location": {"lat": start_lat, "lon": start_lon},
        "end_location": {"lat": end_lat, "lon": end_lon, "name": place_name},
        "distance": {
            "meters": round(distance_meters, 2),
            "kilometers": round(distance_km, 2),
        },
        "route": route_data
    }



if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT
    uvicorn.run(app, host="0.0.0.0", port=port)


