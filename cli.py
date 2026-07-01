import sys
import os
import re
import click
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.logging_config import setup_logging, logger
from bot.validators import validate_order_inputs, ValidationError
from bot.client import BinanceFuturesClient
from bot.orders import execute_order, format_order_summary

load_dotenv()
setup_logging()

def run_interactive():
    import questionary

    click.echo("\n" + "=" * 55)
    click.echo("    Binance Futures Testnet Bot - Interactive Wizard")
    click.echo("=" * 55 + "\n")

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        click.echo("WARNING: BINANCE_API_KEY or BINANCE_API_SECRET is missing from your .env file.")
        setup_creds = questionary.confirm("Would you like to enter your API credentials now?", default=True).ask()
        if setup_creds:
            api_key = questionary.text("Enter Binance Testnet API Key:").ask()
            api_secret = questionary.password("Enter Binance Testnet API Secret:").ask()
            if api_key and api_secret:
                with open(".env", "w") as env_file:
                    env_file.write(f"BINANCE_API_KEY={api_key.strip()}\n")
                    env_file.write(f"BINANCE_API_SECRET={api_secret.strip()}\n")
                os.environ["BINANCE_API_KEY"] = api_key.strip()
                os.environ["BINANCE_API_SECRET"] = api_secret.strip()
                click.echo("Credentials saved to .env file.\n")
            else:
                click.echo("Credentials setup aborted.")
        else:
            click.echo("Continuing without saved credentials.\n")

    symbol = questionary.text(
        "Enter Trading Pair (e.g. BTCUSDT):",
        default="BTCUSDT",
        validate=lambda text: True if len(text.strip()) > 0 else "Symbol cannot be empty."
    ).ask()
    if not symbol:
        return

    side = questionary.select(
        "Select Side:",
        choices=["BUY", "SELL"]
    ).ask()
    if not side:
        return

    order_type = questionary.select(
        "Select Order Type:",
        choices=["MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT"]
    ).ask()
    if not order_type:
        return

    quantity = questionary.text(
        "Enter Quantity (e.g. 0.001):",
        validate=lambda text: True if re.match(r"^\d*\.?\d+$", text.strip()) and float(text.strip()) > 0 else "Quantity must be a positive number."
    ).ask()
    if not quantity:
        return

    price = None
    if order_type in ["LIMIT", "STOP_LIMIT"]:
        price = questionary.text(
            "Enter Limit Price (USDT):",
            validate=lambda text: True if re.match(r"^\d*\.?\d+$", text.strip()) and float(text.strip()) > 0 else "Price must be a positive number."
        ).ask()
        if not price:
            return

    stop_price = None
    if order_type in ["STOP_MARKET", "STOP_LIMIT"]:
        stop_price = questionary.text(
            "Enter Stop/Trigger Price (USDT):",
            validate=lambda text: True if re.match(r"^\d*\.?\d+$", text.strip()) and float(text.strip()) > 0 else "Stop price must be a positive number."
        ).ask()
        if not stop_price:
            return

    click.echo("\n--- Order Preview ---")
    click.echo(f"Pair      : {symbol.upper()}")
    click.echo(f"Side      : {side}")
    click.echo(f"Type      : {order_type}")
    click.echo(f"Quantity  : {quantity}")
    if price:
        click.echo(f"Price     : {price}")
    if stop_price:
        click.echo(f"Stop Price: {stop_price}")
    click.echo("-" * 21)

    confirm = questionary.confirm("Submit this order to Binance Futures Testnet?", default=True).ask()
    if not confirm:
        click.echo("Order cancelled.")
        return

    process_and_place_order(symbol, side, order_type, quantity, price, stop_price)


def process_and_place_order(symbol, side, order_type, quantity, price, stop_price):
    click.echo("\n[1/3] Validating input parameters...")
    try:
        validated = validate_order_inputs(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
    except ValidationError as e:
        click.echo(click.style(f"Input Validation Failure: {e}", fg="red", bold=True))
        logger.error(f"Input validation error: {e}")
        return

    click.echo("[2/3] Connecting to Binance API...")
    try:
        client_wrapper = BinanceFuturesClient()
        binance_client = client_wrapper.get_client()
    except Exception as e:
        click.echo(click.style(f"API Connection Failure: {e}", fg="red", bold=True))
        logger.error(f"API connection failure: {e}")
        return

    click.echo("[3/3] Sending order payload to Binance Futures...")
    try:
        response = execute_order(binance_client, validated)
        summary = format_order_summary(response, validated["type"])
        click.echo(click.style("\nOrder Processed Successfully!", fg="green", bold=True))
        click.echo(click.style(summary, fg="green"))
    except Exception as e:
        click.echo(click.style(f"\nOrder Placement Failure: {e}", fg="red", bold=True))
        logger.error(f"Order placement failed: {e}")


@click.command()
@click.option("--symbol", help="Trading pair symbol (e.g., BTCUSDT)")
@click.option("--side", type=click.Choice(["BUY", "SELL", "buy", "sell"], case_sensitive=False), help="Order side (BUY/SELL)")
@click.option("--type", "order_type", type=click.Choice(["MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT", "market", "limit", "stop_market", "stop_limit"], case_sensitive=False), help="Order type")
@click.option("--quantity", help="Order quantity (e.g. 0.001)")
@click.option("--price", help="Limit price (required for LIMIT and STOP_LIMIT)")
@click.option("--stop-price", help="Stop trigger price (required for STOP_MARKET and STOP_LIMIT)")
def main(symbol, side, order_type, quantity, price, stop_price):
    if len(sys.argv) == 1:
        run_interactive()
    else:
        missing = []
        if not symbol:
            missing.append("--symbol")
        if not side:
            missing.append("--side")
        if not order_type:
            missing.append("--type")
        if not quantity:
            missing.append("--quantity")
        
        if missing:
            click.echo(click.style(f"Error: Missing required parameters: {', '.join(missing)}", fg="red"))
            click.echo("Usage: python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001")
            click.echo("Or run 'python cli.py' without arguments to enter the wizard.")
            sys.exit(1)

        process_and_place_order(symbol, side, order_type, quantity, price, stop_price)

if __name__ == "__main__":
    main()
