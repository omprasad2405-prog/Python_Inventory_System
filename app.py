import csv
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

# --- Page Configuration ---
st.set_page_config(
    page_title="Cloud Inventory Dashboard",
    page_icon="📦",
    layout="wide"
)

# 1. Load secrets from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 2. Security & Connection Check
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Missing Supabase credentials! Please check your .env file.")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    """Initialize and cache Supabase client connection"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"❌ Failed to connect to Supabase: {e}")
    st.stop()

# Function to fetch latest inventory data
def fetch_inventory():
    response = supabase.table("inventory").select("*").execute()
    return response.data

# --- Title & Header ---
st.title("📦 Cloud Inventory Management System")
st.caption("Powered by Streamlit & Supabase PostgreSQL Cloud DB")

# --- Sidebar Navigation ---
st.sidebar.header("🕹️ Navigation Menu")
menu_choice = st.sidebar.radio(
    "Select Action:",
    [
        "📋 View All Products",
        "➕ Add New Product",
        "🛒 Process Checkout",
        "⚠️ Low Stock Alerts",
        "🗑️ Delete Product",
        "📥 Export CSV Report"
    ]
)

# ==========================================
# 1. VIEW ALL PRODUCTS
# ==========================================
if menu_choice == "📋 View All Products":
    st.subheader("📋 Current Inventory Stock")
    
    try:
        items = fetch_inventory()

        if items:
            df = pd.DataFrame(items)
            # Reorder columns nicely
            cols = ['id', 'name', 'price', 'quantity', 'category']
            cols = [c for c in cols if c in df.columns]
            df = df[cols]
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Products", len(df))
            col2.metric("Total Stock Items", int(df['quantity'].sum()))
            col3.metric("Total Inventory Value", f"₹{sum(df['price'] * df['quantity']):,.2f}")

            st.divider()
            # Interactive Streamlit Dataframe table (Fixed deprecation warning)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ Cloud database is currently empty.")
    except Exception as e:
        st.error(f"❌ Error fetching inventory: {e}")

# ==========================================
# 2. ADD NEW PRODUCT
# ==========================================
elif menu_choice == "➕ Add New Product":
    st.subheader("➕ Add Product to Cloud Database")

    with st.form("add_product_form", clear_on_submit=True):
        prod_id = st.text_input("Product ID (e.g., P103)").strip()
        name = st.text_input("Product Name").strip()
        category = st.text_input("Category (e.g., Electronics)").strip()
        price = st.number_input("Price (₹)", min_value=0.0, step=10.0, format="%.2f")
        quantity = st.number_input("Quantity in Stock", min_value=1, step=1)

        submitted = st.form_submit_button("➕ Save Product to Cloud")

        if submitted:
            if not prod_id or not name or not category:
                st.warning("⚠️ Please fill in all fields before submitting.")
            else:
                new_item = {
                    "id": prod_id,
                    "name": name,
                    "price": price,
                    "quantity": int(quantity),
                    "category": category
                }
                try:
                    supabase.table("inventory").insert(new_item).execute()
                    st.success(f"✅ Product **'{name}'** added to Supabase Cloud!")
                    st.rerun()  # Forces page to refresh and fetch fresh data!
                except Exception as e:
                    st.error(f"❌ Error adding item: {e}")

# ==========================================
# 3. PROCESS CHECKOUT
# ==========================================
elif menu_choice == "🛒 Process Checkout":
    st.subheader("🛒 Real-Time Checkout & Stock Sync")

    try:
        items = fetch_inventory()

        if not items:
            st.info("ℹ️ No items available for purchase.")
        else:
            product_options = {f"{item['name']} (Stock: {item['quantity']})": item for item in items}
            selected_label = st.selectbox("Select Product to Buy:", list(product_options.keys()))
            selected_product = product_options[selected_label]

            buy_qty = st.number_input(
                f"Quantity to buy (Max: {selected_product['quantity']}):",
                min_value=1,
                max_value=max(1, int(selected_product['quantity'])),
                step=1
            )

            if st.button("💳 Complete Purchase"):
                if buy_qty > selected_product['quantity']:
                    st.error("❌ Not enough stock available!")
                else:
                    new_qty = selected_product['quantity'] - buy_qty
                    supabase.table("inventory").update({"quantity": new_qty}).eq("id", selected_product['id']).execute()
                    
                    total_cost = buy_qty * selected_product['price']
                    st.balloons()  # Fun animation on successful purchase!
                    st.success(f"🎉 Purchased {buy_qty}x **{selected_product['name']}**!")
                    st.metric("Total Amount Paid", f"₹{total_cost:,.2f}")
                    st.info(f"Updated stock for {selected_product['name']}: {new_qty} units remaining.")
                    st.rerun()

    except Exception as e:
        st.error(f"❌ Transaction failed: {e}")

# ==========================================
# 4. LOW STOCK ALERTS
# ==========================================
elif menu_choice == "⚠️ Low Stock Alerts":
    st.subheader("⚠️ Low-Stock Items Warning (< 5 Units)")

    try:
        response = supabase.table("inventory").select("*").lt("quantity", 5).execute()
        items = response.data

        if items:
            st.warning("⚠️ The following items are running low and need restocking!")
            df = pd.DataFrame(items)
            st.dataframe(df, use_container_width=True)
        else:
            st.success("✅ Stock levels are healthy! All products have 5 or more units.")
    except Exception as e:
        st.error(f"❌ Error checking low stock: {e}")

# ==========================================
# 5. DELETE PRODUCT
# ==========================================
elif menu_choice == "🗑️ Delete Product":
    st.subheader("🗑️ Delete Product from Cloud Database")

    try:
        items = fetch_inventory()

        if not items:
            st.info("ℹ️ Database is empty.")
        else:
            product_options = {f"{item['id']} - {item['name']}": item for item in items}
            selected_label = st.selectbox("Select Product to Delete:", list(product_options.keys()))
            selected_product = product_options[selected_label]

            st.warning(f"⚠️ Are you sure you want to permanently delete **{selected_product['name']}**?")
            if st.button("🔥 Yes, Delete Permanently"):
                supabase.table("inventory").delete().eq("id", selected_product['id']).execute()
                st.success(f"✅ Product **{selected_product['name']}** deleted from Supabase!")
                st.rerun()
    except Exception as e:
        st.error(f"❌ Error deleting item: {e}")

# ==========================================
# 6. EXPORT CSV REPORT
# ==========================================
elif menu_choice == "📥 Export CSV Report":
    st.subheader("📥 Export Inventory Report")

    try:
        items = fetch_inventory()

        if items:
            df = pd.DataFrame(items)
            csv_data = df.to_csv(index=False).encode('utf-8')

            st.download_button(
                label="📄 Download inventory_report.csv",
                data=csv_data,
                file_name="inventory_report.csv",
                mime="text/csv"
            )
            st.info("👉 Click above to download the CSV spreadsheet report directly to your browser download folder!")
        else:
            st.info("ℹ️ No data available to export.")
    except Exception as e:
        st.error(f"❌ Error exporting CSV: {e}")