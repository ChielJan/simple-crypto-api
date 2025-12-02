from fastapi import FastAPI, Path
import httpx

app = FastAPI(
    title="AstraScout Crypto API",
    description="Lightweight crypto price + utility API built step-by-step 🚀",
    version="1.3.0",
)

# ------------------------------------
# TOKEN MAPPINGS & UTILITY SCORES
# ------------------------------------
COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "MATIC": "polygon",
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
    "ADA": {"utility_score": 60, "summary": "Strong research focus, slower real-world adoption."},
    "DOGE": {"utility_score": 30, "summary": "High meme power, limited functional utility."},
    "MATIC": {"utility_score": 80, "summary": "Scaling solution with many live dApps."},
    "DOT": {"utility_score": 78, "summary": "Interoperability-focused ecosystem."},
    "LINK": {"utility_score": 90, "summary": "Leading oracle network connecting on/off-chain data."},
}


# ------------------------------------
# ROOT & HELLO
# ------------------------------------
@app.get("/", tags=["General"], summary="API status")
def root():
    return {
        "message": "AstraScout Crypto API Online 🚀",
        "endpoints": [
            "/price/all",
            "/price/{symbol}",
            "/utility-score/{symbol}",
            "/hello/{name}",
        ],
        "tokens_supported": list(COINGECKO_IDS.keys()),
    }


@app.get("/hello/{name}", tags=["General"], summary="Say hello")
def say_hello(name: str):
    return {"message": f"Hello {name}! 👋", "api": "AstraScout Crypto API"}


# ------------------------------------
# UTILITY SCORE ENDPOINT
# ------------------------------------
@app.get(
    "/utility-score/{symbol}",
    tags=["Utility"],
    summary="Get simple utility score for a token",
)
def get_utility_score(symbol: str):
    sym = symbol.upper()

    if sym in UTILITY_SCORES:
        data = UTILITY_SCORES[sym]
        return {
            "token": sym,
            "utility_score": data["utility_score"],
            "summary": data["summary"],
        }

    return {
        "token": sym,
        "utility_score": 50,
        "summary": "Unknown token — no utility data available.",
    }


# ------------------------------------
# PRICE FOR ALL TOKENS
# ------------------------------------
@app.get(
    "/price/all",
    tags=["Prices"],
    summary="Get USD prices for all supported tokens",
)
async def get_all_prices():
    ids_str = ",".join(COINGECKO_IDS.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            data = resp.json()
    except Exception as e:
        return {"error": f"Failed to fetch prices: {e}"}

    result = {}
    for sym, cg_id in COINGECKO_IDS.items():
        price = data.get(cg_id, {}).get("usd", None)
        result[sym] = {"price_usd": price}

    return result


# ------------------------------------
# PRICE FOR SINGLE TOKEN
# ------------------------------------
@app.get(
    "/price/{symbol}",
    tags=["Prices"],
    summary="Get USD price for a single token",
)
async def get_price(
    symbol: str = Path(..., regex=r"^[A-Za-z0-9]{2,10}$"),
):
    sym = symbol.upper()

    if sym not in COINGECKO_IDS:
        return {"error": f"Token '{sym}' not supported."}

    cg_id = COINGECKO_IDS[sym]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            data = resp.json()
    except Exception as e:
        return {"error": f"Failed to fetch price: {e}"}

    return {"token": sym, "price_usd": data.get(cg_id, {}).get("usd", None)}
