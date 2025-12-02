from fastapi import FastAPI, Path
import httpx
import asyncio

app = FastAPI(
    title="AstraScout Crypto API",
    description="""
A professional multi-source crypto price + utility API 🚀  

---

### 🔥 Supported Price Tokens (26)
BTC, ETH, SOL, BNB, XRP, ADA, DOGE, MATIC, DOT, LINK,  
TRX, ATOM, AVAX, LTC, ETC, UNI, APT, ARB, OP,  
FTM, NEAR, XLM, ICP, FIL, EGLD, AAVE  

### 🔵 Supported Utility Tokens (10)
BTC, ETH, SOL, BNB, XRP, ADA, DOGE, MATIC, DOT, LINK  

---

Powered by:
- CoinGecko (primary)
- Binance (fallback)
- CryptoCompare (fallback)

Built & maintained by **AstraScout** ⚡  
""",
    version="1.5.0",
)

# ============================================================
# TOKEN MAPS
# ============================================================

COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "MATIC": "matic-network,matic,polygon-ecosystem-token",
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

# Binance symbol mapping (TokenUSDT)
BINANCE_SYMBOLS = {
    symbol: symbol + "USDT"
    for symbol in COINGECKO_IDS.keys()
}

UTILITY_SCORES = {
    "BTC": {"utility_score": 95, "summary": "Global store of value and settlement asset."},
    "ETH": {"utility_score": 100, "summary": "Smart contract leader powering DeFi & NFTs."},
    "SOL": {"utility_score": 88, "summary": "Fast, scalable chain with strong ecosystem growth."},
    "BNB": {"utility_score": 85, "summary": "Exchange chain with massive retail usage."},
    "XRP": {"utility_score": 75, "summary": "Used for fast cross-border settlement."},
    "ADA": {"utility_score": 60, "summary": "Research-driven chain with slower adoption."},
    "DOGE": {"utility_score": 30, "summary": "High meme utility, limited functional use."},
    "MATIC": {"utility_score": 80, "summary": "Scaling chain with strong real usage."},
    "DOT": {"utility_score": 78, "summary": "Interoperability-focused ecosystem."},
    "LINK": {"utility_score": 90, "summary": "Leading oracle system feeding real-world data."},
}

# ============================================================
# PRICE FETCHERS
# ============================================================

async def fetch_from_coingecko(symbol: str):
    """Try multiple fallback CoinGecko IDs"""
    ids = COINGECKO_IDS[symbol].split(",")

    async with httpx.AsyncClient() as client:
        for cid in ids:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd"
            try:
                r = await client.get(url, timeout=5)
                data = r.json()
                if cid in data and "usd" in data[cid]:
                    return data[cid]["usd"], "coingecko"
            except:
                continue
    return None, None


async def fetch_from_binance(symbol: str):
    """Use Binance global ticker"""
    binance_symbol = BINANCE_SYMBOLS.get(symbol)

    if not binance_symbol:
        return None, None

    url = f"https://api.binance.com/api/v3/ticker/price?symbol={binance_symbol}"

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=5)
            data = r.json()

            if "price" in data:
                return float(data["price"]), "binance"

    except:
        return None, None

    return None, None


async def fetch_from_cryptocompare(symbol: str):
    url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=5)
            data = r.json()

            if "USD" in data:
                return float(data["USD"]), "cryptocompare"

    except:
        return None, None

    return None, None


# ============================================================
# PRICE AGGREGATOR (3-SOURCE)
# ============================================================

async def get_price_multi_source(symbol: str):
    """Try CoinGecko → Binance → CryptoCompare"""

    # 1️⃣ CoinGecko
    price, source = await fetch_from_coingecko(symbol)
    if price is not None:
        return price, source

    # 2️⃣ Binance
    price, source = await fetch_from_binance(symbol)
    if price is not None:
        return price, source

    # 3️⃣ CryptoCompare
    price, source = await fetch_from_cryptocompare(symbol)
    if price is not None:
        return price, source

    return None, None  # all failed


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", tags=["General"])
def root():
    return {
        "message": "AstraScout Crypto API Online 🚀",
        "status": "online",
        "supported_price_tokens": list(COINGECKO_IDS.keys()),
        "supported_utility_tokens": list(UTILITY_SCORES.keys()),
        "endpoints": {
            "price_single": "/price/{symbol}",
            "price_all": "/price/all",
            "utility_single": "/utility-score/{symbol}",
            "supported_price": "/supported/price",
            "supported_utility": "/supported/utility",
        },
    }


@app.get("/hello/{name}", tags=["General"])
def say_hello(name: str):
    return {"message": f"Hello {name}! 👋", "api": "AstraScout Crypto API"}


@app.get("/supported/price", tags=["General"])
def supported_price_tokens():
    return {"supported_price_tokens": list(COINGECKO_IDS.keys())}


@app.get("/supported/utility", tags=["General"])
def supported_utility_tokens():
    return {"supported_utility_tokens": list(UTILITY_SCORES.keys())}


# ============================================================
# UTILITY SCORE
# ============================================================

@app.get("/utility-score/{symbol}", tags=["Utility"])
def get_utility_score(symbol: str):
    sym = symbol.upper()
    if sym in UTILITY_SCORES:
        return {
            "token": sym,
            "utility_score": UTILITY_SCORES[sym]["utility_score"],
            "summary": UTILITY_SCORES[sym]["summary"],
        }
    return {"token": sym, "utility_score": 50, "summary": "Unknown token."}


# ============================================================
# PRICE — SINGLE TOKEN
# ============================================================

@app.get("/price/{symbol}", tags=["Prices"])
async def price_single(
    symbol: str = Path(..., regex=r"^[A-Za-z0-9]{2,10}$")
):
    sym = symbol.upper()

    if sym not in COINGECKO_IDS:
        return {"error": f"Token '{sym}' not supported."}

    price, source = await get_price_multi_source(sym)

    return {"token": sym, "price_usd": price, "source": source}


# ============================================================
# PRICE — ALL TOKENS
# ============================================================

@app.get("/price/all", tags=["Prices"])
async def price_all():
    results = {}

    tasks = {
        symbol: asyncio.create_task(get_price_multi_source(symbol))
        for symbol in COINGECKO_IDS.keys()
    }

    for symbol, task in tasks.items():
        price, source = await task
        results[symbol] = {"price_usd": price, "source": source}

    return results
