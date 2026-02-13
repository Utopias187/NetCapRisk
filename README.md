# NetCapRisk

A small Python CLI tool that models end-to-end throughput and highlights capacity bottlenecks that become risk points under load (e.g., DoS-style traffic growth).

## Why this exists (security angle)
When traffic spikes (legit or malicious), shared links become bottlenecks. This tool helps you:
- identify bottlenecks quickly
- see how per-flow throughput collapses as N grows
- flag low headroom conditions that are “DoS-prone”

## Features
- Single path throughput + bottleneck detection
- Fair-share backbone modeling (per-flow throughput vs N)
- Efficiency-adjusted link capacities (WiFi/overhead/congestion)
- DoS sweep mode with headroom + risk flags
- Optional JSON output for automation

## Install (dev)
From the repo root:

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -U pip
python -m pip install pytest
