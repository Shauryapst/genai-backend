# app/main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import all_endpoints
import uvicorn

app = FastAPI()

origins = [
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(all_endpoints.router, prefix='/api/v1')


    

@app.get('/')
async def root():
    return RedirectResponse('/docs', status_code=302)

if __name__ == '__main__':
    uvicorn.run(app, port=8080)