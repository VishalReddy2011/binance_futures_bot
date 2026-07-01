import pytest
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
    validate_order_inputs,
    ValidationError
)

def test_validate_symbol():
    assert validate_symbol("btcusdt") == "BTCUSDT"
    assert validate_symbol("  ETHUSDT  ") == "ETHUSDT"
    
    with pytest.raises(ValidationError):
        validate_symbol("")
    with pytest.raises(ValidationError):
        # Too long or invalid characters
        validate_symbol("BTC-USDT")
    with pytest.raises(ValidationError):
        validate_symbol("AB")  # Too short

def test_validate_side():
    assert validate_side("buy") == "BUY"
    assert validate_side("SELL") == "SELL"
    
    with pytest.raises(ValidationError):
        validate_side("HOLD")
    with pytest.raises(ValidationError):
        validate_side("")

def test_validate_order_type():
    assert validate_order_type("market") == "MARKET"
    assert validate_order_type("LIMIT") == "LIMIT"
    assert validate_order_type("stop_market") == "STOP_MARKET"
    assert validate_order_type("STOP_LIMIT") == "STOP_LIMIT"
    
    with pytest.raises(ValidationError):
        validate_order_type("TRAILING_STOP")

def test_validate_quantity():
    assert validate_quantity("0.001") == 0.001
    assert validate_quantity(1.5) == 1.5
    
    with pytest.raises(ValidationError):
        validate_quantity("-0.1")
    with pytest.raises(ValidationError):
        validate_quantity("abc")
    with pytest.raises(ValidationError):
        validate_quantity(None)

def test_validate_price():
    # Price is required for LIMIT and STOP_LIMIT
    assert validate_price("123.45", "LIMIT") == 123.45
    assert validate_price(50000, "STOP_LIMIT") == 50000.0
    
    # Price is not required for MARKET and STOP_MARKET
    assert validate_price(None, "MARKET") == 0.0
    assert validate_price("", "STOP_MARKET") == 0.0

    with pytest.raises(ValidationError):
        validate_price(None, "LIMIT")
    with pytest.raises(ValidationError):
        validate_price("-5", "LIMIT")
    with pytest.raises(ValidationError):
        validate_price("abc", "STOP_LIMIT")

def test_validate_stop_price():
    # Stop price is required for STOP_MARKET and STOP_LIMIT
    assert validate_stop_price("123.45", "STOP_MARKET") == 123.45
    assert validate_stop_price(50000, "STOP_LIMIT") == 50000.0
    
    # Stop price is not required for MARKET and LIMIT
    assert validate_stop_price(None, "MARKET") == 0.0
    assert validate_stop_price("", "LIMIT") == 0.0

    with pytest.raises(ValidationError):
        validate_stop_price(None, "STOP_MARKET")
    with pytest.raises(ValidationError):
        validate_stop_price("-5", "STOP_LIMIT")
    with pytest.raises(ValidationError):
        validate_stop_price("abc", "STOP_MARKET")

def test_validate_order_inputs_success():
    res = validate_order_inputs(
        symbol="BTCUSDT",
        side="buy",
        order_type="limit",
        quantity="0.005",
        price="62000.5",
        stop_price=None
    )
    assert res["symbol"] == "BTCUSDT"
    assert res["side"] == "BUY"
    assert res["type"] == "LIMIT"
    assert res["quantity"] == 0.005
    assert res["price"] == 62000.5
    assert res["stop_price"] == 0.0
