# all
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

#---------------------------------------------


class StandardResponse(BaseModel):
    status: str = "success"  
    message: str  
    data: Optional[Any] = None  
    metadata: Optional[dict] = None  

#---------------------------------------------

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

#---------------------------------------------

app = FastAPI()
security = HTTPBearer()
import os

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


# ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# ssl_context.load_cert_chain(certfile="C:/ssl/cert.pem", keyfile="C:/ssl/key.pem")

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="192.168.10.166", port=8080, ssl_keyfile="C:/ssl/key.pem", ssl_certfile="C:/ssl/cert.pem")
    ## uvicorn.run("main:app", host="0.0.0.0", port=443, ssl_keyfile="C:/ssl/key.pem", ssl_certfile="C:/ssl/cert.pem")

###รันตัวนี้ในคอมมาน --->  uvicorn main:app --host 192.168.10.166 --port 8080 --ssl-keyfile "C:/ssl/key.pem" --ssl-certfile "C:/ssl/cert.pem" --reload        


# ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# ssl_context.load_cert_chain(certfile="C:/ssl/tls/server.crt", keyfile="C:/ssl/tls/server.key")

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="192.168.10.166", port=8080, ssl_keyfile="C:/ssl/tls/server.key", ssl_certfile="C:/ssl/tls/server.crt")


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
# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# import os
# import os
# challenge_dir = r"C:\Users\Areeya Bunma\Desktop\pandas\FastAPI\.well-known\acme-challenge"
# print(f"Challenge directory: {challenge_dir}")
# app.mount("/.well-known", StaticFiles(directory=challenge_dir, html=False), name="acme-challenge")
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



@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}


@app.get("/api/v1", tags=["Docs"])
async def message():
    """
    Test that the domain is valid and the endpoint is working.
    """
    return { "H e l l o  W o r l d "}


templates = Jinja2Templates(directory="templates")
@app.get("/chalo-docs", response_class=HTMLResponse, tags=["Docs"])
async def read_docs():    
    """
    The document describes information about Chalo.com APIs, including how to access data, usage, and related details.
    """
    try:
        file_path = os.path.join(os.getcwd(), 'templates', 'docs.html')
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error loading docs.html: {e}"

@app.get("/chalo-api.json", response_class=HTMLResponse, tags=["Docs"])
async def custom_docs(request: Request):
    return templates.TemplateResponse("openapi.json", {"request": request})






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
@app.get("/api/v1/duckDBs/places/th/region", response_model=StandardResponse, status_code=200, tags=["DuckDBs"])
async def get_data_in_duckdbs_region(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = Query(default=1000, ge=1),  
    offset: int = Query(default=0, ge=0),
    region: str = Query(default=None, description="Filter by region (e.g., 'Bangkok')")  
):
    """
    Endpoint to fetch data from **DuckDB** table **places_th** in chunks as **GeoJSON**.
    - **limit**: The number of records to return (default 1000)
    - **offset**: The offset for pagination (default 0)
    - **region**: Region filter (default None, fetches all regions)
    """

    token = credentials.credentials 
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
    file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
    try:
        con = duckdb.connect()
        con.execute(f"""
            CREATE TABLE IF NOT EXISTS places_th AS
            SELECT fsq_place_id, name, latitude, longitude, address, locality, region, country,
                   date_created, date_refreshed, date_closed
            FROM read_parquet([
                    'D:\\parge\\in_parge\\places-00000.snappy.parquet',
                    'D:\\parge\\in_parge\\places-00001.snappy.parquet',
                    'D:\\parge\\in_parge\\places-00002.snappy.parquet'
                    ])
            WHERE country = 'TH'
        """)
        region_filter = f"WHERE region = '{region}'" if region else ""
        query = f"""
            SELECT * FROM places_th
            {region_filter}
            LIMIT {limit} OFFSET {offset}
        """
        rows = con.execute(query).fetchall()
        column_headers = [desc[0] for desc in con.description]
        features = []
        for row in rows:
            data = dict(zip(column_headers, row))
            features.append({
                "type": "Feature",
                "properties": {
                    key: value for key, value in data.items() if key not in ["latitude", "longitude"]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [data["longitude"], data["latitude"]]
                }
            })
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        count_query = f"SELECT COUNT(*) FROM places_th {region_filter}"
        row_count = con.execute(count_query).fetchone()[0]
        con.close()
        metadata = {
            "row_count": len(features),
            "next_offset": offset + limit,
            "Total_all_data": row_count,
            "data for ": {token_data['username']}
        }

        return StandardResponse(
            status="success",
            message="Data fetched successfully as GeoJSON",
            data=geojson,
            metadata=metadata,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error 500 Failed to fetch data from DuckDB: {str(e)}",
        )
    


    

@app.get("/api/v1/duckDBs/places/th/region/hexagon", response_model=StandardResponse, status_code=200, tags=["H3"])
def convert_geojson_to_h3(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security),):
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
    
    response = requests.get("http://192.168.10.166:8000/api/v1/duckDBs/places/th/region?limit=260000", headers=headers)
    
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
                    h3_index = h3.geo_to_h3(lat, lon, 6)
                    if h3_index in h3_counts:
                        h3_counts[h3_index] += 1
                    else:
                        h3_counts[h3_index] = 1
                else:
                    print(f"Skipping invalid coordinates: {coordinates}")
            else:
                print(f"Skipping malformed coordinates: {coordinates}")
        else:
            print(f"Skipping feature with invalid geometry: {geometry}")
    
    h3_features = []
    for h3_index, count in h3_counts.items():
        polygon_coords = h3.h3_to_geo_boundary(h3_index, geo_json=True)
        h3_features.append({
            "type": "Feature",
            "properties": {
                "h3_index": h3_index,
                "point_count": count
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon_coords]
            }
        })
    result_geojson = {
        "type": "FeatureCollection",
        "features": h3_features
    }
    metadata = {
        "total_H3": len(h3_features),
        "data for ": {token_data['username']}
    }
    return {
        "status": "success",
        "message": "Data converted to H3 successfully",
        "data": result_geojson,
        "metadata": metadata
    }









#---------------------------------------
##
###
## data
@app.get("/api/v1/accidents/heatmap-rvp-death", status_code=200, response_model=StandardResponse, tags=["Data GeoJSON"])
async def get_accidents( credentials: HTTPAuthorizationCredentials = Depends(security),):  
    """This endpoint retrieves the **GeoJSON** data from the file `heatmap-rvp-death.geojson`.
    It also includes metadata about the file, such as the total number of features."""

    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
    if geojson_data1 is None:
        return create_response(
            status="error",  
            message="GeoJSON file 'heatmap-rvp-death.geojson' not found.",
        )
    feature_count = len(geojson_data1.get("features", []))
    return create_response(
        status="success",  
        message=f"GeoJSON for data retrieved successfully. ",
        data=geojson_data1,
        metadata={
            "file_name": "heatmap-rvp-death.geojson",
            "feature_count": feature_count,     
        }
    )




@app.get("/api/v1/accidents/grids-dbscan-2022-2020", status_code=200, response_model=StandardResponse, tags=["Data GeoJSON"])
async def get_accidents2(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """This endpoint retrieves **GeoJSON** data from the file `accident_grids_itic_dbscan_2022_2020.geojson`.
    It includes metadata about the file, such as the total number of features. The file is processed 
    and prepared to be returned in the GeoJSON format."""

    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
    if geojson_data2 is None:
        return create_response(
            status="error",
            message="GeoJSON file 'accident_grids_itic_dbscan_2022_2020.geojson' not found."
        )
    feature_grids = len(geojson_data2.get("features", []))
    return create_response(
        status="success",
        message=f"GeoJSON data retrieved successfully.",
        data=geojson_data2,
        metadata={
            "file_name": "accident_grids_itic_dbscan_2022_2020.geojson",
            "feature_count": feature_grids, 
        }
    )












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
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/FSQ_DB"
engine = create_async_engine(DATABASE_URL, echo=True)
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
    limit: int = Query(10, description="Number of records to retrieve", ge=1),
    offset: int = Query(0, description="Number of records to skip", ge=0),
    lat: Optional[float] = Query(None, description="Latitude of the user"),
    lon: Optional[float] = Query(None, description="Longitude of the user"),
    radius: int = Query(500, description="Search radius in meters", ge=1)
):
    """Endpoint ค้นหาสถานที่รอบตัวฉันภายในรัศมีที่กำหนด
    - **limit** จำกัดการเเสดงข้อมมูล เริ่มต้นที่ 1
    - **offset** เริ่มเเสดงข้อมูลตั้งเเต่ตัวที่กำหนด เริ่มต้นที่ 0
    - **lat** **lon** พิกัดที่ต้องการเป็นจุดศุนย์กลาง
    - **radius** รัศมีที่ต้องการให้ค้นหารอบตัว หน่วย เมตร
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

            if lat is not None and lon is not None:
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
                ).where(
                    text(f"""
                        ST_DWithin(
                            geometry::geography,
                            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                            :radius
                        )
                    """)
                ).params(lon=lon, lat=lat, radius=radius).limit(limit).offset(offset)

            result = await session.execute(query)
            places = result.all()

            if not places:
                raise HTTPException(status_code=404, detail="404 No places found within the specified radius")

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
                    "properties": {
                        key: value for key, value in place_data.items() if key not in ["latitude", "longitude"]
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    }
                })

            total_count_result = await session.execute(select(func.count()).select_from(Place001))
            total_count = total_count_result.scalar()

            return StandardResponse(
                status="success",
                message="Data retrieved successfully",
                data=features,
                metadata={
                    "total_count": total_count,
                    "limit": limit,
                    "offset": offset,
                    "radius": radius
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
    __tablename__ = "places_h3_lv6"
    id = Column(Integer, primary_key=True, index=True)
    h3_index = Column(String(255), index=True)
    point_count = Column(Integer)
    geometry = Column(Text)  

class StandardResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any] = None
    metadata: Optional[dict] = None 

@app.get("/api/v1/pgDBs/places/th/hexagon", status_code=200, response_model=StandardResponse, tags=["postgres"])
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
@app.get("/api/v1/pgDBs/export_geojson", status_code=200, response_model=StandardResponse, tags=["postgres"])
async def export_geojson(background_tasks: BackgroundTasks ,credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Endpoint เป็นการอ่านข้อมูลฝนตาราง **places_th** จากนั้นทำการบันทึกเป็ฯไฟล์ **Geojson** """
    
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
    async with SessionLocal() as session:
        result = await session.execute(
            select(
                Place001.id,
                Place001.fsq_place_id,
                Place001.name,
                Place001.address,
                Place001.latitude,
                Place001.longitude,
                Place001.region,
                Place001.country,
                Place001.geometry
            )
        )
        places = result.all()

        features = []
        for place in places:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": place.id,
                    "fsq_place_id": place.fsq_place_id,
                    "name": place.name,
                    "address": place.address,
                    "region": place.region,
                    "country": place.country
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(place.longitude), float(place.latitude)]
                }
            })

        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }

        async def save_to_file():
            async with aiofiles.open("places.geojson", "w", encoding="utf-8") as f:
                await f.write(json.dumps(geojson_data, indent=2, ensure_ascii=False))
        background_tasks.add_task(save_to_file)
    return {"status": "success", "message": "GeoJSON export started in background"}






# ---------------------------------------------
##
###
#### ดึงข้อมูลจากฐานข้อมูลมา เเล้วบันทึกเป็นไฟล์ geojson  เเลวนำไฟลืนั้นมาทำ H3 level 6 เเล้วส่งกลับไปยัง places_h3_lv6
GEOJSON_FILE_PATH = r"C:\Users\Areeya Bunma\Desktop\pandas\FastAPI\places.geojson"

@app.get("/api/v1/pgDBs/places/th/imhexagon", status_code=200, response_model=StandardResponse, tags=["postgres"])
async def convert_geojson_to_h3(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Endpoint เป็นการอ่านข้อมูลในไฟล์ **Geojson** เเล้วเเปลงเป็ฯ **H3** **level** **6** จากนั้นบันทึกลงตาราง **places_h3_lv6**"""
    
    token = credentials.credentials  
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Error 401 Invalid token.")
    token_data = tokens[token]
    if datetime.utcnow() > token_data["expiration_time"]:
        del tokens[token]
        raise HTTPException(status_code=401, detail="Error 401 Token has expired.")
    
    try:
        async with aiofiles.open(GEOJSON_FILE_PATH, mode="r", encoding="utf-8") as f:
            geojson_str = await f.read()
        geojson_data = json.loads(geojson_str)
        features = geojson_data.get("features", [])
        h3_counts = {}
        for feature in features:
            geometry = feature.get("geometry")
            if not geometry or geometry.get("type") != "Point":
                continue  
            coordinates = geometry.get("coordinates")
            if not coordinates or len(coordinates) != 2:
                continue 
            lon, lat = coordinates
            if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
                continue
            if lon == 0 and lat == 0:
                continue 
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                continue 
            try:
                h3_index = h3.geo_to_h3(lat, lon, 6)
                if h3_index in h3_counts:
                    h3_counts[h3_index] += 1
                else:
                    h3_counts[h3_index] = 1
            except Exception as e:
                print(f"Skipping invalid H3 conversion: {coordinates}, Error: {e}")
        async with SessionLocal() as session:
            async with session.begin():
                for h3_index, count in h3_counts.items():
                    polygon_coords = h3.h3_to_geo_boundary(h3_index, geo_json=True)
                    polygon_wkt = f"POLYGON(({','.join(f'{lon} {lat}' for lon, lat in polygon_coords)}))"
                    insert_query = text("""
                        INSERT INTO places_h3_lv6 (h3_index, point_count, geometry)
                        VALUES (:h3_index, :point_count, ST_GeomFromText(:geometry, 4326))
                    """)
                    await session.execute(insert_query, {
                        "h3_index": h3_index,
                        "point_count": count,
                        "geometry": polygon_wkt
                    })
        h3_features = []
        for h3_index, count in h3_counts.items():
            polygon_coords = h3.h3_to_geo_boundary(h3_index, geo_json=True)
            h3_features.append({
                "type": "Feature",
                "properties": {
                    "h3_index": h3_index,
                    "point_count": count
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_coords]
                }
            })
        result_geojson = {
            "type": "FeatureCollection",
            "features": h3_features
        }
        metadata = {
            "total_H3": len(h3_features)
        }
        return {
            "status": "success",
            "message": "Data converted to H3 and saved to database successfully",
            "data": result_geojson,
            "metadata": metadata
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to process data: {str(e)}"}





















# ---------------------------------------------
##
###
#### ทำได้เเต่รูปมันหมุนผิด
# class PlacesH3(Base):
#     __tablename__ = 'places_h3_v1'

#     id = Column(Integer, primary_key=True, index=True)
#     h3_index = Column(String, nullable=False)
#     point_count = Column(Integer)
#     geometry = Column(Geometry('POLYGON', srid=4326))

# def get_h3_index(latitude, longitude, resolution=6):
#     """
#     แปลงพิกัด latitude และ longitude เป็น H3 index.
#     """
#     if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
#         raise ValueError(f"Invalid coordinates: {latitude}, {longitude}")

#     return h3.geo_to_h3(latitude, longitude, resolution)

# @app.post("/api/v1/pgDBs/places/th/hexagon_v1", response_model=StandardResponse, status_code=200, tags=["error"])
# async def convert_parquet_to_h3():
#     """
#     API reads data from Parquet files and converts the region data into H3 format.
#     """
#     parquet_files = [
#         "D:/parge/in_parge/places-00000.snappy.parquet"
#     ]

#     try:
#         data_frames = [pd.read_parquet(file) for file in parquet_files]
#         df = pd.concat(data_frames, ignore_index=True)
        
#         df = df[df['country'] == 'TH']
#         df = df[(df['latitude'] != 0) & (df['longitude'] != 0)]
#         df = df[(df['latitude'].between(-90, 90)) & (df['longitude'].between(-180, 180))]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error loading Parquet files: {str(e)}")

#     h3_counts = {}

#     async with SessionLocal() as session:
#         try:
#             for index, row in df.iterrows():
#                 latitude = row.get('latitude')
#                 longitude = row.get('longitude')

#                 if isinstance(latitude, (int, float)) and isinstance(longitude, (int, float)):
#                     try:
#                         h3_index = get_h3_index(latitude, longitude, 6)
                        
#                         if h3_index in h3_counts:
#                             h3_counts[h3_index] += 1
#                         else:
#                             h3_counts[h3_index] = 1
#                     except ValueError as e:
#                         print(f"Skipping invalid coordinates: {latitude}, {longitude} - Error: {e}")
#                 else:
#                     print(f"Skipping row with invalid coordinates: {row}")

#             for h3_index, count in h3_counts.items():
#                 polygon_coords = h3.h3_to_geo_boundary(h3_index, geo_json=True)
#                 geometry = f"SRID=4326;POLYGON(({', '.join([f'{lon} {lat}' for lat, lon in polygon_coords])}))"


#                 new_place_h3 = PlacesH3(
#                     h3_index=h3_index,
#                     point_count=count,
#                     geometry=geometry
#                 )
#                 session.add(new_place_h3)
            
#             await session.commit()

#             return {
#                 "status": "success",
#                 "message": "Data converted to H3 and saved successfully",
#                 "total_h3_indexes": len(h3_counts)
#             }

#         except Exception as e:
#             await session.rollback()
#             raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")






# @app.get("/api/v1/pgDBs/places/th/hexagon_v3", response_model=StandardResponse, status_code=200, tags=["error"])
# async def convert_geojson_to_h3():
#     """
#     API region fetches data from the **PostgreSQL** service and converts the region data into **H3** format.
#     The processed H3 data is saved into the `places_h3_v3` table.
#     """
#     response = requests.get("http://192.168.10.166:8000/api/v1/pgdbs/places/th?limit=1")
    
#     geojson_data = response.json()
#     if geojson_data.get("status") != "success":
#         return {"status": "error", "message": "Failed to fetch data"}
    
#     features = geojson_data["data"]["features"]
#     h3_counts = {}

#     for feature in features:
#         geometry = feature.get("geometry")
#         if geometry and geometry.get("type") == "Point":
#             coordinates = geometry.get("coordinates")
#             if coordinates and len(coordinates) == 2:
#                 lon, lat = coordinates
#                 if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
#                     h3_index = h3.geo_to_h3(lat, lon, 6)
#                     if h3_index in h3_counts:
#                         h3_counts[h3_index] += 1
#                     else:
#                         h3_counts[h3_index] = 1
#                 else:
#                     print(f"Skipping invalid coordinates: {coordinates}")
#             else:
#                 print(f"Skipping malformed coordinates: {coordinates}")
#         else:
#             print(f"Skipping feature with invalid geometry: {geometry}")
    
#     async with SessionLocal() as session:
#         async with session.begin():
#             for h3_index, count in h3_counts.items():
#                 polygon_coords = h3.h3_to_geo_boundary(h3_index, geo_json=True)
#                 polygon_wkt = f"POLYGON(({','.join(f'{lon} {lat}' for lon, lat in polygon_coords)}))"
#                 insert_query = text("""
#                     INSERT INTO places_h3_v3 (h3_index, point_count, geometry)
#                     VALUES (:h3_index, :point_count, ST_GeomFromText(:geometry, 4326))
#                 """)
#                 await session.execute(insert_query, {
#                     "h3_index": h3_index,
#                     "point_count": count,
#                     "geometry": polygon_wkt
#                 })
    
#     h3_features = []
#     for h3_index, count in h3_counts.items():
#         polygon_coords = h3.h3_to_geo_boundary(h3_index, geo_json=True)
#         h3_features.append({
#             "type": "Feature",
#             "properties": {
#                 "h3_index": h3_index,
#                 "point_count": count
#             },
#             "geometry": {
#                 "type": "Polygon",
#                 "coordinates": [polygon_coords]
#             }
#         })
    
#     result_geojson = {
#         "type": "FeatureCollection",
#         "features": h3_features
#     }
#     metadata = {
#         "total_H3": len(h3_features)
#     }
    
#     return {
#         "status": "success",
#         "message": "Data converted to H3 and saved to database successfully",
#         "data": result_geojson,
#         "metadata": metadata
#     }
























# from fastapi import FastAPI, HTTPException
# from sqlalchemy import create_engine, Column, Integer, String
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.dialects.postgresql import insert
# from geoalchemy2 import Geometry
# import pyarrow.parquet as pq
# import h3
# from shapely.geometry import Polygon


# class PlacessH3(Base):
#     __tablename__ = 'places_h3_v2'

#     id = Column(Integer, primary_key=True, index=True)
#     h3_index = Column(String, nullable=False, unique=True)
#     point_count = Column(Integer, default=0)
#     geometry = Column(Geometry('POLYGON', srid=4326))


# @app.post("/api/v1/pgDBs/places/th/hexagon_v2", status_code=201)
# def calculate_h3_and_save():
#     """
#     API สำหรับคำนวณ H3 ระดับ 6 จากไฟล์ Parquet และบันทึกลงฐานข้อมูล PostgreSQL
#     """
#     try:
#         file_path = "D:/parge/in_parge/places-00000.snappy.parquet"
#         table = pq.read_table(file_path)
#         df = table.to_pandas()

#         if 'latitude' not in df.columns or 'longitude' not in df.columns:
#             raise HTTPException(status_code=400, detail="Parquet file must contain 'latitude' and 'longitude' columns")

#         h3_counts = {}

#         for _, row in df.iterrows():
#             lat = row['latitude']
#             lon = row['longitude']

#             if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
#                 h3_index = h3.geo_to_h3(lat, lon, 6)
#                 if h3_index in h3_counts:
#                     h3_counts[h3_index] += 1
#                 else:
#                     h3_counts[h3_index] = 1

#         db = SessionLocal()
#         try:
#             for h3_index, count in h3_counts.items():
#                 boundary = h3.h3_to_geo_boundary(h3_index, geo_json=True)
#                 polygon = Polygon(boundary)
#                 record = {
#                     "h3_index": h3_index,
#                     "point_count": count,
#                     "geometry": f'SRID=4326;{polygon.wkt}'
#                 }

#                 stmt = insert(PlacessH3).values(record).on_conflict_do_update(
#                     index_elements=['h3_index'],
#                     set_={"point_count": count, "geometry": f'SRID=4326;{polygon.wkt}'}
#                 )
#                 db.execute(stmt)

#             db.commit()
#         finally:
#             db.close()

#         return {"status": "success", "message": "Data saved to places_h3_v2 successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))









# class PlacesH3(Base):
#     __tablename__ = 'places_h3'

#     id = Column(Integer, primary_key=True, index=True)
#     h3_index = Column(String, nullable=False)
#     point_count = Column(Integer)
#     geometry = Column(Geometry('POLYGON', srid=4326))

# def get_h3_index(latitude, longitude, resolution=6):
#     return h3.geo_to_h3(latitude, longitude, resolution)

# @app.post("/api/v1/pgDBs/places/th/hexagon", tags=["error"])
# async def convert_geojson_to_h3():
#     """
#     API fetches data from the **PostgreSQL** database and converts the region data into **H3** format.
#     After calculation, it stores the result in the `places_h3` table.
#     """
    
#     response = requests.get("http://192.168.10.166:8000/api/v1/pgdbs/places/th?limit=1000")
#     geojson_data = response.json()
    
#     if geojson_data.get("status") != "success":
#         raise HTTPException(status_code=400, detail="Failed to fetch data")
    
#     features = geojson_data["data"]["features"]
#     h3_counts = {}

#     async with SessionLocal() as session:
#         try:
#             for feature in features:
#                 geometry = feature.get("geometry")
#                 if geometry and geometry.get("type") == "Point":
#                     coordinates = geometry.get("coordinates")
#                     if coordinates and len(coordinates) == 2:
#                         lon, lat = coordinates
#                         if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
#                             h3_index = get_h3_index(lat, lon, 6)
#                             if h3_index in h3_counts:
#                                 h3_counts[h3_index] += 1
#                             else:
#                                 h3_counts[h3_index] = 1
#                         else:
#                             print(f"Skipping invalid coordinates: {coordinates}")
#                     else:
#                         print(f"Skipping malformed coordinates: {coordinates}")
#                 else:
#                     print(f"Skipping feature with invalid geometry: {geometry}")

#             for h3_index, count in h3_counts.items():
#                 polygon_coords = h3.h3_to_geo_boundary(h3_index, geo_json=True)
#                 geometry = f'SRID=4326;POLYGON(({", ".join([f"{lon} {lat}" for lat, lon in polygon_coords])}))'

#                 new_place_h3 = PlacesH3(
#                     h3_index=h3_index,
#                     point_count=count,
#                     geometry=geometry
#                 )
#                 session.add(new_place_h3)
            
#             await session.commit()
#             return {
#                 "status": "success",
#                 "message": "Data converted to H3 and saved successfully",
#                 "total_h3_indexes": len(h3_counts)
#             }
#         except Exception as e:
#             await session.rollback()
#             raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")










# from fastapi import FastAPI, HTTPException
# from sqlalchemy import create_engine, select
# from sqlalchemy.orm import sessionmaker
# from geoalchemy2 import Geometry
# from geoalchemy2.functions import ST_AsText
# import h3
# from sqlalchemy import Column, Integer, String, Float
# from geoalchemy2 import Geometry
# from sqlalchemy.ext.declarative import declarative_base
# from fastapi import FastAPI, HTTPException
# from sqlalchemy import create_engine, select
# from sqlalchemy.orm import sessionmaker, declarative_base
# from geoalchemy2 import Geometry
# import h3
# from sqlalchemy import Column, Integer, String, Float

# SessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )
# async def get_places():
#     async with SessionLocal() as session:
#         result = await session.execute(select(PlacesTH))
#         places = result.scalars().all()
#         return places


# class PlacesTH(Base):
#     __tablename__ = 'places_th'

#     id = Column(Integer, primary_key=True, index=True)
#     fsq_place_id = Column(String, unique=True, nullable=False)
#     name = Column(String, nullable=False)
#     latitude = Column(Float)
#     longitude = Column(Float)
#     address = Column(String)
#     locality = Column(String)
#     region = Column(String)
#     country = Column(String, nullable=False)
#     date_created = Column(String)
#     date_refreshed = Column(String)
#     date_closed = Column(String)
#     geometry = Column(Geometry('POINT', srid=4326))

# class PlacesH3(Base):
#     __tablename__ = 'places_h3'

#     id = Column(Integer, primary_key=True, index=True)
#     h3_index = Column(String, nullable=False)
#     point_count = Column(Integer)
#     geometry = Column(Geometry('POINT', srid=4326))

# def get_h3_index(latitude, longitude, resolution=6):
#     return h3.geo_to_h3(latitude, longitude, resolution)


# @app.post("/api/v1/pgdbs/places/th/hexagon")
# async def create_h3_hexagon():
#     async with SessionLocal() as session:
#         try:
#             result = await session.execute(select(PlacesTH))
#             places = result.scalars().all()

#             for place in places:
#                 latitude = place.latitude
#                 longitude = place.longitude

#                 # Validate if latitude and longitude are valid
#                 if latitude is None or longitude is None or not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
#                     continue  # Skip invalid data

#                 h3_index = get_h3_index(latitude, longitude, 6)
#                 geometry = f'SRID=4326;POINT({longitude} {latitude})'

#                 new_place_h3 = PlacesH3(
#                     h3_index=h3_index,
#                     point_count=1,
#                     geometry=geometry
#                 )

#                 session.add(new_place_h3)
#             await session.commit()

#             return {"message": "H3 hexagons created successfully."}

#         except Exception as e:
#             await session.rollback()
#             raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")


























#------------------------------------------
##
###
#conn duckDBs
# เอาเข้าทั้งหมด ไม่ได้กรอง  TH 
# /api/v1/duckDBs/places/02?limit=1000&offset=0   #ดึงตั้งเเต่ตัว 0 ไปจนครบ 1000
# /api/v1/duckDBs/places/02?limit=1000&offset=1000   #ดึงตั้งเเต่ตัวที่ 1000 ไปจนครบ 1000  อยากเริ่มตัวไหน ให้ปรับตัว offset=

#กรองเเค่ TH เเบไม่ลิมิต
# @app.get("/api/v1/duckDBs/places/th/unlimit", response_model=StandardResponse, status_code=200, tags=["duckDBs"])
# async def get_data_in_duckdbs_unlimit():
#     """
#     Endpoint to fetch all data from DuckDB table 'places_th' (filtered by country='TH').
#     Returns all rows from the table without pagination. Unlimit data.
#     """
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"""
#             CREATE TABLE IF NOT EXISTS places_th AS
#             SELECT fsq_place_id, name, latitude, longitude, address, locality, region, country,
#                    date_created, date_refreshed, date_closed, fsq_category_ids, fsq_category_labels
#             FROM read_parquet('{file_path}')
#             WHERE country = 'TH'
#         """)
#         query = "SELECT * FROM places_th"
#         result = con.execute(query).fetchall()
#         count_query = "SELECT COUNT(*) FROM places_th"
#         row_count = con.execute(count_query).fetchone()[0]
#         con.close()
#         return create_response(
#             status="success",
#             message="All data fetched successfully",
#             data=result,
#             metadata={"row_count": len(result), "Total_all_data": row_count}
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}",
#         )




# # เเก้ไขการตอบกลับ ให้มีฟิลมาด้วย
# @app.get("/api/v1/duckDBs/places/th/limit", response_model=StandardResponse, status_code=200, tags=["duckDBs"])
# async def get_data_in_duckdbs_limit(
#     limit: int = Query(default=1000, ge=1),
#     offset: int = Query(default=0, ge=0)
# ):
#     """
#     Endpoint to fetch data from DuckDB table 'places_th' (filtered by country='TH') with pagination.
#     Returns JSON objects with field names as keys. Limit data.
#     - **?limit=1000&offset=0**  #ดึงตั้งเเต่ตัว 0 ไปจนครบ 1000
#     - **?limit=1000&offset=1000**  #ดึงตั้งเเต่ตัวที่ 1000 ไปจนครบ 1000  อยากเริ่มตัวไหน ให้ปรับตัว offset=
#     """
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"""
#             CREATE TABLE IF NOT EXISTS places_th AS
#             SELECT fsq_place_id, name, latitude, longitude, address, locality, region, country,
#                    date_created, date_refreshed, date_closed, fsq_category_ids, fsq_category_labels
#             FROM read_parquet('{file_path}')
#             WHERE country = 'TH'
#         """)
#         query = f"SELECT * FROM places_th LIMIT {limit} OFFSET {offset}"
#         rows = con.execute(query).fetchall()
#         column_headers = [desc[0] for desc in con.description]
#         result = [dict(zip(column_headers, row)) for row in rows]
#         total_rows = con.execute("SELECT COUNT(*) FROM places_th").fetchone()[0]
#         con.close()
#         return {
#             "status": "success",
#             "message": "Data fetched successfully",
#             "data": result,
#             "metadata": {
#                 "row_count": len(result),
#                 "total_all_data": total_rows,
#                 "limit": limit,
#                 "offset": offset,
#             }
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}",
#         )


#---------------------------------
##
###
#ทำ h3 level 8
#ทำจาก geojson
# @app.get("/api/v1/duckDBs/places/h3/regions", response_model=StandardResponse, status_code=200, tags=["H3"])
# async def get_data_in_h3_lv12(
#     limit: int = Query(default=100, ge=1),
#     offset: int = Query(default=0),
#     region: Optional[str] = Query(default=None, description="Filter by region (e.g., 'Bangkok')")
# ):
#     """
#     API to fetch data from 'in_h3_lv12' GeoJSON file.
#     - **limit**: Number of records to fetch (default: 100).
#     - **offset**: Pagination offset (default: 0).
#     - **region**: Optional region filter.
#     """
#     file_path = r"D:\parge\in_h3_lv12\data_test_004.geojson"
#     try:
#         with open(file_path, "r", encoding="utf-8") as file:
#             geojson_data = json.load(file)
#         features = geojson_data["features"]
#         if region:
#             features = [
#                 feature for feature in features
#                 if feature["properties"].get("region") == region
#             ]
#         paginated_features = features[offset:offset + limit]
#         response_geojson = {
#             "type": "FeatureCollection",
#             "features": paginated_features
#         }
#         metadata = {
#             "row_count": len(paginated_features),
#             "next_offset": offset + len(paginated_features),
#             "total_records": len(features)
#         }
#         return StandardResponse(
#             status="success",
#             message="Data fetched successfully as GeoJSON",
#             data=response_geojson,
#             metadata=metadata
#         )
#     except FileNotFoundError:
#         raise HTTPException(
#             status_code=404,
#             detail="GeoJSON file not found"
#         )
#     except json.JSONDecodeError:
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to parse GeoJSON file"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"An unexpected error occurred: {str(e)}"
#         )
    











# ---------------------------------------
# ---------------------------------------















# ขนาดไฟล์ 3 gb ใช่เวลา 5-6 น.
# @app.get("/api/v1/accidents/download-geojson-zip", status_code=200, response_model=StandardResponse, tags=["data"])
# async def download_all_geojson():
#     """This endpoint will extract the GeoJSON data from the files `heatmap-rvp-death.geojson`. 
#     and `accident_grids_itic_dbscan_2022_2020.geojson`. 
#     and compress them into a `.ZIP` for download."""
#     zip_path = "C:/Users/Areeya Bunma/Desktop/pandas/acc/geojson_files.zip"
#     try:

#         with ZipFile(zip_path, "w") as zipf:
#             zipf.write("C:/Users/Areeya Bunma/Desktop/pandas/acc/heatmap-rvp-death.geojson", "heatmap-rvp-death.geojson")
#             zipf.write("C:/Users/Areeya Bunma/Desktop/pandas/acc/accident_grids_itic_dbscan_2022_2020.geojson", "accident_grids.geojson")
        
#         return FileResponse(zip_path, media_type="application/zip", filename="geojson_files.zip")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error creating zip file: {str(e)}")



# @app.get("/api/v1/image/44/download-images-zip", status_code=200, response_model=StandardResponse, tags=["image"]) 
# async def get_images_zip():
#     """This endpoint will extract the image data from the `image` folder and compress it into a `.ZIP` for download."""
#     image_paths = [
#         "C:/Users/Areeya Bunma/Desktop/image/44/0033.png",
#         "C:/Users/Areeya Bunma/Desktop/image/44/0011.jpg",
#         "C:/Users/Areeya Bunma/Desktop/image/44/0022.jpg"
#     ]
#     zip_file_path = "C:/Users/Areeya Bunma/Desktop/image/44/images.zip"
#     with ZipFile(zip_file_path, 'w') as zipf:
#         for image_path in image_paths:
#             if not os.path.exists(image_path):
#                 raise HTTPException(status_code=404, detail=f"Image not found: {image_path}")
#             zipf.write(image_path, os.path.basename(image_path))
#     return FileResponse(zip_file_path, media_type='application/zip', filename='images.zip')



# #http://192.168.10.166:8000/image/66/all-download-images-zip
# #ส่งรุปไปทั้งหมดในโฟลเดอร์
# @app.get("/api/v1/image/66/all-download-images-zip", status_code=200, response_model=StandardResponse, tags=["image"])
# async def get_all_images_zip():
#     """This endpoint will extract all image data from the `image` folder and compress it into a `.ZIP` for download."""
#     folder_path = "C:/Users/Areeya Bunma/Desktop/image/66/"
#     zip_file_path = "C:/Users/Areeya Bunma/Desktop/image/zip-images/images.zip"
#     if not os.path.exists(folder_path):
#         raise HTTPException(status_code=404, detail="Folder not found")
#     file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
#     if not file_paths:
#         raise HTTPException(status_code=404, detail="No files found in the folder")
#     with ZipFile(zip_file_path, 'w') as zipf:
#         for file_path in file_paths:
#             zipf.write(file_path, os.path.basename(file_path))
#     return FileResponse(zip_file_path, media_type='application/zip', filename='images.zip')



# @app.get("/api/v1/select/accidents/geojson-select", status_code=200, response_model=StandardResponse, tags=["select"]) 
# async def get_heatmap_data(file: str = Query(..., description="Name of the GeoJSON file")):
#     """This endpoint requires a manual selection of the final destination between `heatmap-rvp-death` and `accident-grids`. 
#     It includes metadata about the file, such as the total number of features. 
#     The file is processed and prepared to be returned in the GeoJSON format."""
#     file_map = {
#         "heatmap-rvp-death": "C:/Users/Areeya Bunma/Desktop/pandas/acc/heatmap-rvp-death.geojson",
#         "accident-grids": "C:/Users/Areeya Bunma/Desktop/pandas/acc/accident_grids_itic_dbscan_2022_2020.geojson",
#     }
    
#     if file not in file_map:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid file name. Available options: {list(file_map.keys())}"
#         )
    
#     file_path = file_map[file]
    
#     try:
#         geojson_data_select = load_geojson_file(file_path)
#         feature_grids = len(geojson_data_select.get("features", []))
#         return create_response(
#             status="success",
#             message="GeoJSON data retrieved successfully",
#             metadata={"file_name": file_path, "feature_count": feature_grids},
#             data=geojson_data_select
#         )
#     except FileNotFoundError:
#         raise HTTPException(
#             status_code=404,
#             detail=f"File not found at path: {file_path}"
#         )
#     except json.JSONDecodeError: #เมื่อไม่ได้ใส่ ?file=...
#         raise HTTPException(
#             status_code=422,
#             detail=f"Failed to parse the file: {file_path} as valid GeoJSON."
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}"
#         )
    

















# ---------------------------------------
# ---------------------------------------





















# #ทำจาd API
# @app.get("/api/v1/duckDBs/places/h3/APIregion")
# def convert_geojson_to_h3():
#     response = requests.get("http://192.168.10.166:8000/api/v1/duckDBs/places/th/region?limit=50000")
#     geojson_data = response.json()
#     if geojson_data["status"] != "success":
#         return {"status": "error", "message": "Failed to fetch data"} 
#     features = geojson_data["data"]["features"]
#     h3_counts = {}
#     for feature in features:
#         geometry = feature["geometry"]
#         if geometry["type"] == "Point":
#             lon, lat = geometry["coordinates"]
#             h3_index = h3.geo_to_h3(lat, lon, 6)
#             if h3_index in h3_counts:
#                 h3_counts[h3_index] += 1
#             else:
#                 h3_counts[h3_index] = 1
#     h3_features = []
#     for h3_index, count in h3_counts.items():
#         polygon_coords = h3.h3_to_geo_boundary(h3_index, geo_json=True)
#         h3_features.append({
#             "type": "Feature",
#             "properties": {
#                 "h3_index": h3_index,
#                 "point_count": count
#             },
#             "geometry": {
#                 "type": "Polygon",
#                 "coordinates": [polygon_coords]
#             }
#         })
#     result_geojson = {
#         "type": "FeatureCollection",
#         "features": h3_features
#     }
#     metadata = {
#             "total_H3": len(h3_features)
#     }
#     return {
#         "status": "success",
#         "message": "Data converted to H3 successfully",
#         "data": result_geojson,
#         "metadata":metadata
#     }






# @app.get("/api/v2/duckDBs/places/th/region", response_model=StandardResponse, status_code=200, tags=["duckDBs"])
# async def get_data_in_duckdbs_region(
#     # username: str = Depends(verify_token),
#     limit: int = Query(default=1000, ge=1),
#     offset: int = Query(default=0, ge=0),
#     region: str = Query(default=None, description="Filter by region (e.g., 'Bangkok')")
# ):
#     """
#     Endpoint to fetch data from DuckDB table 'places_th' in chunks as GeoJSON.
#     - **limit**: The number of records to return (default 1000)
#     - **offset**: The offset for pagination (default 0)
#     - **region**: Region filter (default None, fetches all regions)
#     """
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

#         # สร้าง next_url
#         base_url = "/api/v1/duckDBs/places/th/region"
#         next_offset = offset + limit
#         next_url = None
#         if next_offset:
#             next_url = f"{base_url}?limit={limit}&offset={next_offset}"
#             if region:
#                 next_url += f"&region={region}"

#         metadata = {
#             "row_count": len(features),
#             "next_offset": next_offset,
#             "total_all_data": row_count,
#             "next_url": next_url
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
#             detail=f"Unexpected error occurred: {str(e)}",
#         )







# geojson_file_path = r"C:\Users\Areeya Bunma\Desktop\pandas\ALL\th_filtered.geojson"
# def load_geojson():
#     try:
#         with open(geojson_file_path, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return None
# geojson_data1 = load_geojson()

# @app.get("/api/v1/accidents/th-geojson", status_code=200, tags=["data"])
# async def get_accidents():
#     """This endpoint retrieves the GeoJSON data from the file """
#     if geojson_data1 is None:
#         return JSONResponse(
#             status_code=404,
#             content={
#                 "status": "error",  
#                 "message": "GeoJSON file 'th.geojson' not found."
#             }
#         )
#     feature_count = len(geojson_data1.get("features", []))
#     return JSONResponse(
#         status_code=200,
#         content={
#             "status": "success",  
#             "message": "GeoJSON data retrieved successfully.",
#             "data": geojson_data1,
#             "metadata": {
#                 "file_name": "th.geojson",
#                 "feature_count": feature_count
#             }
#         }
#     )









# @app.get("/api/v1/duckDBs/places/h3/save_and_load", status_code=200, tags=["duckDBs"])
# def save_and_load_h3_data():
#     try:
#         # ดึงข้อมูลจาก API
#         response = requests.get("http://192.168.10.166:8000/api/v1/duckDBs/places/h3/APIregion")
#         if response.status_code != 200 or response.json()["status"] != "success":
#             raise HTTPException(status_code=500, detail="Failed to fetch H3 data")

#         # ข้อมูล GeoJSON
#         geojson_data = response.json()["data"]

#         # บันทึกไฟล์ GeoJSON
#         file_path = r"D:\data\h3\H3_api.geojson"
#         with open(file_path, "w", encoding="utf-8") as f:
#             import json
#             json.dump(geojson_data, f, ensure_ascii=False, indent=4)

#         # โหลดข้อมูลจากไฟล์เพื่อแสดงผล
#         with open(file_path, "r", encoding="utf-8") as f:
#             loaded_data = json.load(f)
        
#         return {
#             "status": "success",
#             "message": "H3 data saved and loaded successfully",
#             "data": loaded_data,
            
#         }
#     except FileNotFoundError:
#         raise HTTPException(
#             status_code=404,
#             detail="GeoJSON file not found. Please ensure the save operation completed."
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}"
#         )













# # Path to the shapefile and DuckDB database
# shapefile_path = r"D:\data\Area_TH\Area_TH.shp"
# duckdb_path = r"D:\data\Area_TH\area_th.duckdb"

# # Load Shapefile into DuckDB
# def load_shapefile_to_duckdb():
#     try:
#         # Read the shapefile
#         gdf = gpd.read_file(shapefile_path)

#         # Connect to DuckDB and create table
#         con = duckdb.connect(duckdb_path)
#         con.execute("CREATE TABLE IF NOT EXISTS area_th AS SELECT * FROM gdf")
#         con.close()
#         print("Shapefile loaded into DuckDB successfully!")
#     except Exception as e:
#         print(f"Error loading shapefile into DuckDB: {e}")

# # API to fetch data
# @app.get("/api/v1/duckDBs/places/th/area", response_model=StandardResponse, status_code=200, tags=["duckDBs"])
# async def get_data_in_duckdbs_region(
#     limit: int = Query(default=100, ge=1),
#     offset: int = Query(default=0, ge=0),
#     region: Optional[str] = Query(default=None, description="Filter by region (e.g., 'Bangkok')")
# ):
#     """
#     Endpoint to fetch data from DuckDB table 'area_th' as GeoJSON.
#     - **limit**: Number of records to fetch.
#     - **offset**: Offset for pagination.
#     - **region**: Filter by ADM1_EN or ADM1_TH.
#     """
#     try:
#         # Connect to DuckDB
#         con = duckdb.connect(duckdb_path)

#         # Filter by region if provided
#         region_filter = f"WHERE ADM1_EN = '{region}' OR ADM1_TH = '{region}'" if region else ""
#         query = f"""
#             SELECT Shape_leng, Shape_Area, ADM1_EN, ADM1_TH, ADM1_PCODE, ADM0_EN, ADM0_TH, geometry
#             FROM area_th
#             {region_filter}
#             LIMIT {limit} OFFSET {offset}
#         """
#         rows = con.execute(query).fetchall()
#         column_headers = [desc[0] for desc in con.description]

#         # Convert rows to GeoJSON
#         features = []
#         for row in rows:
#             data = dict(zip(column_headers, row))
#             features.append({
#                 "type": "Feature",
#                 "properties": {
#                     key: value for key, value in data.items() if key != "geometry"
#                 },
#                 "geometry": data["geometry"]
#             })

#         # Get row count for metadata
#         count_query = f"SELECT COUNT(*) FROM area_th {region_filter}"
#         row_count = con.execute(count_query).fetchone()[0]
#         con.close()

#         # Build GeoJSON response
#         geojson = {
#             "type": "FeatureCollection",
#             "features": features
#         }
#         metadata = {
#             "row_count": len(features),
#             "next_offset": offset + limit,
#             "total_records": row_count
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
#             detail=f"Unexpected error occurred: {str(e)}",
#         )

# # Load the shapefile into DuckDB when the script is run
# load_shapefile_to_duckdb()




#เเชทบอกว่าช่วยให้เร็วขึ้น เเต่ลองเเล้วก้ปกติ
# @app.get("/api/v1/duckDBs/places/h3/A001")
# async def convert_geojson_to_h3():
#     async with aiohttp.ClientSession() as session:
#         async with session.get("http://192.168.10.166:8000/api/v1/duckDBs/places/th/region?region=Bangkok&limit=1000") as response:
#             geojson_data = await response.json()
    
#     if geojson_data["status"] != "success":
#         return {"status": "error", "message": "Failed to fetch data"} 

#     features = geojson_data["data"]["features"]
#     h3_counts = {}

#     async def process_feature(feature):
#         geometry = feature["geometry"]
#         if geometry["type"] == "Point":
#             lon, lat = geometry["coordinates"]
#             h3_index = h3.geo_to_h3(lat, lon, 6)
#             if h3_index in h3_counts:
#                 h3_counts[h3_index] += 1
#             else:
#                 h3_counts[h3_index] = 1

#     tasks = [process_feature(feature) for feature in features]
#     await asyncio.gather(*tasks)

#     h3_features = []
#     for h3_index, count in h3_counts.items():
#         polygon_coords = h3.h3_to_geo_boundary(h3_index, geo_json=True)
#         h3_features.append({
#             "type": "Feature",
#             "properties": {
#                 "h3_index": h3_index,
#                 "point_count": count
#             },
#             "geometry": {
#                 "type": "Polygon",
#                 "coordinates": [polygon_coords]
#             }
#         })
#     result_geojson = {
#         "type": "FeatureCollection",
#         "features": h3_features
#     }
#     return {
#         "status": "success",
#         "message": "Data converted to H3 successfully",
#         "data": result_geojson
#     }














# #ตอบกลับเเบบ geojson
# @app.get("/api/v1/duckDBs/places/th/geojson1", response_model=StandardResponse, status_code=200, tags=["duckDBs"])
# async def get_data_in_duckdbs_geojson(
#     limit: int = Query(default=1000, ge=1),  
#     offset: int = Query(default=0, ge=0)    
# ):
#     """
#     Endpoint to fetch data from DuckDB table 'places_th' in chunks as GeoJSON.
#     - **?limit=1000&offset=0**   #ดึงตั้งเเต่ตัว 0 ไปจนครบ 1000
#     - **?limit=1000&offset=1000**  #ดึงตั้งเเต่ตัวที่ 1000 ไปจนครบ 1000  อยากเริ่มตัวไหน ให้ปรับตัว offset=
#     """
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"""
#             CREATE TABLE IF NOT EXISTS places_th AS
#             SELECT fsq_place_id, name, latitude, longitude, address, locality, region, country,
#                    date_created, date_refreshed, date_closed
#             FROM read_parquet('{file_path}')
#             WHERE country = 'TH'
#         """)
#         query = f"SELECT * FROM places_th LIMIT {limit} OFFSET {offset}"
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
#         count_query = "SELECT COUNT(*) FROM places_th"
#         row_count = con.execute(count_query).fetchone()[0]
#         con.close()
#         return create_response(
#             status="success",
#             message="Data fetched successfully as GeoJSON",
#             data=geojson,
#             metadata={ 
#                 "row_count": len(features),
#                 "next_offset": offset + limit,
#                 "Total_all_data": row_count
#             },
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}",
#         )



# @app.get("/api/v1/duckDBs/places/th/geon2", response_model=StandardResponse, status_code=200, tags=["duckDBs"])
# async def get_data_in_duckdbs_geon2(
#     limit: int = Query(default=1000, ge=1),  
#     offset: int = Query(default=0, ge=0)    
# ):
#     """
#     Endpoint to fetch data from DuckDB table 'places_th' in chunks as GeoJSON.
#     - **limit**: The number of records to return (default 1000)
#     - **offset**: The offset for pagination (default 0)
#     """
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"""
#             CREATE TABLE IF NOT EXISTS places_th AS
#             SELECT fsq_place_id, name, latitude, longitude, address, locality, region, country,
#                    date_created, date_refreshed, date_closed
#             FROM read_parquet('{file_path}')
#             WHERE country = 'TH'
#         """)
#         query = f"SELECT * FROM places_th LIMIT {limit} OFFSET {offset}"
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
#         count_query = "SELECT COUNT(*) FROM places_th"
#         row_count = con.execute(count_query).fetchone()[0]
#         con.close()
#         metadata = {
#             "row_count": len(features),
#             "next_offset": offset + limit,
#             "Total_all_data": row_count
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
#             detail=f"Unexpected error occurred: {str(e)}",
#         )


# @app.get("/api/v1/duckDBs/places/th/geon3", response_model=StandardResponse, status_code=200, tags=["duckDBs"])
# async def get_data_in_duckdbs_geon3(
#     limit: int = Query(default=1000, ge=1),  
#     offset: int = Query(default=0, ge=0)    
# ):
#     """
#     Endpoint to fetch data from DuckDB table 'places_th' in chunks as GeoJSON.
#     - **limit**: The number of records to return (default 1000)
#     - **offset**: The offset for pagination (default 0)
#     """
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"""
#             CREATE TABLE IF NOT EXISTS places_th AS
#             SELECT fsq_place_id, name, latitude, longitude, address, locality, region, country,
#                    date_created, date_refreshed, date_closed
#             FROM read_parquet('{file_path}')
#             WHERE country = 'TH'
#         """)
#         # Add filtering for 'region = Bangkok'
#         query = f"""
#             SELECT * FROM places_th
#             WHERE region = 'Bangkok'
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
#         count_query = "SELECT COUNT(*) FROM places_th WHERE region = 'Bangkok'"
#         row_count = con.execute(count_query).fetchone()[0]
#         con.close()
#         metadata = {
#             "row_count": len(features),
#             "next_offset": offset + limit,
#             "Total_all_data": row_count
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
#             detail=f"Unexpected error occurred: {str(e)}",
#         )







# def create_response(
#     status: str = "success",
#     message: str = "Request completed successfully",
#     data: Any = None,
#     metadata: Optional[dict] = None
# ) -> JSONResponse:
#     return JSONResponse(
#         content={
#             "status": status,
#             "message": message,
#             "data": data,
#             "metadata": metadata,
#         }
#     )



# @app.get("/api/v1/github/accident/heatmap-rvp", status_code=200, response_model=StandardResponse, tags=["github"])
# async def geojson_from_github_heatmap_rvp(limit: int = Query(default=None, ge=1)):
#     """Endpoint to fetch GeoJSON data from GITHUB `heatmap-rvp.geojson`, 
#     it will include metadata about the file, mean total number to be awarded and prepare to return in GeoJSON."""
#     github_url = "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/heatmap-rvp.geojson" 

#     try:
#         response = requests.get(github_url)
#         response.raise_for_status()  
#         geojson_data = response.json()  
#         feature_grids = len(geojson_data.get("features", []))

#          # ตรวจสอบและจำกัดจำนวน features
#         features = geojson_data.get("features", [])
#         if limit:
#             features = features[:limit]

#         # สร้าง GeoJSON ใหม่สำหรับการตอบกลับ
#         limited_geojson = {**geojson_data, "features": features}

#         return create_response(
#             status="success",
#             message="GeoJSON file fetched successfully",
#             data=limited_geojson,
#             metadata={"source": github_url, "feature_count": feature_grids}
#         )
    
#     except requests.exceptions.HTTPError as http_err:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail=f"HTTP error occurred: {http_err}"
#         )
#     except requests.exceptions.RequestException as req_err:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Request error occurred: {req_err}"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}"
#         )



# @app.get("/api/v1/github/accident/itic-top200-all-road", status_code=200, response_model=StandardResponse, tags=["github"])
# async def geojson_from_github_itic_top200_raod(limit: int = Query(default=None, ge=1)):
#     """Endpoint to fetch GeoJSON data from GITHUB `itic-top200-all-road`, 
#     it will include metadata about the file, mean total number to be awarded and prepare to return in GeoJSON."""
#     github_url = "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/itic-top200-all-road.geojson" 

#     try:
#         response = requests.get(github_url)
#         response.raise_for_status()  
#         geojson_data = response.json()  
#         feature_grids = len(geojson_data.get("features", []))

#          # ตรวจสอบและจำกัดจำนวน features
#         features = geojson_data.get("features", [])
#         if limit:
#             features = features[:limit]

#         # สร้าง GeoJSON ใหม่สำหรับการตอบกลับ
#         limited_geojson = {**geojson_data, "features": features}

#         return create_response(
#             status="success",
#             message="GeoJSON file fetched successfully",
#             data=limited_geojson,
#             metadata={"source": github_url, "feature_count": feature_grids}
#         )
    
#     except requests.exceptions.HTTPError as http_err:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail=f"HTTP error occurred: {http_err}"
#         )
#     except requests.exceptions.RequestException as req_err:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Request error occurred: {req_err}"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}"
#         )




# @app.get("/api/v1/github/accident/heatmap-itic", status_code=200, response_model=StandardResponse, tags=["github"])
# async def geojson_from_github_heatmap_itic(limit: int = Query(default=None, ge=1)):
#     """Endpoint to fetch GeoJSON data from GITHUB `accident_grids_itic_dbscan_2022_2020.geojson`, 
#     it will include metadata about the file, mean total number to be awarded and prepare to return in GeoJSON."""
#     github_url = "https://raw.githubusercontent.com/chaloemphona/test-data/refs/heads/main/accident/heatmap-itic.geojson" 

#     try:
#         response = requests.get(github_url)
#         response.raise_for_status()  
#         geojson_data = response.json()  
#         feature_grids = len(geojson_data.get("features", []))

#          # ตรวจสอบและจำกัดจำนวน features
#         features = geojson_data.get("features", [])
#         if limit:
#             features = features[:limit]

#         # สร้าง GeoJSON ใหม่สำหรับการตอบกลับ
#         limited_geojson = {**geojson_data, "features": features}

#         return create_response(
#             status="success",
#             message="GeoJSON file fetched successfully",
#             data=limited_geojson,
#             metadata={"source": github_url, "feature_count": feature_grids}
#         )
    
#     except requests.exceptions.HTTPError as http_err:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail=f"HTTP error occurred: {http_err}"
#         )
#     except requests.exceptions.RequestException as req_err:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Request error occurred: {req_err}"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}"
#         )






# กรองเค่TH เเต่ลิมิต 1000
# @app.get("/api/v1/duckDBs/places/03", status_code=200, tags=["duckDBs"])
# async def get_data_in_duckdbs_lim_offset(
#     limit: int = Query(default=1000, ge=1),  
#     offset: int = Query(default=0, ge=0)    
# ):
#     """
#     Endpoint to fetch data from DuckDB table 'places_th' in chunks.
#     `/api/v1/duckDBs/places/02?limit=1000&offset=0`   Fetch from index 0 to 1000
#     `/api/v1/duckDBs/places/02?limit=1000&offset=1000` Fetch from index 1000 to 2000
#     Adjust `offset` to change the starting point of the query.
#     """
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"""
#             CREATE TABLE IF NOT EXISTS places_th AS
#             SELECT fsq_place_id, name, latitude, longitude, address, locality, region, country,
#                    date_created, date_refreshed, date_closed, fsq_category_ids, fsq_category_labels
#             FROM read_parquet('{file_path}')
#             WHERE country = 'TH'
#         """)
#         query = f"SELECT * FROM places_th LIMIT {limit} OFFSET {offset}"
#         result = con.execute(query).fetchall()
#         count_query = "SELECT COUNT(*) FROM places_th"
#         row_count = con.execute(count_query).fetchone()[0]
#         con.close()
#         return create_response(
#             status="success",
#             message="Data fetched successfully",
#             data=result,
#             metadata={"row_count": len(result), "next_offset": offset + limit, "Total_all_data": row_count}, 
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}",
#         )




# @app.get("/api/v1/duckDBs/places/02", status_code=200, response_model=StandardResponse, tags=["duckDBs"])
# async def get_data_in_duckdbs_lim_offset(
#     limit: int = Query(default=1000, ge=1), 
#     offset: int = Query(default=0, ge=0)  
# ):
#     """
#     Endpoint to fetch data from DuckDB table 'places_00000' in chunks.
#     `/api/v1/duckDBs/places/02?limit=1000&offset=0`   ดึงตั้งเเต่ตัว 0 ไปจนครบ 1000
#     `/api/v1/duckDBs/places/02?limit=1000&offset=1000`   ดึงตั้งเเต่ตัวที่ 1000 ไปจนครบ 1000  
#     อยากเริ่มตัวไหน ให้ปรับตัว offset=
#     """
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"CREATE TABLE IF NOT EXISTS places_00000 AS SELECT * FROM read_parquet('{file_path}')")
#         query = f"SELECT * FROM places_00000 LIMIT {limit} OFFSET {offset}"
#         result = con.execute(query).fetchall()
#         count_query = "SELECT COUNT(*) FROM places_00000"
#         row_count = con.execute(count_query).fetchone()[0]
#         con.close()
#         return create_response(
#             status="success",
#             message="Data fetched successfully",
#             data=result,
#             metadata={"row_count": len(result), "next_offset": offset + limit, "Total_all_data": row_count},
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}",
#         )




# @app.get("/api/v1/duckDBs/places/01", status_code=200, response_model=StandardResponse, tags=["duckDBs"])
# async def get_data_in_duckdbs(limit: int = Query(default=None, ge=1)):
#     """
#     Endpoint to fetch data from DuckDB table 'places_00000'.
#     """
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"CREATE TABLE IF NOT EXISTS places_00000 AS SELECT * FROM read_parquet('{file_path}')")
#         query = "SELECT * FROM places_00000"
#         if limit:
#             query += f" LIMIT {limit}"
#         result = con.execute(query).fetchall()
#         con.close()
#         return create_response(
#             status="success",
#             message="Data fetched successfully",
#             data=result,
#             metadata={"row_count": len(result)},
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}",
#         )
    





#เเบบที่ยังไม่ได้ทำ geojson
# @app.get("/api/v1/duckDBs/places/th/001", status_code=200, tags=["duckDBs"])
# async def get_data_in_duckdbs_lim_offset(
#     limit: int = Query(default=1000, ge=1),  
#     offset: int = Query(default=0, ge=0)    
# ):
#     """
#     Endpoint to fetch data from DuckDB table 'places_th' in chunks.
#     `/api/v1/duckDBs/places/02?limit=1000&offset=0`   Fetch from index 0 to 1000
#     `/api/v1/duckDBs/places/02?limit=1000&offset=1000` Fetch from index 1000 to 2000
#     Adjust `offset` to change the starting point of the query.
#     """
#     file_path = r"D:\parge\in_parge\places-00000.snappy.parquet"
#     try:
#         con = duckdb.connect()
#         con.execute(f"""
#             CREATE TABLE IF NOT EXISTS places_th AS
#             SELECT fsq_place_id, name, latitude, longitude, address, locality, region, country,
#                    date_created, date_refreshed, date_closed, fsq_category_ids, fsq_category_labels
#             FROM read_parquet('{file_path}')
#             WHERE country = 'TH'
#         """)
#         query = f"SELECT * FROM places_th LIMIT {limit} OFFSET {offset}"
#         rows = con.execute(query).fetchall()
#         column_headers = [desc[0] for desc in con.description]
#         result = [dict(zip(column_headers, row)) for row in rows]
#         count_query = "SELECT COUNT(*) FROM places_th"
#         row_count = con.execute(count_query).fetchone()[0]
#         con.close()
#         return create_response(
#             status="success",
#             message="Data fetched successfully",
#             data=result,
#             metadata={ 
#                 "row_count": len(result),
#                 "next_offset": offset + limit,
#                 "Total_all_data": row_count
#             }, 
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Unexpected error occurred: {str(e)}",
#         )





# @app.get("/image/44/image", response_model=StandardResponse, tags=["image"])
# async def get_image():
#     image_path = "C:/Users/Areeya Bunma/Desktop/image/44/0033.png"
#     if not os.path.exists(image_path):
#         return create_response(
#             status="error",
#             message="Image not found."
#         )
#     return create_response(
#         message="Image retrieved successfully.",
#         data={"image_url": image_path}
#     )









# file_path3 = "C:/Users/Areeya Bunma/Desktop/pandas/acc/heatmap-rvp.geojson"
# try:
#     geojson_data3 = load_geojson_file(file_path3)
# except HTTPException as e:
#     geojson_data3 = None




#create app@module (); print("hellow world")


#เเบบ 1 ไฟล์
# from fastapi import FastAPI
# import json

# app = FastAPI()

# # โหลด GeoJSON
# with open("C:/Users/Areeya Bunma/Desktop/pandas/acc/heatmap-rvp-death.geojson", "r", encoding="utf-8") as f:
#     geojson_data = json.load(f)

# @app.get("/accidents")
# async def get_accidents():
#     """Endpoint ที่ส่งคืนข้อมูล GeoJSON ทั้งหมด"""
#     return geojson_data


##Run this
## http://127.0.0.1:8000/accidents




#----------------------------------------------



#เเบบหลายไฟล์
# from fastapi import FastAPI
# import json
# import os

# app = FastAPI()

# # ฟังก์ชันสำหรับโหลด GeoJSON จากโฟลเดอร์
# def load_geojson_files(folder_path):
#     geojson_data = {}
#     for filename in os.listdir(folder_path):
#         if filename.endswith(".geojson"):  # ตรวจสอบว่าเป็นไฟล์ .geojson
#             file_path = os.path.join(folder_path, filename)
#             with open(file_path, "r", encoding="utf-8") as f:
#                 geojson_data[filename] = json.load(f)
#     return geojson_data

# # โหลดไฟล์ทั้งหมดในโฟลเดอร์ geojson_files
# geojson_files = load_geojson_files(r"C:\Users\Areeya Bunma\Desktop\pandas\acc") #C:\Users\Areeya Bunma\Desktop\pandas\acc

# @app.get("/all-accidents")
# async def get_all_accidents():
#     """ส่งคืนข้อมูล GeoJSON ทั้งหมด"""
#     return geojson_files


# from fastapi import FastAPI
# import json
# from fastapi.middleware.cors import CORSMiddleware
# import os




#---------------------------------------------






#-------------------------------------------



# from fastapi import FastAPI, HTTPException
# from sqlalchemy import create_engine, Column, Integer, String, Float
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.dialects.postgresql import VARCHAR

# # กำหนดรายละเอียดการเชื่อมต่อฐานข้อมูล
# DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/FSQ_DB"

# # สร้าง engine และ session
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # สร้างฐานข้อมูลจาก SQLAlchemy
# Base = declarative_base()

# # กำหนด model ให้ตรงกับตาราง h3_lv12_0123
# class H3Lv12(Base):
#     __tablename__ = "h3_lv12_0123"
#     id = Column(Integer, primary_key=True, index=True)
#     h3_index = Column(VARCHAR(50))
#     fsq_place_id = Column(String(255))
#     name = Column(String(255))
#     latitude = Column(Float)
#     longitude = Column(Float)
#     address = Column(String(255))
#     locality = Column(String(255))
#     geometry = Column(String)  # หากต้องการใช้ Geometry จริง คุณจะต้องเพิ่ม PostGIS ในฐานข้อมูล

# # สร้าง FastAPI app
# app = FastAPI()

# # Dependency สำหรับการสร้าง session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # API สำหรับดึงข้อมูลทั้งหมด
# @app.get("/places")
# def get_all_places(db: SessionLocal = next(get_db())):
#     try:
#         places = db.query(H3Lv12).all()
#         return places
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # API สำหรับดึงข้อมูลเฉพาะ id
# @app.get("/places/{place_id}")
# def get_place_by_id(place_id: int, db: SessionLocal = next(get_db())):
#     try:
#         place = db.query(H3Lv12).filter(H3Lv12.id == place_id).first()
#         if place is None:
#             raise HTTPException(status_code=404, detail="Place not found")
#         return place
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))











































##


# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Token Request</title>
#     <style>
#         pre {
#             padding: 10px;
#             border-radius: 5px;
#             white-space: pre-wrap;
#             word-wrap: break-word;
#             font-family: 'Courier New', Courier, monospace;
#             overflow-x: auto;
#         }
#         button {
#             background-color: #eaffff;
#             padding: 5px 10px;
#             border: 1px solid #ccc;
#             border-radius: 5px;
#             cursor: pointer;
#         }
#         button:disabled {
#             background-color: #f0f0f0;
#             cursor: not-allowed;
#         }
#         #response_token { background-color: #f9f9f9; }
#         #response_data { background-color: #fef7f7; }
#         #response_metadata { background-color: #fefcf7; }
#         form, select, button {
#             margin: 10px 0;
#         }
#     </style>
# </head>
# <body>
#     <h1>ขอ API</h1>
#     <h3>อายุการใช้งาน 1 นาที</h3>
#     <form id="tokenForm">
#         <label for="username">ชื่อ:</label>
#         <input type="text" id="username" name="username" value="" required>
#         <button type="submit">ส่งคำขอ</button>
#     </form>
#     <pre id="response_token"></pre>

#     <h1>เลือก API เพื่อเรียกดูข้อมูล</h1>
#     <select id="apiSelect">
#         <option value="">-- เลือก API --</option>
#         <option value="/api/v1/duckDBs/places/th/region?limit=5&region=Bangkok">parqe</option>
#         <option value="/api/v1/accidents/heatmap-rvp-death">Heatmap RVP Death</option>
#         <option value="/api/v1/accidents/grids-dbscan-2022-2020">Grids DBSCAN 2022-2020</option>
#     </select>
#     <button id="callApi" disabled>เรียก API</button>

#     <pre id="response_data"></pre>
#     <pre id="response_metadata"></pre>

#     <script>
#         let token = "";
#         let username = "";

#         // ขอ Token
#         document.getElementById('tokenForm').addEventListener('submit', async (event) => {
#             event.preventDefault();
#             username = document.getElementById('username').value;
#             try {
#                 const response = await fetch('https://bb84-125-26-174-54.ngrok-free.app/api/v1/token', {
#                     method: 'POST',
#                     headers: {
#                         'Content-Type': 'application/json',
#                     },
#                     body: JSON.stringify({ username }),
#                 });
#                 if (!response.ok) {
#                     throw new Error(`HTTP error! status: ${response.status}`);
#                 }
#                 const data = await response.json();
#                 if (data.token) {
#                     token = data.token;
#                     document.getElementById('response_token').innerText = `Token: ${token}`;
#                     document.getElementById('callApi').disabled = false;
#                 } else {
#                     document.getElementById('response_token').innerText = `Error: ${JSON.stringify(data)}`;
#                 }
#             } catch (error) {
#                 document.getElementById('response_token').innerText = `Error requesting token: ${error.message}`;
#             }
#         });

#         // เรียก API
#         document.getElementById("callApi").addEventListener("click", async () => {
#             const apiEndpoint = document.getElementById("apiSelect").value;
#             if (!apiEndpoint) {
#                 document.getElementById("response_data").innerText = "กรุณาเลือก API ก่อน!";
#                 return;
#             }
#             const selectedApi = document.getElementById("apiSelect").value;
#             if (!selectedApi) {
#                 alert("กรุณาเลือก API!");
#                 return;
#             }
#             try {
#                 const response = await fetch(`https://bb84-125-26-174-54.ngrok-free.app${selectedApi}`, {   //http://127.0.0.1:8000  //https://bb84-125-26-174-54.ngrok-free.app
#                     method: "GET",
#                     headers: { "Authorization": `Bearer ${token}` },
#                 });
#                 if (!response.ok) {
#                     throw new Error(`HTTP error! status: ${response.status}`);
#                 }
                
#                 const data = await response.json();
#                 if (data.status === "success") {
#                     document.getElementById("response_data").innerText = JSON.stringify(data, null, 2);
#                     document.getElementById("response_metadata").innerText = JSON.stringify(data.metadata, null, 2);
#                 } else {
#                     document.getElementById("response_data").innerText = `Error: ${data.message}`;
#                     document.getElementById("response_metadata").innerText = '';
#                 }
#             } catch (error) {
#                 console.error("Error fetching data:", error);
#                 document.getElementById("response_data").innerText = `Error: ${error.message}`;
#                 document.getElementById("response_metadata").innerText = '';
#             }
#         });
#     </script>
# </body>
# </html>
















# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Token Request</title>
#     <style>
#         pre {
#             padding: 10px;
#             border-radius: 5px;
#             white-space: pre-wrap;
#             word-wrap: break-word;
#             font-family: 'Courier New', Courier, monospace;
#             overflow-x: auto;
#         }
#         button {
#             background-color: #eaffff;
#             padding: 5px 10px;
#             border: 1px solid #ccc;
#             border-radius: 5px;
#             cursor: pointer;
#         }
#         button:disabled {
#             background-color: #f0f0f0;
#             cursor: not-allowed;
#         }
#         #response_token { background-color: #f9f9f9; }
#         #response_data { background-color: #fef7f7; }
#         #response_metadata { background-color: #fefcf7; }
#         form, select, button {
#             margin: 10px 0;
#         }
#     </style>
# </head>
# <body>
#     <h1>ขอ API</h1>
#     <h3>อายุการใช้งาน 1 นาที</h3>
#     <form id="tokenForm">
#         <label for="username">ชื่อ:</label>
#         <input type="text" id="username" name="username" value="" required>
#         <button type="submit">ส่งคำขอ</button>
#     </form>
#     <pre id="response_token"></pre>

#     <h1>เลือก API เพื่อเรียกดูข้อมูล</h1>
#     <select id="apiSelect">
#         <option value="">-- เลือก API --</option>
#         <option value="/api/v1/duckDBs/places/th/region?limit=5&region=Bangkok">parqe</option>
#         <option value="/api/v1/accidents/heatmap-rvp-death">Heatmap RVP Death</option>
#         <option value="/api/v1/accidents/grids-dbscan-2022-2020">Grids DBSCAN 2022-2020</option>
#     </select>
#     <button id="callApi" disabled>เรียก API</button>

#     <pre id="response_data"></pre>
#     <pre id="response_metadata"></pre>

#     <script>
#         let token = "";
#         let username = "";

#         // ขอ Token
#         document.getElementById('tokenForm').addEventListener('submit', async (event) => {
#             event.preventDefault();
#             username = document.getElementById('username').value;
#             try {
#                 const response = await fetch('https://bb84-125-26-174-54.ngrok-free.app/api/v1/token', {
#                     method: 'POST',
#                     headers: {
#                         'Content-Type': 'application/json',
#                     },
#                     body: JSON.stringify({ username }),
#                 });
#                 if (!response.ok) {
#                     throw new Error(HTTP error! status: ${response.status});
#                 }
#                 const data = await response.json();
#                 if (data.token) {
#                     token = data.token;
#                     document.getElementById('response_token').innerText = Token: ${token};
#                     document.getElementById('callApi').disabled = false;
#                 } else {
#                     document.getElementById('response_token').innerText = Error: ${JSON.stringify(data)};
#                 }
#             } catch (error) {
#                 document.getElementById('response_token').innerText = Error requesting token: ${error.message};
#             }
#         });

#         // เรียก API
#         document.getElementById("callApi").addEventListener("click", async () => {
#             const apiEndpoint = document.getElementById("apiSelect").value;
#             if (!apiEndpoint) {
#                 document.getElementById("response_data").innerText = "กรุณาเลือก API ก่อน!";
#                 return;
#             }
#             const selectedApi = document.getElementById("apiSelect").value;
#             if (!selectedApi) {
#                 alert("กรุณาเลือก API!");
#                 return;
#             }
#             try {
#                 const response = await fetch(https://bb84-125-26-174-54.ngrok-free.app${selectedApi}, {   //http://127.0.0.1:8000  //https://bb84-125-26-174-54.ngrok-free.app
#                     method: "GET",
#                     headers: { "Authorization": Bearer ${token} },
#                 });
#                 if (!response.ok) {
#                     throw new Error(HTTP error! status: ${response.status});
#                 }

#                 const contentType = response.headers.get("Content-Type");
#                 if (!contentType || !contentType.includes("application/json")) {
#                     const text = await response.text();
#                     throw new Error(Unexpected response format. Content-Type: ${contentType}. Response: ${text});
#                 }

#                 const data = await response.json();
#                 if (data.status === "success") {
#                     document.getElementById("response_data").innerText = JSON.stringify(data, null, 2);
#                     document.getElementById("response_metadata").innerText = JSON.stringify(data.metadata, null, 2);
#                 } else {
#                     document.getElementById("response_data").innerText = Error: ${data.message};
#                     document.getElementById("response_metadata").innerText = '';
#                 }
#             } catch (error) {
#                 console.error("Error fetching data:", error);
#                 document.getElementById("response_data").innerText = Error: ${error.message};
#                 document.getElementById("response_metadata").innerText = '';
#             }
#         });
#     </script>
# </body>
# </html>
