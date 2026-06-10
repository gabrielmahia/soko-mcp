# soko-mcp — Dockerfile for Glama sandbox build and evaluation
# Glama uses this to run security checks and assign quality/security scores.
#
# Local usage:
#   docker build -t soko-mcp .
#   docker run soko-mcp

FROM python:3.11-slim

LABEL org.opencontainers.image.title="soko-mcp"
LABEL org.opencontainers.image.description="MCP server for East Africa commodity price intelligence and market signals"
LABEL org.opencontainers.image.source="https://github.com/gabrielmahia/soko-mcp"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Gabriel Mahia <contact@aikungfu.dev>"

# Non-root for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir soko-mcp

USER mcpuser

# MCP servers use stdio transport
ENTRYPOINT ["soko-mcp"]
