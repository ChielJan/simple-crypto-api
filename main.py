from fastapi import FastAPI, Path
import httpx
import asyncio

app = FastAPI(
    title="AstraScout Crypto API",
    description="""
A professional multi-source crypto price + utility API 🚀  

Sources used (in order):
1. CoinGecko (primary)
2. Binance (fallback)
3. CryptoCompare (fallback)
4. CoinPaprika (fallback — guarantees a price)

Designed & maintained by AstraScout.
""",
    version="1.6.0",
)

# ============================================================
# TOKEN MAPS
# ============================================================

# CoinGecko IDs (with fallbacks)
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
    "EGLD": "multiversx",  # CG ID for EGLD is "multiversx"
    "AAVE": "aave",
}

# Binance symbols
BINANCE_SYMBOLS = {symbol: symbol + "USDT" for symbol in COINGECKO_IDS}

# CryptoCompare mapping (your EGLD=EGLD,ELGD rule)
CRYPTOCOMPARE_MAP = {
    **{symbol: symbol for symbol in COINGECKO_IDS},
    "EGLD": "EGLD,ELGD",
}

UTILITY_SCORES = {
    "BTC": {"utility_score": 95, "summary": "Global store of value."},
    "ETH": {"utility_score": 100, "summary": "Smart contract leader."},
    "SOL": {"utility_score": 88, "summary": "Fast scalable blockchain."},
    "BNB": {"utility_score": 85, "summary": "Exchange chain with mass adoption."},
    "XRP": {"utility_score": 75, "summary": "Cross-border payment asset."},
    "ADA": {"utility_score": 60, "summary": "Research-driven chain."},
    "DOGE": {"utility_score": 30, "summary": "High meme utility."},
    "MATIC": {"utility_score": 80, "summary": "Major scaling chain."},
    "DOT": {"utility_score": 78, "summary": "Interoperability ecosystem."},
    "LINK": {"utility_score": 90, "summary": "Top oracle provider."},
}

# ============================================================
# SOURCE FETCHERS
# ============================================================

async def fetch_coingecko(symbol: str):
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


async def fetch_binance(symbol: str):
    sym = BINANCE_SYMBOLS.get(symbol)
    if not sym:
        return None, None
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://api.binance.com/api/v3/ticker/price?symbol={sym}", timeout=5
            )
            data = r.json()
            if "price" in data:
                return float(data["price"]), "binance"
    except:
        return None, None
    return None, None


async def fetch_cryptocompare(symbol: str):
    symbols = CRYPTOCOMPARE_MAP[symbol].split(",")
    async with httpx.AsyncClient() as client:
        for s in symbols:
            try:
                r = await client.get(
                    f"https://min-api.cryptocompare.com/data/price?fsym={s}&tsyms=USD",
                    timeout=5,
                )
                data = r.json()
                if "USD" in data:
                    return float(data["USD"]), "cryptocompare"
            except:
                continue
    return None, None


async def fetch_paprika(symbol: str):
    try:
        async with httpx.AsyncClient() as client:
            # Paprika uses lowercase id lookup by /tickers/{id}
            r = await client.get(
                f"https://api.coinpaprika.com/v1/tickers/{symbol.lower()}",
                timeout=5,
            )
            data = r.json()
            if "quotes" in data and "USD" in data["quotes"]:
                return float(data["quotes"]["USD"]["price"]), "coinpaprika"
    except:
        return None, None
    return None, None


# ============================================================
# PRICE AGGREGATOR (4 sources)
# ============================================================

async def get_price(symbol: str):
    # 1. CoinGecko
    price, source = await fetch_coingecko(symbol)
    if price is not None:
        return price, source

    # 2. Binance
    price, source = await fetch_binance(symbol)
    if price is not None:
        return price, source

    # 3. CryptoCompare
    price, source = await fetch_cryptocompare(symbol)
    if price is not None:
        return price, source

    # 4. CoinPaprika (guaranteed fallback)
    price, source = await fetch_paprika(symbol)
    if price is not None:
        return price, source

    return None, None


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AstraScout Crypto API Online 🚀",
        "status": "online",
        "supported_price_tokens": list(COINGECKO_IDS.keys()),
        "supported_utility_tokens": list(UTILITY_SCORES.keys()),
    }


@app.get("/supported/price")
def supported_price():
    return {"supported_price_tokens": list(COINGECKO_IDS.keys())}


@app.get("/supported/utility")
def supported_utility():
    return {"supported_utility_tokens": list(UTILITY_SCORES.keys())}


@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello {name} 👋"}


# ============================================================
# PRICE ALL (must be ABOVE single-price)
# ============================================================

@app.get("/price/all")
async def price_all():
    tasks = {sym: asyncio.create_task(get_price(sym)) for sym in COINGECKO_IDS}
    out = {}
    for sym, task in tasks.items():
        price, source = await task
        out[sym] = {"price_usd": price, "source": source}
    return out


# ============================================================
# PRICE SINGLE
# ============================================================

@app.get("/price/{symbol}")
async def price_single(
    symbol: str = Path(..., regex=r"^[A-Za-z0-9]{2,10}$")
):
    sym = symbol.upper()
    if sym not in COINGECKO_IDS:
        return {"error": f"Token '{sym}' not supported."}

    price, source = await get_price(sym)

    return {"token": sym, "price_usd": price, "source": source}


# ============================================================
# UTILITY SCORE
# ============================================================

@app.get("/utility-score/{symbol}")
def utility(symbol: str):
    sym = symbol.upper()
    if sym in UTILITY_SCORES:
        return {"token": sym, **UTILITY_SCORES[sym]}
    return {"token": sym, "utility_score": 50, "summary": "Unknown token."}
