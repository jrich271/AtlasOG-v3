import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

# ---------------------------
# Google Sheets setup
# ---------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

# Upload your JSON key to Streamlit and point to it here
creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
client = gspread.authorize(creds)

# Open or create sheet
try:
    sheet = client.open("AtlasOG").sheet1
except:
    sheet = client.create("AtlasOG").sheet1
    sheet.append_row(["Type", "Name", "Amount", "Date"])

# ---------------------------
# Helper functions
# ---------------------------
def log_transaction(type_, name, amount):
    sheet.append_row([type_, name, amount, datetime.now().isoformat()])

def fetch_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="AtlasOG", layout="wide")
st.title("🌍 AtlasOG Dashboard - Minimal Wealth Engine")

tab = st.sidebar.radio("Navigate", ["Investments", "Cashflow & Goals", "Compounding Tracker"])

data = fetch_data()

# ---------------------------
# Investments Tab
# ---------------------------
if tab == "Investments":
    st.header("📊 Investments Tracker")
    name = st.text_input("Investment Name")
    amount = st.number_input("Amount Invested ($)", min_value=0.0)
    if st.button("Add Investment"):
        log_transaction("Investment", name, amount)
        st.success(f"Investment {name} logged!")

    st.subheader("Your Investments")
    investments = data[data["Type"]=="Investment"] if not data.empty else pd.DataFrame()
    for _, row in investments.iterrows():
        st.write(f"{row['Name']}: ${row['Amount']} | Logged: {row['Date']}")

# ---------------------------
# Cashflow & Goals Tab
# ---------------------------
elif tab == "Cashflow & Goals":
    st.header("💰 Cashflow Tracker")
    name = st.text_input("Income/Expense Source")
    amount = st.number_input("Amount ($, positive=income, negative=expense)")
    if st.button("Add Cashflow"):
        log_transaction("Cashflow", name, amount)
        st.success("Cashflow logged!")

    st.subheader("Weekly Target Tracker")
    total_income = data[data["Type"]=="Cashflow"]["Amount"].sum() if not data.empty else 0
    weekly_goal = 1000
    progress = min(total_income / weekly_goal, 1.0)
    st.progress(progress)
    st.write(f"Current Weekly Income: ${total_income:.2f} / $1000 goal")

# ---------------------------
# Compounding Tracker
# ---------------------------
elif tab == "Compounding Tracker":
    st.header("📈 Automated Wealth Compounding")
    investments = data[data["Type"]=="Investment"] if not data.empty else pd.DataFrame()
    total = investments["Amount"].sum() if not investments.empty else 0
    projected_weekly = total * 0.05  # 5% weekly growth simulation
    st.write(f"Total Investment Capital: ${total:.2f}")
    st.write(f"Projected Micro-Scale Weekly Growth: ${projected_weekly:.2f}")
    st.write(f"Projected Weeks to $1000/week: {1000/projected_weekly:.1f} weeks" if projected_weekly>0 else "Add investments to start compounding!")

st.success("✅ AtlasOG is running autonomously with minimal tasks!")
