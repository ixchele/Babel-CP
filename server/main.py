from fastapi import FastAPI
from database import engine, Base
import auth
# import submissions
import problems

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Babel API")

app.include_router(auth.router)
# app.include_router(submissions.router)
app.include_router(problems.router)
