from fastapi import FastAPI

app = FastAPI(
    title="Simple Crypto API",
    description="My first tiny API, built with a bit of help 🚀",
    version="0.1.0",
)

@app.get("/")
def root():
    return {
        "message": "Hello from AstraScout's first API 🚀",
        "status": "online"
    }
@app.get("/hello/{name}")
def say_hello(name: str):
    return {
        "message": f"Hello {name}! 👋"
    }
