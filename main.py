from fastapi import FastAPI, Path
import httpx

app = FastAPI(
    title="AstraScout Crypto API",
    description="""
A lightweight crypto price + utility API built step-by-step 🚀  

---

### 🔥 Supported Price Tokens (26)
BTC, ETH, SOL, BNB, XRP, ADA, DOGE, MATIC, DOT, LINK,  
TRX, ATOM, AVAX, LTC, ETC, UNI, APT, ARB, OP,  
FTM, NEAR, XLM, ICP, FIL, EGLD, AAVE  

### 🔵 Supported Utility Tokens (10)
BTC, ETH, SOL, BNB, XRP, ADA, DOGE, MATIC, DOT, LINK  

---

Built and maintained by **AstraScout** ⚡  
Ideal for testing, bots, dashboards, education & experiments.
""",
    version="1.4.1",
)

# ============================================================
# TOKEN CONFIG
# ============================================================

COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "MATIC": "matic-network",
    "DOT": "polkadot",
    "LINK": "chainlink",
    "TRX": "tron",
    "ATOM": "cosmos",
    "AVAX": "avalanche-2",
    "LTC": "litecoin",
    "ETC": "ethereum-classic",
    "UNI": "uniswap",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "FTM": "fantom",
    "NEAR": "near",
    "XLM": "stellar",
    "ICP": "internet-computer",
    "FIL": "filecoin",
    "EGLD": "multiversx",
    "AAVE": "aave",
}

UTILITY_SCORES = {
    "BTC": {"utility_score": 95, "summary": "Global store of value and settlement asset."},
    "ETH": {"utility_score": 100, "summary": "Smart contract leader powering DeFi & NFTs."},
    "SOL": {"utility_score": 88, "summary": "Fast, scalable chain with strong ecosystem growth."},
    "BNB": {"utility_score": 85, "summary": "Exchange chain with massive retail usage."},
    "XRP": {"utility_score": 75, "summary": "Used for fast cross-border settlement."},
    "ADA": {"utility_score": 60, "summary": "Research-driven chain with slower adoption."},
    "DOGE": {"utility_score": 30, "summary": "High meme power but limited real utility."},
    "MATIC": {"utility_score": 80, "summary": "Scaling chain used in many real dApps."},
    "DOT": {"utility_score": 78, "summary": "Interoperability-focused ecosystem."},
    "LINK": {"utility_score": 90, "summary": "Leading oracle system connecting real-world data."},
}

# ============================================================
# ROOT
# ============================================================

@app.get("/", tags=["General"], summary="API status & overview")
def root():
    return {
        "message": "AstraScout Crypto API Online 🚀",
        "endpoints": {
            "hello": "/hello/{name}",
            "price_single": "/price/{symbol}",
            "price_all": "/price/all",
            "utility_single": "/utility-score/{symbol}",
            "supported_price": "/supported/price",
            "supported_utility": "/supported/utility",
        },
        "tokens_supported_price": list(COINGECKO_IDS.keys()),
        "tokens_supported_utility": list(UTILITY_SCORES.keys()),
        "status": "online",
    }

# ============================================================
# SUPPORTED TOKENS ENDPOINTS
# ============================================================

@app.get("/supported/price", tags=["General"], summary="List all supported price tokens")
def supported_price_tokens():
    return {"supported_price_tokens": list(COINGECKO_IDS.keys())}


@app.get("/supported/utility", tags=["General"], summary="List all supported utility tokens")
def supported_utility_tokens():
    return {"supported_utility_tokens": list(UTILITY_SCORES.keys())}

# ============================================================
# HELLO ENDPOINT
# ============================================================

@app.get("/hello/{name}", tags=["General"], summary="Say hello")
def say_hello(name: str):
    return {"message": f"Hello {name}! 👋", "api": "AstraScout Crypto API"}

# ============================================================
# UTILITY SCORE ENDPOINT
# ============================================================

@app.get("/utility-score/{symbol}", tags=["Utility"], summary="Get utility score for a token")
def get_utility_score(symbol: str):
    sym = symbol.upper()

    if sym in UTILITY_SCORES:
        return {
            "token": sym,
            "utility_score": UTILITY_SCORES[sym]["utility_score"],
            "summary": UTILITY_SCORES[sym]["summary"],
        }

    return {
        "token": sym,
        "utility_score": 50,
        "summary": "Unknown token — no utility data available.",
    }

# ============================================================
# PRICE ALL TOKENS (MOET BOVEN SINGLE PRICE STAAN)
# ============================================================

@app.get("/price/all", tags=["Prices"], summary="Get USD prices for all supported tokens")
async def get_all_prices():
    ids_str = ",".join(COINGECKO_IDS.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            data = resp.json()
    except Exception as e:
        return {"error": f"Failed to fetch prices: {e}"}

    return {
        sym: {"price_usd": data.get(cid, {}).get("usd")}
        for sym, cid in COINGECKO_IDS.items()
    }

# ============================================================
# PRICE SINGLE TOKEN
# ============================================================

@app.get("/price/{symbol}", tags=["Prices"], summary="Get USD price for a single token")
async def get_price(
    symbol: str = Path(..., regex=r"^[A-Za-z0-9]{2,10}$"),
):
    sym = symbol.upper()

    if sym not in COINGECKO_IDS:
        return {"error": f"Token '{sym}' not supported."}

    cid = COINGECKO_IDS[sym]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            data = resp.json()
    except Exception as e:
        return {"error": f"Failed to fetch price: {e}"}

    return {"token": sym, "price_usd": data.get(cid, {}).get("usd")}
