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

Sources:
- CoinGecko (primary)
- Binance (fallback)
- CryptoCompare (fallback)

Maintained by **AstraScout**
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

BINANCE_SYMBOLS = {symbol: symbol + "USDT" for symbol in COINGECKO_IDS}

UTILITY_SCORES = {
    "BTC": {"utility_score": 95, "summary": "Global store of value and settlement asset."},
    "ETH": {"utility_score": 100, "summary": "Smart contract leader powering DeFi & NFTs."},
    "SOL": {"utility_score": 88, "summary": "Fast high-throughput blockchain."},
    "BNB": {"utility_score": 85, "summary": "Exchange chain with massive usage."},
    "XRP": {"utility_score": 75, "summary": "Cross-border settlement focus."},
    "ADA": {"utility_score": 60, "summary": "Research-driven chain."},
    "DOGE": {"utility_score": 30, "summary": "Meme power, limited utility."},
    "MATIC": {"utility_score": 80, "summary": "Major scaling chain."},
    "DOT": {"utility_score": 78, "summary": "Interoperability hub."},
    "LINK": {"utility_score": 90, "summary": "Top oracle network."},
}

# ============================================================
# PRICE FETCHERS
# ============================================================

async def fetch_from_coingecko(symbol: str):
    ids = COINGECKO_IDS[symbol].split(",")
    async with httpx.AsyncClient() as client:
        for cid in ids:
            try:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd"
                r = await client.get(url, timeout=5)
                data = r.json()
                if cid in data and "usd" in data[cid]:
                    return data[cid]["usd"], "coingecko"
            except:
                continue
    return None, None


async def fetch_from_binance(symbol: str):
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
# PRICE AGGREGATOR (3-SOURCE LOGIC)
# ============================================================

async def get_price_multi_source(symbol: str):
    # Try CoinGecko
    price, source = await fetch_from_coingecko(symbol)
    if price is not None:
        return price, source

    # Try Binance
    price, source = await fetch_from_binance(symbol)
    if price is not None:
        return price, source

    # Try CryptoCompare
    price, source = await fetch_from_cryptocompare(symbol)
    if price is not None:
        return price, source

    return None, None


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
    }


@app.get("/hello/{name}", tags=["General"])
def hello(name: str):
    return {"message": f"Hello {name} 👋", "api": "AstraScout Crypto API"}


@app.get("/supported/price", tags=["General"])
def supported_price():
    return {"supported_price_tokens": list(COINGECKO_IDS.keys())}


@app.get("/supported/utility", tags=["General"])
def supported_utility():
    return {"supported_utility_tokens": list(UTILITY_SCORES.keys())}


# ============================================================
# PRICE — ALL TOKENS  (IMPORTANT: MUST BE ABOVE SINGLE PRICE)
# ============================================================

@app.get("/price/all", tags=["Prices"], summary="Get prices for all tokens")
async def price_all():
    tasks = {sym: asyncio.create_task(get_price_multi_source(sym)) for sym in COINGECKO_IDS}
    results = {}

    for sym, task in tasks.items():
        price, source = await task
        results[sym] = {"price_usd": price, "source": source}

    return results


# ============================================================
# PRICE — SINGLE TOKEN
# ============================================================

@app.get("/price/{symbol}", tags=["Prices"], summary="Get price for one token")
async def price_single(
    symbol: str = Path(..., regex=r"^[A-Za-z0-9]{2,10}$")
):
    sym = symbol.upper()

    if sym not in COINGECKO_IDS:
        return {"error": f"Token '{sym}' not supported."}

    price, source = await get_price_multi_source(sym)

    return {"token": sym, "price_usd": price, "source": source}


# ============================================================
# UTILITY SCORE
# ============================================================

@app.get("/utility-score/{symbol}", tags=["Utility"])
def utility(symbol: str):
    sym = symbol.upper()
    if sym in UTILITY_SCORES:
        return {"token": sym, **UTILITY_SCORES[sym]}
    return {"token": sym, "utility_score": 50, "summary": "Unknown token."}
