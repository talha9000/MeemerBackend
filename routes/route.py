import os
from fastapi import APIRouter, HTTPException, File, UploadFile,Form,Query,Response
from PIL import Image
from io import BytesIO
import json
from typing import List,Annotated
from uuid import uuid4
import base64
from fastapi.responses import JSONResponse, StreamingResponse
import mimetypes

Router = APIRouter()

ALLOWED_IMAGE_FORMATS = ["image/jpeg", "image/png", "image/gif"]
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@Router.post("/upload_file", tags=["Upload_file"])


async def upload_file(
    files: List[UploadFile] = File(...),
    titles: List[str] = Form(...),
    descriptions: List[str] = Form(...)
):  
    
    try:
        titles = list(titles)
        descriptions = list(descriptions)

        tf = len(files)
        tt = len(titles)
        td = len(descriptions)
    

        if tf != tt or tf != td:
            return {"error": f"Number of files, titles, and descriptions must be the same. Files: {tf}, Titles: {tt}, Descriptions: {td}"}

        uploaded_files = []
        tmp=[]
        for idx, file in enumerate(files):
            contents = await file.read()
            filename = file.filename
            file_extension = filename.split(".")[-1]
            file_path = os.path.join(UPLOAD_DIR, f"{titles[idx]}.{file_extension}")

            if (os.path.exists(file_path)):
                raise HTTPException(500,f"Error  file already {titles[idx]} exist change title ")
            with open(file_path, "wb") as f:
                f.write(contents)
            uploaded_files.append({
                "filename": file.filename,
                "title": titles[idx],
                "description": descriptions[idx],
                "file_path": file_path
            })
            jfp=os.path.join(UPLOAD_DIR,f"{titles[idx]}.json")
            with open(file=jfp, mode='w') as sjf:
                json.dump(uploaded_files, sjf, indent=2)
            tmp=uploaded_files.copy()
            uploaded_files.clear()
            

        return {"uploaded_files sucess": tmp}
    except Exception as e:
        raise HTTPException(500,f"Error ocur uplaod file due to:::: {e}")


@Router.get("/get_files", tags=['Upload_file'], name="Get all uploaded files", description="Show uploaded files")
async def getfile():
    try:
        image_files = []
        if os.path.exists(UPLOAD_DIR):
            for root, _, files in os.walk(UPLOAD_DIR):
                for f in files:
                    if f.endswith((".png", ".jpeg", ".jpg")):
                        fname = f.split('.')[0]
                        fname = fname + ".json"
                        jrp = os.path.join(root, fname)
                        if os.path.exists(jrp):
                            with open(jrp, 'r') as jf:
                                try:
                                    data = json.load(jf)
                                    if data:
                                        # Read image content and encode as base64
                                        with open(os.path.join(root, f), "rb") as image_file:
                                            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

                                        image_files.append({
                                            "filename": f,
                                            "path": data[0]['file_path'],
                                            "title": data[0]['title'],
                                            "description": data[0]['description'],
                                            "image_content": encoded_image
                                        })
                                except json.JSONDecodeError:
                                    raise HTTPException(500, "JSON decode fail")
                    elif f.endswith(".json"):
                        jbp = os.path.join(root, f)
                        with open(jbp, 'r') as jp:
                            data = json.load(jp)
                            if 'upload-type' in data and data['upload-type'] == "text-post":
                                image_files.append({
                                    "type": data.get('type'),
                                    "title": data.get('title'),
                                    "description": data.get('description')
                                })


                                     
                        
        # Return as JSON array
        return JSONResponse(content={"image_files": image_files})
    except Exception as e:
        raise HTTPException(500, f"Error viewing files: {e}")

@Router.get("/get_files_query", tags=['get-file'], name="Get all uploaded files", description="Show uploaded files")
async def getfile(title: str = Query(None, description="Filter by title"), description: str = Query(None, description="Filter by description")):
    try:
        image_files = []
        if os.path.exists(UPLOAD_DIR):
            for root, _, files in os.walk(UPLOAD_DIR):
                for f in files:
                    if f.endswith((".png", ".jpeg", ".jpg")):
                        fname = f.split('.')[0]
                        fname = fname + ".json"
                        jrp = os.path.join(root, fname)
                        if os.path.exists(jrp):
                            with open(jrp, 'r') as jf:
                                try:
                                    data = json.load(jf)
                                    if data:
                                        if (not title or data[0]['title'] == title) and (not description or data[0]['description'] == description):
                                            # Open the image file and encode its content as base64
                                            image_file_path = os.path.join(root, f)
                                            with open(image_file_path, "rb") as image_file:
                                                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                                            
                                            image_files.append({
                                                "filename": f,
                                                "path": data[0]['file_path'],
                                                "title": data[0]['title'],
                                                "description": data[0]['description'],
                                                "image_content": encoded_image
                                            })
                                except json.JSONDecodeError:
                                    raise HTTPException(500, "JSON decode fail")
            return {"image_files": image_files}
        else:
            raise HTTPException(400, "No such directory exists")
    except Exception as e:
        raise HTTPException(500, f"Error viewing files: {e}")

async def encode_video(vf):
    with open(vf, 'rb') as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            yield chunk
        

@Router.post("/write",tags=['Write something'])
async def Write_Post(title:str,desription:str):
    try:
        tmp=[]
        if not title and not desription or not title or not desription:
            raise HTTPException(500,"Title and description is required")
        odir=os.path.join(UPLOAD_DIR,f"{title}.json")
        with open(odir,'w')as jfw:
            tmp.append([
                {
                    "upload-type":"text-post",
                    "title":title,
                    "description":desription
                }
            ])
            json.dump(tmp,jfw)
            return Response("upload sucess!!",200)
    except Exception as e:
          raise HTTPException(500,"fail to write post {e}")