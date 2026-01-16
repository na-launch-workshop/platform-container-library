from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yaml

try:
    with open('/devhub/dashboard.yaml', 'r') as f:
        dashboard_data = yaml.safe_load(f)
except Exception as e:
    raise RuntimeError(f"Failed to load /devhub/dashboard.yaml: {e}")

try:
    with open('/devhub/radar.yaml', 'r') as f:
        radar_data = yaml.safe_load(f)
except Exception as e:
    raise RuntimeError(f"Failed to load /devhub/radar.yaml: {e}")

app = FastAPI()

@app.get("/dashboard")
async def get_dashboard():
    if dashboard_data is None:
        raise HTTPException(status_code=500, detail="Dashboard data not loaded")
    return JSONResponse(content=dashboard_data)

@app.get("/radar")
async def get_radar():
    if radar_data is None:
        raise HTTPException(status_code=500, detail="Radar data not loaded")
    return JSONResponse(content=radar_data)
