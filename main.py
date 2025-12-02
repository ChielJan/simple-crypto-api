from fastapi import FastAPI

app = FastAPI(
    title="Simple Crypto API",
    description="My first tiny API, built with a bit of help 🚀",
    version="0.2.0",
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

# Heel simpele 'utility data' voor een paar tokens.
UTILITY_SCORES = {
    "BTC": {
        "utility_score": 88,
        "summary": "BTC is widely adopted as a store of value and settlement layer."
    },
    "ETH": {
        "utility_score": 92,
        "summary": "ETH powers a massive ecosystem of DeFi, NFTs and smart contracts."
    },
    "SOL": {
        "utility_score": 85,
        "summary": "SOL is fast, cheap and hosts a growing ecosystem of dApps."
    },
    "DOGE": {
        "utility_score": 55,
        "summary": "DOGE has strong meme power, but limited real-world utility."
    }
}

@app.get("/utility-score/{symbol}")
def get_utility_score(symbol: str):
    sym = symbol.upper()

    if sym in UTILITY_SCORES:
        data = UTILITY_SCORES[sym]
        return {
            "token": sym,
            "utility_score": data["utility_score"],
            "summary": data["summary"]
        }
    else:
        # Standaard antwoord voor onbekende tokens
        return {
            "token": sym,
            "utility_score": 50,
            "summary": "No specific data found. Treated as unknown utility for now."
        }
