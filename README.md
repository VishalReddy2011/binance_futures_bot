# Binance Futures Testnet Trading Bot

A structured Python application that operates on the Binance Futures Testnet (USDT-M) environment. 

This project implements:
1. Core API Client & Validation Layers (using the official python-binance library).
2. Standard Option-driven CLI (using click).
3. Interactive Guided Wizard (using questionary) when run without CLI arguments.
4. Interactive Dashboard UI (using streamlit).
5. Additional Order Types: MARKET, LIMIT, STOP_MARKET, and STOP_LIMIT.
6. Automated Unit Tests (using pytest and pytest-mock).

---

## Project Structure

```text
binance_futures_bot/
│
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance Futures Testnet client setup
│   ├── orders.py          # API parameter mapping and order execution wrapper
│   ├── validators.py      # Strict validation for symbol, side, qty, price, and stop price
│   └── logging_config.py  # Structured file & console rotating logs configurations
│
├── tests/
│   ├── test_validators.py # Validation rule tests
│   └── test_client.py     # Mocked client initialization and order mapping tests
│
├── cli.py                 # Command line interface & guided wizard entry point
├── app.py                 # Streamlit web application
├── requirements.txt       # Dependencies manifest
└── .env.example           # API credential configuration template
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- A Binance Futures Testnet account. Register at testnet.binancefuture.com.

### 1. Configure Credentials
Duplicate `.env.example` as `.env` and enter your Testnet API Key and API Secret:
```bash
cp .env.example .env
```
Open `.env` and fill in:
```ini
BINANCE_API_KEY=your_actual_testnet_api_key
BINANCE_API_SECRET=your_actual_testnet_api_secret
```
*Note: Credentials can also be configured or updated via the Streamlit sidebar.*

### 2. Create Virtual Environment and Install Dependencies
Ensure you are in the project folder and run:
```bash
python -m venv venv
```

Activate the virtual environment:
- On Windows (Command Prompt):
  ```cmd
  venv\Scripts\activate.bat
  ```
- On Windows (PowerShell):
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

Install requirements:
```bash
pip install -r requirements.txt
```

---

## How to Run

### 1. Running the Interactive Wizard
Run the CLI without arguments to launch a guided step-by-step terminal wizard:
```bash
python cli.py
```

### 2. Running via Standard CLI Arguments
Submit orders directly from the command line:
- MARKET Order:
  ```bash
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  ```
- LIMIT Order:
  ```bash
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 61250.0
  ```
- STOP_MARKET Order:
  ```bash
  python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 59500.0
  ```
- STOP_LIMIT Order:
  ```bash
  python cli.py --symbol BTCUSDT --side SELL --type STOP_LIMIT --quantity 0.001 --price 59200.0 --stop-price 59500.0
  ```

### 3. Launching the Streamlit Web UI
Run the interactive Streamlit dashboard:
```bash
streamlit run app.py
```
This launches a browser window (usually at http://localhost:8501).

---

## Running Automated Tests

Run the test suite using pytest:
```bash
pytest tests/
```

---

## Logging Behavior
- Logs are written to both standard output (console) and a rotating file at `logs/trading_bot.log` (rotating at 5MB, keeping 3 history archives).
- Log records include the outbound order details and the full JSON payload returned from the Binance API.
- Any API exception, validation issue, or network connection failure is fully logged.

---

## Assumptions & Specifications
1. Symbol Formatting: Input symbol is automatically capitalized and sanitized.
2. Order Execution Limits: The user is responsible for ensuring the quantity, price, and stopPrice adhere to the Binance Testnet symbol filters (tick size, step size, minimum notional values).
3. STOP_LIMIT mapping: A STOP_LIMIT order is mapped to Binance's API order type `STOP` which requires both `price`, `stopPrice`, and a `timeInForce` policy (e.g. `GTC`).
4. STOP_MARKET mapping: Mapped to `STOP_MARKET` which requires `stopPrice` but no `price`.
