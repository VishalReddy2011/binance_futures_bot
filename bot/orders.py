from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from bot.logging_config import logger

def execute_order(client: Client, order_params: dict) -> dict:
    symbol = order_params["symbol"]
    side = order_params["side"]
    order_type = order_params["type"]
    quantity = order_params["quantity"]
    price = order_params.get("price", 0.0)
    stop_price = order_params.get("stop_price", 0.0)

    api_params = {
        "symbol": symbol,
        "side": side,
        "quantity": quantity
    }

    if order_type == "MARKET":
        api_params["type"] = "MARKET"
    elif order_type == "LIMIT":
        api_params["type"] = "LIMIT"
        api_params["price"] = price
        api_params["timeInForce"] = "GTC"
    elif order_type == "STOP_MARKET":
        api_params["type"] = "STOP_MARKET"
        api_params["stopPrice"] = stop_price
    elif order_type == "STOP_LIMIT":
        api_params["type"] = "STOP"
        api_params["price"] = price
        api_params["stopPrice"] = stop_price
        api_params["timeInForce"] = "GTC"

    logger.info(f"Placing order: {symbol} {side} {order_type} Qty={quantity} Px={price} StopPx={stop_price}")
    
    try:
        response = client.futures_create_order(**api_params)
        logger.info(f"Order response received: {response}")
        return response
    except BinanceAPIException as e:
        logger.error(f"Binance order failed: {e.message} (code: {e.code})")
        raise RuntimeError(f"Binance API Error: {e.message} (code: {e.code})") from e
    except BinanceRequestException as e:
        logger.error(f"Binance network/request error: {str(e)}")
        raise ConnectionError(f"Network error: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected execution error: {str(e)}")
        raise RuntimeError(f"Unexpected error: {str(e)}") from e

def format_order_summary(response: dict, request_type: str) -> str:
    order_id = response.get("orderId", "N/A")
    status = response.get("status", "N/A")
    executed_qty = response.get("executedQty", "N/A")
    avg_price = response.get("avgPrice", None)
    
    if not avg_price or float(avg_price) == 0.0:
        avg_price = response.get("price", "N/A")

    summary = (
        f"------------------ ORDER SUCCESS ------------------\n"
        f"Order ID       : {order_id}\n"
        f"Status         : {status}\n"
        f"Side & Type    : {response.get('side', 'N/A')} {request_type}\n"
        f"Quantity       : Requested: {response.get('origQty', 'N/A')} | Executed: {executed_qty}\n"
        f"Avg/Limit Price: {avg_price}\n"
        f"---------------------------------------------------"
    )
    return summary
