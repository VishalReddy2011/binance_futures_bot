import re

class ValidationError(Exception):
    pass

def validate_symbol(symbol: str) -> str:
    if not symbol:
        raise ValidationError("Symbol cannot be empty.")
    symbol_clean = symbol.strip().upper()
    if not re.match(r"^[A-Z0-9]{3,15}$", symbol_clean):
        raise ValidationError(f"Invalid symbol: '{symbol}'. Must be 3-15 alphanumeric characters.")
    return symbol_clean

def validate_side(side: str) -> str:
    if not side:
        raise ValidationError("Side cannot be empty.")
    side_clean = side.strip().upper()
    if side_clean not in ["BUY", "SELL"]:
        raise ValidationError(f"Invalid side: '{side}'. Must be BUY or SELL.")
    return side_clean

def validate_order_type(order_type: str) -> str:
    if not order_type:
        raise ValidationError("Order type cannot be empty.")
    type_clean = order_type.strip().upper()
    valid_types = ["MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT"]
    if type_clean not in valid_types:
        raise ValidationError(f"Invalid order type: '{order_type}'. Must be one of {', '.join(valid_types)}.")
    return type_clean

def validate_quantity(quantity) -> float:
    if quantity is None:
        raise ValidationError("Quantity cannot be empty.")
    try:
        qty_float = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if qty_float <= 0:
        raise ValidationError(f"Quantity must be greater than zero.")
    return qty_float

def validate_price(price, order_type: str) -> float:
    if order_type in ["LIMIT", "STOP_LIMIT"]:
        if price is None or str(price).strip() == "":
            raise ValidationError(f"Price is required for {order_type} orders.")
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price must be a number, got '{price}'.")
        if price_float <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price_float
    return 0.0

def validate_stop_price(stop_price, order_type: str) -> float:
    if order_type in ["STOP_MARKET", "STOP_LIMIT"]:
        if stop_price is None or str(stop_price).strip() == "":
            raise ValidationError(f"Stop price is required for {order_type} orders.")
        try:
            stop_float = float(stop_price)
        except (ValueError, TypeError):
            raise ValidationError(f"Stop price must be a number, got '{stop_price}'.")
        if stop_float <= 0:
            raise ValidationError("Stop price must be greater than zero.")
        return stop_float
    return 0.0

def validate_order_inputs(symbol: str, side: str, order_type: str, quantity, price=None, stop_price=None):
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_type = validate_order_type(order_type)
    clean_qty = validate_quantity(quantity)
    clean_price = validate_price(price, clean_type)
    clean_stop_price = validate_stop_price(stop_price, clean_type)
    
    return {
        "symbol": clean_symbol,
        "side": clean_side,
        "type": clean_type,
        "quantity": clean_qty,
        "price": clean_price,
        "stop_price": clean_stop_price
    }
