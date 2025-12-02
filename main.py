from fastapi import FastAPI
import httpx

app = FastAPI(
    title="AstraScout Crypto API",
    description="Simple crypto price + utility API",
    version="1.1.0",
)

# ------------------------------
# ROOT
# ------------------------------

@app.get("/")
def root():
    return {
        "message": "AstraScout Crypto API Online 🚀",
        "endpoints": [
            "/hello/{name}",
            "/utility-score/{symbol}",
            "/price/{symbol}"
        ]
    }


# ------------------------------
# HELLO ENDPOINT
# ------------------------------

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}! 👋"}


# ------------------------------
# SIMPLE UTILITY SCORE
# ------------------------------

UTILITY_SCORES = {
    "BTC": {"utility_score": 88, "summary": "Strong, secure, widely adopted store of value."},
    "ETH": {"utility_score": 92, "summary": "Smart contract leader powering DeFi + NFTs."},
    "SOL": {"utility_score": 85, "summary": "Fast, scalable chain with strong ecosystem growth."},
    "BNB": {"utility_score": 80, "summary": "Major exchange chain with high retail usage."},
    "DOGE": {"utility_score": 55, "summary": "Meme-driven, limited real-world utility."},
    "ADA": {"utility_score": 60, "summary": "Strong academic vision, slower real-world adoption."},
    "XRP": {"utility_score": 78, "summary": "Fast settlement asset used for cross-border payments."}
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

    return {
        "token": sym,
        "utility_score": 50,
        "summary": "Unknown token — no utility data available."
    }


# ------------------------------
# CRYPTO PRICE ENDPOINT (COINGECKO)
# ------------------------------

COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "MATIC": "polygon",
    "TRX": "tron",
    "ATOM": "cosmos",
    "UNI": "uniswap",
    "LTC": "litecoin",
    "ETC": "ethereum-classic",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "FTM": "fantom",
    "NEAR": "near",
}

@app.get("/price/{symbol}")
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
