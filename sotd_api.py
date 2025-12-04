from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SOTD API")

# Add CORS to allow requests from anywhere (including Shortcuts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SOTD(BaseModel):
    entry_number: int
    date: str
    title: str
    artist: str
    track_url: str
    playlist_url: str
    image_url: Optional[str] = None

STORAGE_FILE = "sotd_data.json"

def load_sotd() -> SOTD:
    """Load SOTD from JSON file. If no file exists, return default data."""
    default_sotd = SOTD(
        entry_number=0,
        date="1970-01-01",
        title="No SOTD yet",
        artist="",
        track_url="https://open.spotify.com",
        playlist_url="https://open.spotify.com/playlist/7vas6ruuKqAAdM7xXxbpTE",
        image_url=None
    )
    
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, "r") as f:
                data = json.load(f)
                # Convert loaded data back to SOTD object
                return SOTD(**data)
    except Exception as e:
        print(f"Error loading SOTD data: {e}")
    
    return default_sotd

def save_sotd(sotd: SOTD):
    """Save SOTD to JSON file."""
    try:
        with open(STORAGE_FILE, "w") as f:
            json.dump(sotd.dict(), f, indent=2)
        print(f"SOTD saved: {sotd.title}")
    except Exception as e:
        print(f"Error saving SOTD data: {e}")

# Load the current SOTD from file when the app starts
LATEST_SOTD = load_sotd()

@app.get("/current")
def get_current():
    """Return the current SOTD data."""
    return LATEST_SOTD

@app.post("/update")
def update_sotd(sotd: SOTD):
    """Update the SOTD data and save to file."""
    global LATEST_SOTD
    LATEST_SOTD = sotd
    save_sotd(sotd)
    return {"status": "updated", "song": sotd.title}

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring services."""
    return {
        "status": "healthy", 
        "current_sotd": LATEST_SOTD.title,
        "entry": LATEST_SOTD.entry_number,
        "file_exists": os.path.exists(STORAGE_FILE)
    }

@app.get("/wakeup")
def wakeup():
    """Simple endpoint to wake up the app."""
    return {"message": "API is awake", "song": LATEST_SOTD.title}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)