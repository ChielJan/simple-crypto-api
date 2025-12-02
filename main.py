from fastapi import FastAPI
import httpx

app = FastAPI(
    title="AstraScout Crypto API",
    description="""
A lightweight crypto data API built step-by-step.  
Provides live USD prices + simple utility scoring for selected tokens.  

🚀 Built for learning, experimenting, and creating — free to use!  
Maintained by **AstraScout**, exploring Web3 with transparency and insight.
""",
    version="1.2.1"
)

# -------------------------------------------
# Supported tokens
# -------------------------------------------
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "LINK": "chainlink"
}

UTILITY_SCORES = {
    "BTC": 95,
    "ETH": 100,
    "SOL": 88,
    "BNB": 85,
    "XRP": 70,
    "ADA": 60,
    "DOGE": 25,
    "DOT": 78,
    "AVAX": 82,
    "LINK": 90
}

# -------------------------------------------
# Root
# -------------------------------------------
@app.get("/", tags=["General"], summary="Root Endpoint")
def root():
    return {
        "message": "Welcome to AstraScout Crypto API 🚀",
        "endpoints": ["/price/{symbol}", "/price/all", "/utility-score/{symbol}"],
        "status": "online"
    }

# -------------------------------------------
# Say Hello
# -------------------------------------------
@app.get("/hello/{name}", tags=["General"], summary="Say Hello")
def hello(name: str):
    return {"message": f"Hello {name} 👋", "api": "AstraScout Crypto API"}

# -------------------------------------------
# Utility Score
# -------------------------------------------
@app.get("/utility-score/{symbol}", tags=["Utility"], summary="Get Utility Score")
def utility_score(symbol: str):
    sym = symbol.upper()
    if sym not in UTILITY_SCORES:
        return {"error": f"Token '{sym}' not supported."}
    return {"token": sym, "utility_score": UTILITY_SCORES[sym]}

# -------------------------------------------
# Price for single token
# -------------------------------------------
@app.get("/price/{symbol}", tags=["Prices"], summary="Get Price")
async def get_price(symbol: str):
    sym = symbol.upper()

    if sym not in COINGECKO_IDS:
        return {"error": f"Token '{sym}' not supported yet."}

    cg_id = COINGECKO_IDS[sym]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10)
            data = r.json()
    except Exception as e:
        return {"error": f"Failed to fetch price: {str(e)}"}

    return {
        "token": sym,
        "price_usd": data.get(cg_id, {}).get("usd", None)
    }


# -------------------------------------------
# Price for ALL tokens
# -------------------------------------------
@app.get("/price/all", tags=["Prices"], summary="Get All Prices")
async def get_all_prices():
    ids_str = ",".join(COINGECKO_IDS.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=10)
            data = r.json()
    except Exception as e:
        return {"error": f"Failed to fetch prices: {str(e)}"}

    result = {}
    for sym, cg_id in COINGECKO_IDS.items():
        price = data.get(cg_id, {}).get("usd", None)
        result[sym] = {"price_usd": price}

    return result
