#!/usr/bin/env python3
# soko-mcp — Commodity Price Intelligence MCP Server
# © 2026 Gabriel Mahia / AI Kung Fu LLC — MIT License
#
# The problem: Kenya smallholder farmers make sell/hold decisions with zero price data.
# A maize farmer in Nakuru doesn't know that Nairobi prices are 40% higher that week.
# The information asymmetry flows upward — traders know, farmers don't.
# Western parallel: CME Group commodity futures, USDA NASS reports, Reuters Commodities
# African context: EAGC (East Africa Grain Council) collects data but it's hard to access
# Research: "Information and Communication Technology and Agricultural Markets" (World Bank, 2016)
#           "Mobile Phones and Agricultural Performance" (Suri & Jack, 2016)
#
# TRUST INTEGRITY: All prices are DEMO/synthetic. Verify at EAGC, KALRO, or county markets.
# =============================================================================

from __future__ import annotations
import datetime
import random
from typing import Annotated
from fastmcp import FastMCP

mcp = FastMCP(
    name="soko-mcp",
    instructions="""Kenya commodity price intelligence MCP server.
    Provides tools for market price queries, regional comparisons, trend analysis,
    and sell/hold decision support for farmers and traders.
    
    IMPORTANT: All prices are DEMO/synthetic for educational purposes.
    Real prices: EAGC (eagc.org), KALRO (kalro.org), county market boards.
    Not affiliated with any commodity exchange.
    """,
)

TODAY = datetime.date.today()
MONTH = TODAY.month

# DEMO commodity price database (KES per 90kg bag unless noted)
# Seasonal patterns built in. All DEMO — verify at eagc.org, kalro.org
_BASE_PRICES = {
    "maize":    {"nairobi": 3200, "nakuru": 2800, "eldoret": 2600, "kisumu": 3000, "mombasa": 3500, "unit": "90kg bag"},
    "beans":    {"nairobi": 12000, "nakuru": 10500, "eldoret": 10000, "kisumu": 11000, "mombasa": 12500, "unit": "90kg bag"},
    "wheat":    {"nairobi": 4500, "nakuru": 4200, "eldoret": 4000, "kisumu": 4600, "mombasa": 4800, "unit": "90kg bag"},
    "potatoes": {"nairobi": 2800, "nakuru": 1800, "eldoret": 1600, "kisumu": 2500, "mombasa": 3000, "unit": "50kg bag"},
    "tomatoes": {"nairobi": 4000, "nakuru": 2500, "eldoret": 2200, "kisumu": 3500, "mombasa": 4500, "unit": "crate (64kg)"},
    "avocados": {"nairobi": 8000, "nakuru": 6000, "eldoret": 5500, "kisumu": 7000, "mombasa": 9000, "unit": "bag (60 pieces)"},
    "tea_bulk": {"nairobi": 200, "nakuru": 180, "eldoret": 170, "kisumu": 210, "mombasa": 220, "unit": "kg"},
    "coffee_parchment": {"nairobi": 120, "nakuru": 100, "eldoret": 95, "kisumu": 110, "mombasa": 125, "unit": "kg"},
    "sugarcane": {"nairobi": 0, "nakuru": 4200, "eldoret": 3800, "kisumu": 4500, "mombasa": 0, "unit": "tonne"},
    "onions":   {"nairobi": 6000, "nakuru": 4500, "eldoret": 4000, "kisumu": 5500, "mombasa": 6500, "unit": "50kg bag"},
    "kale_sukuma": {"nairobi": 30, "nakuru": 20, "eldoret": 18, "kisumu": 25, "mombasa": 35, "unit": "bunch"},
    "milk":     {"nairobi": 60, "nakuru": 45, "eldoret": 40, "kisumu": 50, "mombasa": 65, "unit": "litre"},
    "chicken":  {"nairobi": 600, "nakuru": 500, "eldoret": 450, "kisumu": 550, "mombasa": 650, "unit": "kg live"},
    "eggs":     {"nairobi": 15, "nakuru": 13, "eldoret": 12, "kisumu": 14, "mombasa": 16, "unit": "piece"},
}

# Seasonal multipliers (month index 1-12)
# Long rains harvest (June-July): +supply = lower prices
# Short rains harvest (Dec-Jan): +supply = lower prices
# Lean seasons (Feb-May, Aug-Nov): higher prices
_SEASONAL = {
    1: 0.90, 2: 1.10, 3: 1.15, 4: 1.10, 5: 1.05,
    6: 0.85, 7: 0.80, 8: 1.00, 9: 1.05, 10: 1.10,
    11: 1.05, 12: 0.90
}

def _price(commodity, market):
    base = _BASE_PRICES.get(commodity, {}).get(market.lower())
    if not base: return None
    return int(base * _SEASONAL.get(MONTH, 1.0))


@mcp.tool(
    description=(
        "Query current commodity prices at Kenya markets. "
        "Western parallel: CME Group spot price query, USDA Agricultural Marketing Service. "
        "DEMO prices — verify at eagc.org or county market boards."
    ),
    annotations={"readOnlyHint": True},
)
def commodity_price_query(
    commodity: Annotated[str, "Commodity: maize, beans, wheat, potatoes, tomatoes, avocados, tea_bulk, coffee_parchment, sugarcane, onions, kale_sukuma, milk, chicken, eggs"],
    market: Annotated[str, "Market: nairobi, nakuru, eldoret, kisumu, mombasa"],
) -> dict:
    price = _price(commodity.lower(), market.lower())
    if price is None:
        available = list(_BASE_PRICES.get(commodity.lower(), {}).keys())
        return {"status": "NOT_FOUND",
                "message": f"No data for {commodity} in {market}",
                "markets_with_data": available}

    info = _BASE_PRICES[commodity.lower()]
    season = ("HARVEST (supply high, prices lower)" if MONTH in (6,7,12,1)
              else "LEAN (supply lower, prices higher)" if MONTH in (2,3,4,5,8,9,10,11)
              else "MID-SEASON")

    return {
        "status": "OK",
        "commodity": commodity,
        "market": market,
        "price_kes": price,
        "unit": info["unit"],
        "date": TODAY.isoformat(),
        "season": season,
        "note": "DEMO — Synthetic price. Verify at eagc.org, KALRO, or the local market board.",
        "source": "soko-mcp DEMO dataset. Reference: EAGC market data format.",
    }


@mcp.tool(
    description=(
        "Compare commodity prices across all Kenya markets to find the best price. "
        "Western parallel: CME regional basis reports, DTN ProphetX. "
        "This is the 'should I take my maize to Nairobi or sell locally?' tool. "
        "DEMO prices."
    ),
    annotations={"readOnlyHint": True},
)
def regional_price_comparison(
    commodity: Annotated[str, "Commodity to compare (maize, beans, wheat, potatoes, avocados, etc.)"],
    farmer_location: Annotated[str, "Farmer's location/county (for transport cost context)"],
) -> dict:
    markets = ["nairobi", "nakuru", "eldoret", "kisumu", "mombasa"]
    prices = {}
    for m in markets:
        p = _price(commodity.lower(), m)
        if p: prices[m] = p

    if not prices:
        return {"status": "NOT_FOUND", "message": f"No regional data for {commodity}"}

    sorted_markets = sorted(prices.items(), key=lambda x: x[1], reverse=True)
    best_market, best_price = sorted_markets[0]
    worst_market, worst_price = sorted_markets[-1]
    spread_kes = best_price - worst_price
    spread_pct = round(spread_kes / worst_price * 100, 1)

    unit = _BASE_PRICES.get(commodity.lower(), {}).get("unit", "unit")

    return {
        "status": "OK",
        "commodity": commodity,
        "comparison_date": TODAY.isoformat(),
        "prices_by_market": {m: {"price_kes": p, "unit": unit} for m, p in sorted_markets},
        "best_market": {"market": best_market, "price_kes": best_price},
        "worst_market": {"market": worst_market, "price_kes": worst_price},
        "price_spread": {"kes": spread_kes, "percent": f"{spread_pct}%"},
        "transport_note": (
            f"Price spread of KES {spread_kes:,} across markets. "
            f"Transport from {farmer_location} to {best_market}: estimate KES 2,000-8,000/tonne "
            f"(actual: check county cooperatives or boda boda aggregators). "
            f"Net benefit calculation required before deciding to transport."
        ),
        "arbitrage_opportunity": spread_pct > 15,
        "note": "DEMO — Synthetic prices. Verify at eagc.org before making transport decisions.",
        "source": "soko-mcp DEMO dataset.",
    }


@mcp.tool(
    description=(
        "Analyse price trends for a commodity to inform sell/hold timing. "
        "Western parallel: CME seasonal charts, DTN market commentary. "
        "DEMO historical simulation."
    ),
    annotations={"readOnlyHint": True},
)
def price_trend_analysis(
    commodity: Annotated[str, "Commodity to analyse"],
    market: Annotated[str, "Market: nairobi, nakuru, eldoret, kisumu, mombasa"],
    months_ahead: Annotated[int, "Forecast horizon in months (1-6)"] = 3,
) -> dict:
    base = _BASE_PRICES.get(commodity.lower(), {}).get(market.lower())
    if not base:
        return {"status": "NOT_FOUND", "message": f"No data for {commodity} in {market}"}

    # Build 6-month history and 3-month forecast using seasonal model
    history = []
    for i in range(6, 0, -1):
        m = ((MONTH - i - 1) % 12) + 1
        hist_price = int(base * _SEASONAL.get(m, 1.0))
        history.append({
            "month": (TODAY.replace(day=1) - datetime.timedelta(days=30*i)).strftime("%Y-%m"),
            "price_kes": hist_price
        })

    forecast = []
    for i in range(1, months_ahead + 1):
        m = ((MONTH + i - 1) % 12) + 1
        fcast_price = int(base * _SEASONAL.get(m, 1.0))
        forecast.append({
            "month": (TODAY.replace(day=1) + datetime.timedelta(days=30*i)).strftime("%Y-%m"),
            "price_kes": fcast_price,
            "confidence": "LOW — demo seasonal model only"
        })

    current_price = _price(commodity.lower(), market.lower())
    next_month_price = forecast[0]["price_kes"] if forecast else current_price
    trend = "RISING" if next_month_price > current_price * 1.03 else \
            "FALLING" if next_month_price < current_price * 0.97 else "STABLE"

    unit = _BASE_PRICES.get(commodity.lower(), {}).get("unit", "unit")

    return {
        "status": "OK",
        "commodity": commodity,
        "market": market,
        "current_price_kes": current_price,
        "unit": unit,
        "price_trend": trend,
        "6_month_history": history,
        f"{months_ahead}_month_forecast": forecast,
        "trend_driver": {
            "RISING": "Post-harvest supplies decreasing. Lean season approaching. Prices typically rise.",
            "FALLING": "Harvest season approaching. Increased supply expected. Prices typically fall.",
            "STABLE": "Mid-season. No major supply/demand shift expected in near term.",
        }.get(trend, ""),
        "warning": "DEMO — Seasonal model only. Real prices affected by weather, exports, government policy, currency. Verify at eagc.org.",
        "source": "soko-mcp DEMO seasonal model. Reference: EAGC East Africa Regional Market Monitor.",
    }


@mcp.tool(
    description=(
        "Give a sell/hold recommendation for a commodity based on price trends. "
        "Western parallel: CME basis trading decision tools, grain elevator advisory. "
        "This is the 'what should I do with my harvest today?' AI advisor. "
        "DEMO model — always verify prices before acting."
    ),
    annotations={"readOnlyHint": True},
)
def sell_hold_decision(
    commodity: Annotated[str, "Your commodity"],
    market: Annotated[str, "Your nearest market"],
    quantity_bags: Annotated[int, "Quantity you want to sell (bags or units)"],
    storage_cost_per_month_kes: Annotated[int, "Your storage cost per month in KES (0 if storing is free)"] = 0,
    months_can_store: Annotated[int, "Maximum months you can store the commodity"] = 3,
) -> dict:
    current = _price(commodity.lower(), market.lower())
    if not current:
        return {"status": "NOT_FOUND", "message": f"No data for {commodity} in {market}"}

    unit = _BASE_PRICES.get(commodity.lower(), {}).get("unit", "unit")
    total_current_value = current * quantity_bags
    storage_total = storage_cost_per_month_kes * months_can_store

    # Project future prices
    future_prices = []
    for i in range(1, months_can_store + 1):
        m = ((MONTH + i - 1) % 12) + 1
        base = _BASE_PRICES[commodity.lower()][market.lower()]
        fp = int(base * _SEASONAL.get(m, 1.0))
        net_gain = (fp - current) * quantity_bags - (storage_cost_per_month_kes * i)
        future_prices.append({
            "months_from_now": i,
            "forecast_price_kes": fp,
            "projected_value_kes": fp * quantity_bags,
            "storage_cost_kes": storage_cost_per_month_kes * i,
            "net_gain_vs_selling_now_kes": net_gain,
        })

    best_option = max(future_prices, key=lambda x: x["net_gain_vs_selling_now_kes"])
    sell_now_better = best_option["net_gain_vs_selling_now_kes"] <= 0

    recommendation = "SELL NOW" if sell_now_better else f"HOLD {best_option['months_from_now']} MONTHS"
    rationale = (
        f"Selling now yields KES {total_current_value:,}. "
        + (f"Expected price rise in {best_option['months_from_now']} months would add KES {best_option['net_gain_vs_selling_now_kes']:,} after storage costs."
           if not sell_now_better else
           "Storage costs exceed the expected price increase. Sell now.")
    )

    return {
        "status": "OK",
        "commodity": commodity,
        "market": market,
        "quantity": f"{quantity_bags} {unit}s",
        "current_value_kes": total_current_value,
        "recommendation": recommendation,
        "rationale": rationale,
        "scenarios": future_prices,
        "caveat": "DEMO model — based on seasonal averages only. Real decisions require checking actual market prices, storage quality, buyer contracts, and weather forecasts.",
        "verify_prices_at": ["eagc.org", "kalro.org", f"County Market Coordinator — {market} area"],
        "source": "soko-mcp DEMO seasonal model.",
    }


@mcp.tool(
    description=(
        "Query commodity prices for multiple markets and commodities in one call. "
        "Useful for traders comparing portfolios across regions. "
        "DEMO data."
    ),
    annotations={"readOnlyHint": True},
)
def market_overview(
    commodities: Annotated[str, "Comma-separated list of commodities (e.g., 'maize,beans,potatoes')"],
    market: Annotated[str, "Primary market to query"] = "nairobi",
) -> dict:
    commodity_list = [c.strip().lower() for c in commodities.split(",")]
    results = {}
    for c in commodity_list:
        p = _price(c, market.lower())
        if p:
            unit = _BASE_PRICES.get(c, {}).get("unit", "?")
            results[c] = {"price_kes": p, "unit": unit}

    season_note = {
        True: "HARVEST SEASON — supplies high, prices typically below annual average",
        False: "LEAN SEASON — supplies lower, prices typically above annual average",
    }[MONTH in (6, 7, 12, 1)]

    return {
        "status": "OK",
        "market": market,
        "date": TODAY.isoformat(),
        "season_context": season_note,
        "prices": results,
        "commodities_not_found": [c for c in commodity_list if c not in results],
        "note": "DEMO — Synthetic prices. Verify at eagc.org or county market boards.",
        "source": "soko-mcp DEMO dataset.",
    }


def main():
    mcp.run()

if __name__ == "__main__":
    main()
