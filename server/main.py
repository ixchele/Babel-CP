from fastapi import FastAPI
from database import engine, Base
import auth
import submission
import users
import problems
import contest

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Babel API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contest.router)
app.include_router(submission.router)
app.include_router(problems.router)
