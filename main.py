from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Added import
from db.database import engine
from db import models
from router import user, usage, inventory, health
from auth import authentication

app = FastAPI()

# --- CORS CONFIGURATION START ---
# Define the origins that are allowed to make requests to this API
# We include localhost for development and your specific network IP
origin_regex = r"https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.\d+\.\d+\.\d+)(:\d+)?"
#origins = [
#    "http://localhost:3000",
#    "http://127.0.0.1:3000",
#    "http://10.75.40.10:3000",
#    "http://10.75.40.1:3000",
#    "http://10.88.0.1:3000", # Common for containerized or network environments
#]

app.add_middleware(
    CORSMiddleware,
#   allow_origins=origins, 
    allow_origin_regex=origin_regex,           # For dev, this is the most reliable wildcard
    allow_credentials=True,        # Must be false for "*"
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- CORS CONFIGURATION END ---

app.include_router(user.router)
app.include_router(usage.router)
app.include_router(inventory.router)
app.include_router(authentication.router)
app.include_router(health.router)


@app.get("/")
def root():
    return {"message": "DC Inventory FastAPI Backend"}

models.Base.metadata.create_all(engine)