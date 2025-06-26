from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cvrdtp, dashboard, exemptedvehicles, monthlypass, setup, tollfee, tolltransactions, users, helppage
# from app.routers import *


app = FastAPI(title="TNMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(setup.router)
app.include_router(tollfee.router)
app.include_router(exemptedvehicles.router)
app.include_router(monthlypass.router)
app.include_router(cvrdtp.router)
app.include_router(tolltransactions.router)
app.include_router(helppage.router)








