from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from routers import login, user

# set up app
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routes
app.include_router(login.router, tags=["login"])
app.include_router(user.router, tags=["user"])


# all misc routes
@app.get("/")
def root():
    return RedirectResponse("/docs")
