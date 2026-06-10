FROM python:3.11-slim
RUN pip install --no-cache-dir soko-mcp
CMD ["soko-mcp"]
