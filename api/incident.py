from fastapi import FastAPI
from pydantic import BaseModel

from shared.state import add_item

app = FastAPI()

class Incident(BaseModel):
    number: str
    short_description: str
    description: str

@app.post("/incident")
def receive_incident(incident: Incident):
    data = {
        "number": incident.number,
        "short_description": incident.short_description,
        "description": incident.description
    }
    add_item(data)
    
    return { "status": "RECEIVED", "incident": data }