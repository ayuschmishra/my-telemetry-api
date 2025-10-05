from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data (if needed for testing)
with open("api/q-vercel-latency.json", "r") as f:
    telemetry_data = json.load(f)

@app.post("/")
async def process_telemetry(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    
    result = {}
    for region in regions:
        data = telemetry_data.get(region, [])
        if not data:
            result[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": 0}
            continue
        
        latencies = [rec["latency_ms"] for rec in data]
        uptimes = [rec["uptime"] for rec in data]
        
        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(1 for x in latencies if x > threshold)
        }
    return result
