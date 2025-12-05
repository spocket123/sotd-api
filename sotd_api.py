from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SOTD API")

# CORS: allow iOS Shortcuts or anything else to call this easily
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORAGE_FILE = "sotd_data.json"


class SOTD(BaseModel):
    entry_number: int
    date: str
    title: str
    artist: str
    track_url: str
    playlist_url: str
    image_url: Optional[str] = None


LATEST_SOTD: Optional[SOTD] = None


def load_from_disk() -> Optional[SOTD]:
    """Load the last saved SOTD from disk, if present."""
    if not os.path.exists(STORAGE_FILE):
        return None
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SOTD(**data)
    except Exception as e:
        print("Failed to load SOTD from disk:", e)
        return None


def save_to_disk(sotd: SOTD) -> None:
    """Persist SOTD to a JSON file."""
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(sotd.model_dump(), f, indent=2)
    except Exception as e:
        print("Failed to save SOTD to disk:", e)


# Initialize in-memory state on startup
@app.on_event("startup")
def startup_event():
    global LATEST_SOTD
    LATEST_SOTD = load_from_disk()
    if LATEST_SOTD:
        print(f"Loaded SOTD from disk: {LATEST_SOTD.title} ({LATEST_SOTD.date})")
    else:
        print("No existing SOTD found on disk.")


@app.get("/")
def root():
    """Basic info endpoint."""
    return {
        "message": "MGW Song of the Day API",
        "has_current": LATEST_SOTD is not None,
    }


@app.get("/current")
def get_current():
    """
    Return the current SOTD.
    This is what your iOS Shortcuts should call.
    """
    global LATEST_SOTD

    if LATEST_SOTD is None:
        # if possible, try to lazy-load from disk
        loaded = load_from_disk()
        if loaded:
            LATEST_SOTD = loaded
        else:
            return {"error": "No SOTD set yet."}

    return LATEST_SOTD


@app.post("/update")
def update_sotd(sotd: SOTD):
    """
    Update the current SOTD.
    Called by your Discord bot whenever a new SOTD is posted,
    or when you run /update_api to re-send the same one.
    """
    global LATEST_SOTD
    LATEST_SOTD = sotd
    save_to_disk(sotd)
    return {"status": "ok", "message": "SOTD updated.", "title": sotd.title}


@app.get("/health")
def health():
    """
    Simple health endpoint so you (and Render) can see if the app is alive.
    """
    return {
        "status": "healthy",
        "current_sotd": LATEST_SOTD.title if LATEST_SOTD else None,
        "entry": LATEST_SOTD.entry_number if LATEST_SOTD else None,
        "file_exists": os.path.exists(STORAGE_FILE),
    }


@app.get("/wakeup")
def wakeup():
    """Simple endpoint to wake up the app (used by /wakeup command on the bot)."""
    title = LATEST_SOTD.title if LATEST_SOTD else None
    return {"message": "API is awake", "song": title}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)