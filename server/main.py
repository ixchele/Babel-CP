from fastapi import FastAPI
import auth
# import submissions

app = FastAPI(title="Project Babel API")

# Connect the routers to the main application
app.include_router(auth.router)
# app.include_router(submissions.router)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "Project Babel Server is running"}
