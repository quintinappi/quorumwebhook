# Quorum Webhook Configuration

This repository contains Python scripts for managing webhook subscriptions for HikCentral sites.

## Structure

- `subscribe_events/`: Scripts for subscribing URLs to events
- `check_events/`: Scripts for checking subscription status
- `tunnel_tests/`: Scripts for testing tunnel connections

## Configuration

Each site has its own configuration with:
- Base URL
- API Key
- API Secret

## Usage

### Subscribing to Events

To subscribe a URL to events for a specific site:

```python
python3 subscribe_events/subscribe_events_[site].py
```

### Checking Subscriptions

To check current subscriptions for a specific site:

```python
python3 check_events/list_subscriptions_[site].py
```

## Sites

- Work and Art
- Drivelines
- Eastside
- Highbury
- Notabene
- Sovereign
- Stanley

## Requirements

- Python 3.x
- requests library

## Installation

```bash
pip install requests
```
