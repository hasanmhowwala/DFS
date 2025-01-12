from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


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
    nodes.append(node)
    return {f"Message":"Node registration for {node.ip} : {node.port} was successfull"}

if __name__=="__main__":
    uvicorn.run(app, host="127.0.0.1",port=8000)


