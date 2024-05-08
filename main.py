from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.route import Router

app = FastAPI(title="Meemer API")

# Include CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can adjust this to your specific needs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(Router)
 