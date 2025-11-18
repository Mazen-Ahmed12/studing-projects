from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
import asyncio

app = FastAPI()


# Middleware example: This adds a custom middleware to measure and add response time to headers
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Route example: A simple synchronous route
@app.get("/sync")
def sync_route():
    return {"message": "This is a synchronous route"}


# Async route example: An asynchronous route that simulates a delay
@app.get("/async")
async def async_route():
    await asyncio.sleep(1)  # Simulate async I/O operation
    return {"message": "This is an asynchronous route"}


# Another async route with path parameters
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "description": "Item fetched asynchronously"}
