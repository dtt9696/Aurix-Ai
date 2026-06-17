#!/bin/bash
uv run python3 -m streamlit run demo_app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false
