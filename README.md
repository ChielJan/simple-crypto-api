# 🚀 AstraScout Crypto API  
A lightweight, multi-source cryptocurrency price API with zero-null fallback logic.

The AstraScout Crypto API provides fast and reliable USD price data for 26 major cryptocurrencies using an intelligent multi-source aggregator:

1. CoinGecko (primary)  
2. Binance  
3. CryptoCompare  
4. CoinPaprika (final fallback → no null values)

It also includes simple utility scores for 10 well-known tokens.

This API is designed to be fast, practical, and extremely stable — perfect for bots, dashboards, Web3 apps, or educational projects.

---

## ✨ Features

- Live USD prices for 26 cryptocurrencies  
- Automatic multi-source fallback (4 providers)  
- Zero null values — always returns a price  
- Utility score endpoint  
- High performance (async)  
- No API key required  
- Small, clean JSON payloads  
- Developer-friendly endpoints  

---

## 🪙 Supported Price Tokens (26)

BTC, ETH, SOL, BNB, XRP, ADA, DOGE, MATIC, DOT, LINK,  
TRX, ATOM, AVAX, LTC, ETC, UNI, APT, ARB, OP, FTM,  
NEAR, XLM, ICP, FIL, EGLD, AAVE

Retrieve them via:  
GET /supported/price

---

## ⭐ Supported Utility Score Tokens (10)

BTC, ETH, SOL, BNB, XRP, ADA, DOGE, MATIC, DOT, LINK

Retrieve them via:  
GET /supported/utility

---

## 📡 Endpoints

### Health & Metadata  
GET /

Returns API status and supported token lists.

---

### Get Price for All Tokens  
GET /price/all

Returns a dictionary with 26 tokens, each containing for example:

    {
      "price_usd": 138.45,
      "source": "coingecko"
    }

---

### Get Price for a Single Token  
GET /price/{symbol}

Examples:

    /price/BTC
    /price/MATIC
    /price/EGLD

---

### Utility Score  
GET /utility-score/{symbol}

Returns a simple 0–100 score plus a short summary, for example:

    {
      "token": "ETH",
      "utility_score": 100,
      "summary": "Smart contract leader."
    }

---

## 🧠 How the Multi-Source Fallback Works

For every token, the API attempts to fetch the price from:

1. CoinGecko  
2. Binance  
3. CryptoCompare  
4. CoinPaprika  

The first successful response is returned, including the name of the source.

This ensures:

- No null prices  
- Minimal downtime  
- Higher reliability than single-source APIs  
- Ideal for bots or dashboards needing consistent data  

---

## 📌 Example Usage

### Python

    import requests
    data = requests.get("https://YOUR-URL/price/BTC").json()
    print(data)

### JavaScript

    fetch("https://YOUR-URL/price/all")
      .then(res => res.json())
      .then(console.log);

---

## 🚀 Deploying Yourself

Built with:

- FastAPI  
- Python  
- Asyncio  
- httpx  

Deploy easily on platforms like Railway, Render, Fly.io, etc.

---

## 🤝 Credits

Built by AstraScout — combining Web3 curiosity with practical tools.

---

## 📜 License

MIT License – free to use, modify, and build upon.
