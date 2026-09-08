#!/usr/bin/env python3
"""Fetch and validate the symbols feed before replacing the mirror."""
import json
import os
import time
import urllib.request
from pathlib import Path

url = "https://sh1219.xyz/news-symbols.json?nonce=" + str(time.time_ns())
request = urllib.request.Request(url, headers={
    "Cache-Control": "no-cache, no-store",
    "Pragma": "no-cache",
    "User-Agent": "cpg-symbols-mirror/1.0",
})
with urllib.request.urlopen(request, timeout=45) as response:
    raw = response.read(1_000_001)
if len(raw) > 1_000_000:
    raise ValueError("Feed exceeds size limit")
data = json.loads(raw)
if not isinstance(data, dict) or data.get("ok") is not True or data.get("stale") is not False:
    raise ValueError("Feed is unsuccessful or stale")
symbols = data.get("symbols")
if not isinstance(symbols, list) or not symbols:
    raise ValueError("Expected a non-empty symbols list")
if any(not isinstance(s, str) or not s.strip() or len(s) > 64 for s in symbols):
    raise ValueError("Invalid symbol")
if data.get("count") != len(symbols):
    raise ValueError("Symbol count mismatch")
target = Path(__file__).resolve().parents[1] / "news-symbols.json"
temporary = target.with_suffix(".json.tmp")
temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
os.replace(temporary, target)
print("Validated and synchronized", len(symbols), "symbols")
