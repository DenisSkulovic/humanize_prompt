from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import register_routes

app = FastAPI(title="Humanization API", version="1.0.0")

# CORS Middleware (if needed for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
register_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
