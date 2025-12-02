from fastapi import FastAPI
import httpx

app = FastAPI(
    title="AstraScout Crypto API",
    description="Simple utility + price API",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "message": "AstraScout Crypto API Online 🚀",
        "endpoints": ["/hello/{name}", "/utility-score/{symbol}", "/price/{symbol}"]
    }

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name} 👋"}

UTILITY_SCORES = {
    "BTC": {"utility_score": 88, "summary": "Strong store of value"},
    "ETH": {"utility_score": 92, "summary": "Smart contract leader"},
    "SOL": {"utility_score": 85, "summary": "Fast & scalable"},
}

@app.get("/utility-score/{symbol}")
def get_utility_score(symbol: str):
    sym = symbol.upper()
    if sym in UTILITY_SCORES:
        data = UTILITY_SCORES[sym]
        return {"token": sym, "utility_score": data["utility_score"], "summary": data["summary"]}
    return {"token": sym, "utility_score": 50, "summary": "Unknown token"}

# ⭐ Hier komt de echte waarde: prijs endpoint
COINGECKO_IDS = {
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "MATIC": "polygon",
    "DOT": "polkadot"
}

}

@app.get("/price/{symbol}")
async def get_price(symbol: str):
    sym = symbol.upper()
    
    if sym not in COINGECKO_IDS:
        return {"error": "Token not supported yet"}

    cg_id = COINGECKO_IDS[sym]

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

    return {
        "token": sym,
        "price_usd": data.get(cg_id, {}).get("usd", None)
    }
