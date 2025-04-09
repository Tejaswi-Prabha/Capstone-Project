from fastapi import FastAPI, HTTPException
import requests
import pandas as pd
from functools import lru_cache
from config import (
    ALPHA_VANTAGE_API_KEY, GOOGLE_FINANCE_API_KEY, 
    ALPHA_VANTAGE_BASE_URL, GOOGLE_FINANCE_BASE_URL
)

app = FastAPI()

@lru_cache(maxsize=10)
def get_stock_data_alpha(symbol: str):
    """Fetch stock data from Alpha Vantage."""
    url = f"{ALPHA_VANTAGE_BASE_URL}?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
    return fetch_stock_data(url)

@lru_cache(maxsize=10)
def get_stock_data_google(query: str):
    """Fetch stock data from Google Finance (via SerpAPI)."""
    url = f"{GOOGLE_FINANCE_BASE_URL}?engine=google_finance&q={query}&api_key={GOOGLE_FINANCE_API_KEY}"
    return fetch_stock_data(url)

def fetch_stock_data(url: str):
    """Generic function to fetch stock data from an API URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data:
            raise HTTPException(status_code=400, detail="Invalid stock symbol or API limit exceeded.")

        return data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

@app.get("/stock/{symbol}/alpha")
def stock_analysis_alpha(symbol: str):
    return get_stock_data_alpha(symbol)

@app.get("/stock/{query}/google")
def stock_analysis_google(query: str):
    return get_stock_data_google(query)
