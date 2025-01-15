from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import logging

logging.basicConfig(filename="logs/node_activity.log", level=logging.INFO, format="%(asctime)s - %(message)s")

app = FastAPI()

nodes = []

class Node(BaseModel):
    ip : str
    port : int

@app.get("/")
async def read_root():
    return {"Message":"This is the masterserver for registration of nodes"}

@app.get("/nodes")
async def get_nodes():
    return nodes

@app.post("/register")
async def registered_nodes(node:Node):
    try:
        nodes.append(node)
        logging.info("Node registration successfull")
        return {f"Message":"Node registration for {node.ip} : {node.port} was successfull"}
    except Exception as e:
        logging.error(f"Registration failed : {e}")

if __name__=="__main__":
    uvicorn.run(app, host="127.0.0.1",port=8000)


