from fastapi import FastAPI
from pydantic import BaseModel

from shared.state import publish_incident

app = FastAPI()

class Incident(BaseModel):
    number: str
    short_description: str
    description: str

@app.post("/incident")
async def receive_incident(incident: Incident):
    data = {
        "number": incident.number,
        "short_description": incident.short_description,
        "description": incident.description
    }
    await publish_incident(data)
    
    return { "status": "RECEIVED", "incident": data }