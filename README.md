🚀 AstraScout Crypto API

A lightweight, multi-source cryptocurrency price API with smart fallback and caching.

The AstraScout Crypto API provides fast and reliable USD price data for 26 major cryptocurrencies using an intelligent multi-source aggregator:

CoinGecko (primary)

Binance

CryptoCompare

CoinPaprika (final fallback)

On top of that, the API uses in-memory caching and a “last known price” fallback to minimise null responses and smooth over short provider outages or rate limits.

It also includes simple utility scores for 10 well-known tokens.

This API is designed to be fast, practical, and highly stable — perfect for bots, dashboards, Web3 apps, or educational projects.

✨ Features

Live USD prices for 26 cryptocurrencies

Automatic multi-source fallback across 4 providers

Caching with a short TTL to reduce rate limits

Fallback to the last known price if all live sources fail

Utility score endpoint for 10 major tokens

High performance (async FastAPI)

No API key required

Small, clean JSON payloads

Developer-friendly endpoints

Note: In rare cases (e.g. when a token has never resolved before), null may still occur.
For all previously resolved tokens, the API returns either a fresh price or the last known price.

🪙 Supported Price Tokens (26)

BTC, ETH, SOL, BNB, XRP, ADA, DOGE, MATIC, DOT, LINK,
TRX, ATOM, AVAX, LTC, ETC, UNI, APT, ARB, OP, FTM,
NEAR, XLM, ICP, FIL, EGLD, AAVE

Retrieve them via:
GET /supported/price

⭐ Supported Utility Score Tokens (10)

BTC, ETH, SOL, BNB, XRP, ADA, DOGE, MATIC, DOT, LINK

Retrieve them via:
GET /supported/utility

📡 Endpoints
Health & Metadata

GET /

Get All Prices

GET /price/all
Returns all 26 price entries with source info.

Get Price for a Single Token

GET /price/{symbol}
Examples: /price/BTC, /price/MATIC, /price/EGLD

Utility Score

GET /utility-score/{symbol}

🧠 How the Multi-Source Fallback Works

For every token, the API attempts:

CoinGecko

Binance

CryptoCompare

CoinPaprika

The first successful price is returned and cached.
If all live sources fail but a cached price exists, the last known price is returned instead.

This system:

Greatly reduces null values

Avoids downtime during provider outages

Makes the API more reliable than single-source feeds

Works extremely well for bots & dashboards

📌 Example Usage

Python:

import requests
r = requests.get("https://YOUR_BASE_URL/price/BTC").json()
print(r)

JavaScript:

fetch("https://YOUR_BASE_URL/price/all")
 .then(res => res.json())
 .then(console.log)

🚀 Tech Stack

Python

FastAPI

Asyncio

httpx

In-memory caching

🤝 Credits

Built by AstraScout — combining Web3 curiosity with practical developer tools.

📜 License

MIT License.
