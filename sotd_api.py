from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="SOTD API")

class SOTD(BaseModel):
    entry_number: int
    date: str
    title: str
    artist: str
    track_url: str
    playlist_url: str
    image_url: Optional[str] = None

LATEST_SOTD = SOTD(
    entry_number=0,
    date="1970-01-01",
    title="No SOTD yet",
    artist="",
    track_url="https://open.spotify.com",
    playlist_url="https://open.spotify.com",
    image_url=None
)

@app.get("/current")
def get_current():
    return LATEST_SOTD

@app.post("/update")
def update(sotd: SOTD):
    global LATEST_SOTD
    LATEST_SOTD = sotd
    return {"ok": True}
