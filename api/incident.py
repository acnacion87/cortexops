from fastapi import FastAPI
from pydantic import BaseModel

from shared.state import add_item

app = FastAPI()

class Incident(BaseModel):
    id: str
    title: str
    description: str

@app.post("/incident")
def receive_incident(incident: Incident):
    data = { "id": incident.id, "title": incident.title, "description": incident.description }
    add_item(data)
    return { "status": "RECEIVED", "incident": data }