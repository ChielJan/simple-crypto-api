from fastapi import FastAPI, Path
import httpx
import asyncio
import time

app = FastAPI(
    title="AstraScout Crypto API",
    description=(
        "Multi-source crypto price + utility API.\n\n"
        "Sources (in order): CoinGecko, Binance, CryptoCompare, CoinPaprika.\n"
        "Provides USD prices for 26 major tokens and simple utility scores for 10 tokens.\n"
        "Includes caching and fallback to minimise null prices."
    ),
    version="1.7.1",
)

# ===========================
# CONFIG
# ===========================

PRICE_TTL_SECONDS = 120  # cache geldigheid in seconden

# ===========================
# TOKEN MAPS
# ===========================

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

CRYPTOCOMPARE_MAP = {
    **{symbol: symbol for symbol in COINGECKO_IDS},
    "EGLD": "EGLD,ELGD",
}

PAPRIKA_IDS = {
    "BTC": "btc-bitcoin",
    "ETH": "eth-ethereum",
    "SOL": "sol-solana",
    "BNB": "bnb-binance-coin",
    "XRP": "xrp-xrp",
    "ADA": "ada-cardano",
    "DOGE": "doge-dogecoin",
    "MATIC": "matic-polygon",
    "DOT": "dot-polkadot",
    "LINK": "link-chainlink",
    "TRX": "trx-tron",
    "ATOM": "atom-cosmos",
    "AVAX": "avax-avalanche",
    "LTC": "ltc-litecoin",
    "ETC": "etc-ethereum-classic",
    "UNI": "uni-uniswap",
    "APT": "apt-aptos",
    "ARB": "arb-arbitrum",
    "OP": "op-optimism",
    "FTM": "ftm-fantom",
    "NEAR": "near-near-protocol",
    "XLM": "xlm-stellar",
    "ICP": "icp-internet-computer",
    "FIL": "fil-filecoin",
    "EGLD": "egld-elrond-erd-2",
    "AAVE": "aave-aave",
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

# ===========================
# IN-MEMORY CACHE
# ===========================

# Voorbeeld: { "BTC": {"price": 12345.0, "source": "coingecko", "ts": 1710000000.0} }
PRICE_CACHE: dict[str, dict] = {}


def get_cached_price(symbol: str):
    """Geef cached prijs als die nog 'vers' is, anders None."""
    entry = PRICE_CACHE.get(symbol)
    if not entry:
        return None, None
    age = time.time() - entry["ts"]
    if age <= PRICE_TTL_SECONDS:
        return entry["price"], entry["source"]
    return None, None


def get_any_cached_price(symbol: str):
    """Geef cached prijs ongeacht leeftijd (als laatste redmiddel)."""
    entry = PRICE_CACHE.get(symbol)
    if not entry:
        return None, None
    return entry["price"], entry["source"]


def set_cached_price(symbol: str, price: float, source: str):
    PRICE_CACHE[symbol] = {
        "price": price,
        "source": source,
        "ts": time.time(),
    }


# ===========================
# SOURCE FETCHERS
# ===========================

async def fetch_coingecko(symbol: str):
    ids = COINGECKO_IDS[symbol].split(",")
    async with httpx.AsyncClient() as client:
        for cid in ids:
            try:
                r = await client.get(
                    f"https://api.coingecko.com/api/v3/simple/price"
                    f"?ids={cid}&vs_currencies=usd",
                    timeout=5,
                )
                data = r.json()
                if cid in data and "usd" in data[cid]:
                    return data[cid]["usd"], "coingecko"
            except Exception:
                continue
    return None, None


async def fetch_binance(symbol: str):
    sym = BINANCE_SYMBOLS.get(symbol)
    if not sym:
        return None, None
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://api.binance.com/api/v3/ticker/price?symbol={sym}",
                timeout=5,
            )
            data = r.json()
            if "price" in data:
                return float(data["price"]), "binance"
    except Exception:
        return None, None
    return None, None


async def fetch_cryptocompare(symbol: str):
    symbols = CRYPTOCOMPARE_MAP[symbol].split(",")
    async with httpx.AsyncClient() as client:
        for s in symbols:
            try:
                r = await client.get(
                    f"https://min-api.cryptocompare.com/data/price"
                    f"?fsym={s}&tsyms=USD",
                    timeout=5,
                )
                data = r.json()
                if "USD" in data:
                    return float(data["USD"]), "cryptocompare"
            except Exception:
                continue
    return None, None


async def fetch_paprika(symbol: str):
    paprika_id = PAPRIKA_IDS.get(symbol)
    if not paprika_id:
        return None, None
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://api.coinpaprika.com/v1/tickers/{paprika_id}",
                timeout=5,
            )
            data = r.json()
            if "quotes" in data and "USD" in data["quotes"]:
                return float(data["quotes"]["USD"]["price"]), "coinpaprika"
    except Exception:
        return None, None
    return None, None


# ===========================
# PRICE AGGREGATOR
# ===========================

async def get_price(symbol: str):
    """
    1. Probeer verse cache
    2. Probeer live bronnen (4 stuks)
    3. Als alles faalt maar er is ooit een cache geweest → gebruik laatste bekende
    """

    # 1. Vers uit cache?
    cached_price, cached_source = get_cached_price(symbol)
    if cached_price is not None:
        return cached_price, cached_source

    # 2. Live proberen (sequentieel, om rate limits te beperken)
    for fetcher in (
        fetch_coingecko,
        fetch_binance,
        fetch_cryptocompare,
        fetch_paprika,
    ):
        price, source = await fetcher(symbol)
        if price is not None:
            set_cached_price(symbol, price, source)
            return price, source

    # 3. Laatste redmiddel: oude cache (kan ouder zijn dan TTL)
    stale_price, stale_source = get_any_cached_price(symbol)
    if stale_price is not None:
        return stale_price, stale_source

    return None, None


# ===========================
# ENDPOINTS
# ===========================

@app.get("/", summary="API status & supported tokens")
def root():
    return {
        "message": "AstraScout Crypto API Online 🚀",
        "status": "online",
        "supported_price_tokens": list(COINGECKO_IDS.keys()),
        "supported_utility_tokens": list(UTILITY_SCORES.keys()),
    }


@app.get("/supported/price", summary="List all supported price tokens")
def supported_price():
    return {"supported_price_tokens": list(COINGECKO_IDS.keys())}


@app.get("/supported/utility", summary="List all supported utility tokens")
def supported_utility():
    return {"supported_utility_tokens": list(UTILITY_SCORES.keys())}


@app.get("/hello/{name}", summary="Greeting endpoint")
def hello(name: str):
    return {"message": f"Hello {name} 👋"}


@app.get("/price/all", summary="Get prices for all supported tokens")
async def price_all():
    out = {}
    # sequentieel i.p.v. 26 parallel requests → minder rate limiting
    for sym in COINGECKO_IDS:
        price, source = await get_price(sym)
        out[sym] = {"price_usd": price, "source": source}
    return out


@app.get(
    "/price/{symbol}",
    summary="Get price for a single token",
)
async def price_single(
    symbol: str = Path(..., regex=r"^[A-Za-z0-9]{2,10}$")
):
    sym = symbol.upper()
    if sym not in COINGECKO_IDS:
        return {"error": f"Token '{sym}' not supported."}

    price, source = await get_price(sym)
    return {"token": sym, "price_usd": price, "source": source}


@app.get(
    "/utility-score/{symbol}",
    summary="Get utility score for major tokens",
)
def utility(symbol: str):
    sym = symbol.upper()
    if sym in UTILITY_SCORES:
        return {"token": sym, **UTILITY_SCORES[sym]}
    return {"token": sym, "utility_score": 50, "summary": "Unknown token."}
