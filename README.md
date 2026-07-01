# 📊 soko-mcp — Kenya Commodity Price Intelligence MCP Server

[![soko-mcp Glama score](https://glama.ai/mcp/servers/gabrielmahia/soko-mcp/badges/score.svg)](https://glama.ai/mcp/servers/gabrielmahia/soko-mcp)
[![smithery badge](https://smithery.ai/badge/@gabrielmahia/soko-mcp)](https://smithery.ai/server/@gabrielmahia/soko-mcp)


---
**Compatible with `claude-sonnet-5`** (released 2026-06-30) — Anthropic's most agentic
Sonnet yet. Runs multi-step tool chains end-to-end without stopping short.
Install: `pip install soko-mcp` · Use with any MCP client.

---


A farmer deciding whether to sell or hold needs current prices across multiple markets simultaneously. That comparison exists nowhere as a single queryable source.

*Soko* = market in Swahili.

A farmer in Nakuru doesn't know that maize prices in Nairobi are 40% higher that week. Traders know. Farmers don't. This information asymmetry is one of the most costly structural disadvantages facing smallholder farmers. soko-mcp closes it.

## The Structural Problem

In mature commodity markets, price discovery is instantaneous — futures markets, satellite price tickers, and SMS alerts exist for every major exchange. A grain elevator in Iowa checks live CME prices before making any offer.

In Kenya, most smallholder farmers receive the price the trader offers, with no independent benchmark to compare against. The result: systematic underpricing at harvest, systematic overpricing at planting.

**Information asymmetry is a tax on the poor.**

## Tools

| Tool | What it does |
|------|-------------|
| `commodity_price_query` | Current price for commodity at a specific market |
| `regional_price_comparison` | Compare prices across all major Kenya markets |
| `price_trend_analysis` | 6-month history + 3-month forecast with seasonal model |
| `sell_hold_decision` | Optimal sell/hold timing given storage costs and price trend |
| `market_overview` | Multi-commodity price snapshot for a market |

## Quick Start

```bash
pip install soko-mcp       # coming soon to PyPI
soko-mcp                   # starts on stdio
```

## Example Queries for Claude

```
"What is the current Nairobi maize price?"
"Should I sell my 50 bags of beans now or wait 2 months?"
"Compare potato prices across all Kenya markets"
"Give me a price trend for avocados in Nakuru for the next 3 months"
```

## Research Basis

- EAGC East Africa Regional Market Monitor
- World Bank "Information and Communication Technology and Agricultural Markets" (2016)
- Suri & Jack "Mobile Phones and Agricultural Performance" (2016)

⚠️ DEMO data — synthetic seasonal model. Verify at eagc.org, kalro.org, or local market boards.

---
*© 2026 Gabriel Mahia / AI Kung Fu LLC · MIT License*

## Part of the East Africa Coordination Stack

This MCP server is one of 32 tools in the Kenya coordination infrastructure.
It connects to [`africa-coord-bus`](https://github.com/gabrielmahia/africa-coord-bus) — the coordination
event bus that routes signals between domains automatically.

When this server detects a threshold condition, the bus notifies:
- `bima-mcp` — parametric insurance evaluation
- `kilimo-mcp` — agricultural advisory
- `afya-mcp` — health surveillance activation
- `county-mcp` — county office alert

```python
pip install africa-coord-bus
```

All servers: [pypi.org/user/gmahia](https://pypi.org/user/gmahia/)