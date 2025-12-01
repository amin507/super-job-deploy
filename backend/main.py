from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Backend is running"}

@app.get("/odoo/status")
def odoo_status():
    return {"odoo": "ok"}
