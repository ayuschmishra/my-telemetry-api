from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load the telemetry data from JSON (adjust path if needed; assumes file in project root)
data = pd.read_json("q-vercel-latency.json")  # Assumes JSON is a list of dicts with 'region', 'latency', 'uptime'

class RequestBody(BaseModel):
    regions: List[str]
    threshold_ms: int

@app.post("/")
def get_metrics(body: RequestBody):
    results = {}
    for region in body.regions:
        df_region = data[data['region'] == region]
        if not df_region.empty:
            avg_latency = df_region['latency'].mean()
            p95_latency = df_region['latency'].quantile(0.95)
            avg_uptime = df_region['uptime'].mean()
            breaches = (df_region['latency'] > body.threshold_ms).sum()
            results[region] = {
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": int(breaches)  # Ensure breaches is an integer
            }
    return results
