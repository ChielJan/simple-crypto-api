from fastapi import FastAPI, Path
import httpx

app = FastAPI(
    title="AstraScout Crypto API",
    description="Lightweight crypto price + utility API built step-by-step 🚀",
    version="1.2.2",
)

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


# ---------------------------
# ROOT
# ---------------------------
@app.get("/")
def root():
    return {
        "message": "AstraScout Crypto API Online 🚀",
        "endpoints": ["/price/all", "/price/{symbol}", "/utility-score/{symbol}"],
    }


# ---------------------------
# PRICE ALL — FIXED
# ---------------------------
@app.get("/price/all", tags=["Prices"], summary="Get all supported token prices")
async def price_all():
    ids_str = ",".join(COINGECKO_IDS.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            data = resp.json()
    except Exception as e:
        return {"error": f"Failed to fetch prices: {e}"}

    return {
        sym: {"price_usd": data.get(cid, {}).get("usd")}
        for sym, cid in COINGECKO_IDS.items()
    }


# ---------------------------
# PRICE SINGLE — Regex FIX
# ---------------------------
@app.get(
    "/price/{symbol}",
    tags=["Prices"],
    summary="Get price of a single token"
)
async def price_single(
    symbol: str = Path(..., regex="^[A-Za-z]{2,6}$")
):
    sym = symbol.upper()

    if sym not in COINGECKO_IDS:
        return {"error": f"Token '{sym}' not supported."}

    cid = COINGECKO_IDS[sym]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            data = resp.json()
    except Exception as e:
        return {"error": f"Failed to fetch price: {e}"}

    return {"token": sym, "price_usd": data.get(cid, {}).get("usd")}
