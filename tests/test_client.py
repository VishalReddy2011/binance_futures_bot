import pytest
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.client import BinanceFuturesClient
from bot.orders import execute_order
from binance.client import Client

def test_client_init_missing_env(monkeypatch):
    # Remove variables to simulate unconfigured environment
    monkeypatch.delenv("BINANCE_API_KEY", raising=False)
    monkeypatch.delenv("BINANCE_API_SECRET", raising=False)
    
    with pytest.raises(ValueError, match="Binance API Key and Secret are required"):
        BinanceFuturesClient(api_key=None, api_secret=None)

def test_client_init_success(mocker, monkeypatch):
    monkeypatch.setenv("BINANCE_API_KEY", "mock_key")
    monkeypatch.setenv("BINANCE_API_SECRET", "mock_secret")
    
    # Mock Binance client connection
    mocker.patch.object(Client, "__init__", return_value=None)
    mocker.patch.object(Client, "futures_time", return_value={"serverTime": 1720000000000})
    
    wrapper = BinanceFuturesClient()
    assert wrapper.get_client() is not None
    Client.futures_time.assert_called_once()

def test_execute_order_market(mocker):
    mock_client = mocker.MagicMock(spec=Client)
    mock_client.futures_create_order.return_value = {
        "orderId": 11111,
        "status": "FILLED",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "origQty": "0.005",
        "executedQty": "0.005",
        "avgPrice": "62000.0"
    }

    order_params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quantity": 0.005,
        "price": 0.0,
        "stop_price": 0.0
    }

    res = execute_order(mock_client, order_params)
    assert res["orderId"] == 11111
    mock_client.futures_create_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="BUY",
        type="MARKET",
        quantity=0.005
    )

def test_execute_order_limit(mocker):
    mock_client = mocker.MagicMock(spec=Client)
    mock_client.futures_create_order.return_value = {
        "orderId": 22222,
        "status": "NEW",
        "symbol": "ETHUSDT",
        "side": "SELL",
        "type": "LIMIT",
        "origQty": "0.1",
        "executedQty": "0.0",
        "price": "3450.0"
    }

    order_params = {
        "symbol": "ETHUSDT",
        "side": "SELL",
        "type": "LIMIT",
        "quantity": 0.1,
        "price": 3450.0,
        "stop_price": 0.0
    }

    res = execute_order(mock_client, order_params)
    assert res["orderId"] == 22222
    mock_client.futures_create_order.assert_called_once_with(
        symbol="ETHUSDT",
        side="SELL",
        type="LIMIT",
        quantity=0.1,
        price=3450.0,
        timeInForce="GTC"
    )

def test_execute_order_stop_limit(mocker):
    mock_client = mocker.MagicMock(spec=Client)
    mock_client.futures_create_order.return_value = {
        "orderId": 33333,
        "status": "NEW",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "STOP",
        "origQty": "0.002",
        "executedQty": "0.0",
        "price": "60100.0",
        "stopPrice": "60000.0"
    }

    order_params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "STOP_LIMIT",
        "quantity": 0.002,
        "price": 60100.0,
        "stop_price": 60000.0
    }

    res = execute_order(mock_client, order_params)
    assert res["orderId"] == 33333
    # Mapped to 'STOP' internally on Binance Futures
    mock_client.futures_create_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="BUY",
        type="STOP",
        quantity=0.002,
        price=60100.0,
        stopPrice=60000.0,
        timeInForce="GTC"
    )
