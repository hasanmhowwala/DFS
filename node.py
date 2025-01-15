from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os 
import logging
import argparse
import httpx
import uvicorn

logging.basicConfig(filename="logs/node_activity.log", level=logging.INFO, format="%(asctime)s - %(message)s")

parser = argparse.ArgumentParser(description="To run a distributed node")
parser.add_argument("--port", type=int, default=8000, help="The port to run the node on")
args = parser.parse_args()
port = args.port

STORAGE_DIR = f"storage/node_storage{port}"
DISCOVERY_SERVER_URL = "http://127.0.0.1:8000/register"

os.makedirs(STORAGE_DIR,exist_ok=True)

app = FastAPI()

async def node_discovery():
    async with httpx.AsyncClient() as client:
        node_info = {"ip":"127.0.0.1", "port":port}
        await client.post(
            DISCOVERY_SERVER_URL,
            json=node_info
        )

@app.on_event("startup")
async def on_stratup():
    await node_discovery()

@app.get("/")
def read_root():
    return {"content":"Welcome to the Node for Hasan's Distributed Filesystem"}

@app.get("/download-file/{filename}")
async def download_file(filename:str):
    file_location = os.path.join(STORAGE_DIR,filename)
    if os.path.exists(file_location):
        logging.info(f"{filename} downloaded successfully")
        return FileResponse(
            
            path = file_location,
            filename = filename,
            media_type = None
        )
    else:
        logging.error("The download wasn't successfull")
        return {"response":"File not found, please try with a different filename"}

@app.post("/upload-file")
async def upload_file(file:UploadFile = File(...)):
    try:
        file_location = os.path.join(STORAGE_DIR,file.filename)
        with open(file_location,"wb") as f:
            content = await file.read()
            f.write(content)
        logging.info(f" File {file.filename} succesfully uploaded")

        async with httpx.AsyncClient() as client:
            files = {"file":(file.filename,content)}
            response = client.get(f"{DISCOVERY_SERVER_URL}/nodes")
            nodes = response.json()

            for node in nodes:
                try:
                    if node["port"]!=port:
                        await client.post(
                            f"http://{node['ip']}:{node['port']}/replicate",
                            files = files
                        )
                except httpx.HTTPStatusError as e:
                    logging.error(f"Failed to replicate to {node['ip']}:{node['port']} - {e}")


        logging.info(f" File {file.filename} replicated successsfully")
        return {"response":f"{file.filename} succesfully uploaded and replicated"}
    except Exception as e:
        logging.error(f"Error uploading file : {e}")
        return {"error":str(e)}
    
@app.post("/replicate")
async def replicate_file(file : UploadFile = File(...)):
    file_location = os.path.join(STORAGE_DIR,file.filename)
    try:
        content = await file.read()
        with open(file_location, "wb") as f:
            f.write(content)
        logging.info(f"File {file.filename} replicated succesfully to node")
        return{"response":"File {file.filename} replicated successfully"}
    except Exception as e:
        logging.error(f"Failed to replicate file: {file.filename}. Error: {e}")
        raise HTTPException(status_code=500, detail="Replication Failed")
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=args.port)
    
