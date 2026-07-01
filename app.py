import streamlit as st
import os
import time
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.logging_config import setup_logging, logger
from bot.validators import validate_order_inputs, ValidationError
from bot.client import BinanceFuturesClient
from bot.orders import execute_order, format_order_summary

load_dotenv()
setup_logging()

st.set_page_config(
    page_title="Binance Futures Client",
    layout="wide"
)

st.markdown("""
<div style="background-color:#1e293b;padding:20px;border-radius:10px;margin-bottom:25px;">
    <h1 style="color:#f8fafc;margin:0;">Binance Futures Testnet Terminal</h1>
    <p style="color:#94a3b8;margin:5px 0 0 0;">Place and monitor USD-M Futures orders on testnet.</p>
</div>
""", unsafe_allow_html=True)

if "order_history" not in st.session_state:
    st.session_state.order_history = []

st.sidebar.markdown("### API Credentials")
api_key = st.sidebar.text_input("API Key", value=os.getenv("BINANCE_API_KEY", ""), type="password")
api_secret = st.sidebar.text_input("API Secret", value=os.getenv("BINANCE_API_SECRET", ""), type="password")

if st.sidebar.button("Save to .env", use_container_width=True):
    if api_key.strip() and api_secret.strip():
        with open(".env", "w") as env_file:
            env_file.write(f"BINANCE_API_KEY={api_key.strip()}\n")
            env_file.write(f"BINANCE_API_SECRET={api_secret.strip()}\n")
        os.environ["BINANCE_API_KEY"] = api_key.strip()
        os.environ["BINANCE_API_SECRET"] = api_secret.strip()
        st.sidebar.success("Credentials saved.")
        time.sleep(0.5)
        st.rerun()
    else:
        st.sidebar.error("Credentials cannot be empty.")

connected = False
binance_client = None
try:
    if os.getenv("BINANCE_API_KEY") and os.getenv("BINANCE_API_SECRET"):
        client_wrapper = BinanceFuturesClient()
        binance_client = client_wrapper.get_client()
        connected = True
        st.sidebar.markdown("""
        <div style="background-color:#065f46;padding:10px;border-radius:5px;text-align:center;font-weight:bold;color:#10b981;">
            CONNECTED TO TESTNET
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="background-color:#7f1d1d;padding:10px;border-radius:5px;text-align:center;font-weight:bold;color:#f87171;">
            NOT CONFIGURED
        </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.sidebar.markdown("""
    <div style="background-color:#7f1d1d;padding:10px;border-radius:5px;text-align:center;font-weight:bold;color:#f87171;">
        CONNECTION ERROR
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.error(str(e))

tab_order, tab_logs, tab_history = st.tabs(["Order Entry", "Logs", "History"])

with tab_order:
    st.subheader("Place Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input("Symbol", value="BTCUSDT").upper().strip()
        side = st.selectbox("Side", ["BUY", "SELL"])
        order_type = st.selectbox("Type", ["MARKET", "LIMIT", "STOP_MARKET", "STOP_LIMIT"])
        
    with col2:
        quantity = st.text_input("Quantity", value="0.001")
        
        price = None
        if order_type in ["LIMIT", "STOP_LIMIT"]:
            price = st.text_input("Limit Price (USDT)", value="")
            
        stop_price = None
        if order_type in ["STOP_MARKET", "STOP_LIMIT"]:
            stop_price = st.text_input("Stop Price (USDT)", value="")

    st.markdown("---")
    if st.button("Submit Order", type="primary", use_container_width=True):
        if not connected or not binance_client:
            st.error("Client not connected. Please verify credentials.")
        else:
            try:
                validated = validate_order_inputs(
                    symbol=symbol,
                    side=side,
                    order_type=order_type,
                    quantity=quantity,
                    price=price,
                    stop_price=stop_price
                )
                
                st.info("Submitting order...")
                response = execute_order(binance_client, validated)
                
                summary = format_order_summary(response, validated["type"])
                st.success("Order Placed")
                st.code(summary, language="text")
                
                st.session_state.order_history.append({
                    "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Symbol": symbol,
                    "Side": side,
                    "Type": order_type,
                    "Quantity": quantity,
                    "Price": price if price else "MARKET",
                    "Stop Price": stop_price if stop_price else "N/A",
                    "OrderId": response.get("orderId", "N/A"),
                    "Status": response.get("status", "N/A")
                })
                
                with st.expander("Raw API Response"):
                    st.json(response)
                    
            except ValidationError as ve:
                st.error(f"Validation Error: {ve}")
            except Exception as e:
                st.error(f"Error: {e}")

with tab_logs:
    st.subheader("Logs")
    
    if st.button("Refresh Logs"):
        st.rerun()

    log_path = "logs/trading_bot.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        recent_log_text = "".join(lines[-80:])
        st.code(recent_log_text, language="text")
    else:
        st.warning("Log file not found.")

with tab_history:
    st.subheader("Session History")
    
    if st.session_state.order_history:
        import pandas as pd
        df = pd.DataFrame(st.session_state.order_history)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No orders placed this session.")
