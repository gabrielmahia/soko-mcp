"""Live tools: parsing, provenance, validation and failure behaviour, with the network mocked (CI never depends on the services)."""
import urllib.error

from soko_mcp import main as server


def _boom(url, params=None, timeout=20.0):
    raise urllib.error.URLError("down")

def test_food_market_prices_keeps_the_latest_per_market(monkeypatch):
    rows = [{"market_name": "Lodwar", "admin1_name": "Turkana", "commodity_name": "Maize (white)", "unit": "KG", "price_type": "Retail", "price": 60.0, "currency_code": "KES", "reference_period_start": "2026-08-15T00:00:00"},
            {"market_name": "Lodwar", "admin1_name": "Turkana", "commodity_name": "Maize (white)", "unit": "KG", "price_type": "Retail", "price": 64.0, "currency_code": "KES", "reference_period_start": "2026-09-15T00:00:00"},
            {"market_name": "Kakuma", "admin1_name": "Turkana", "commodity_name": "Maize (white)", "unit": "KG", "price_type": "Retail", "price": 70.0, "currency_code": "KES", "reference_period_start": "2026-07-15T00:00:00"}]
    seen = {}
    monkeypatch.setattr(server, "_live_get", lambda url, params=None, timeout=20.0: seen.update(params) or {"data": rows})
    r = server.food_market_prices("maize", "Turkana", 6)
    assert [(p["market"], p["price"], p["date"]) for p in r["prices"]] == [("Lodwar", 64.0, "2026-09-15"), ("Kakuma", 70.0, "2026-07-15")]
    assert seen["location_code"] == "KEN" and seen["admin1_name"] == "Turkana" and seen["app_identifier"] and "CC BY-IGO" in r["attribution"]


def test_food_market_prices_failure_and_bad_input_never_give_prices(monkeypatch):
    monkeypatch.setattr(server, "_live_get", _boom)
    assert "error" in server.food_market_prices("maize") and "prices" not in server.food_market_prices("maize")
    assert "error" in server.food_market_prices("") and "error" in server.food_market_prices("maize", months=0)
