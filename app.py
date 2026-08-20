import os
import io
import json
import pandas as pd
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
from PIL import Image
from google import genai

load_dotenv()

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(
    page_title="AI Inventory System",
    page_icon="📦",
    layout="wide"
)

# --- CONNECT TO SUPABASE ---
url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# --- SESSION STATE INITIALIZATION ---
if "user" not in st.session_state:
    st.session_state.user = None

if "guest_inventory" not in st.session_state:
    st.session_state.guest_inventory = pd.DataFrame(
        columns=["id", "name", "price", "quantity", "category"]
    )

# AI Auto-fill State Defaults
if "ai_name" not in st.session_state:
    st.session_state.ai_name = ""
if "ai_category" not in st.session_state:
    st.session_state.ai_category = ""
if "ai_price" not in st.session_state:
    st.session_state.ai_price = 0.0

# --- GEMINI AI HELPER FUNCTIONS ---

def analyze_product_image(uploaded_file):
    """Analyzes an uploaded image using Google Gemini API to pre-fill item details."""
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Missing GEMINI_API_KEY in environment/secrets!")
        return None

    try:
        client = genai.Client(api_key=api_key)
        img = Image.open(uploaded_file)
        
        prompt = """
        Analyze this product image. Return ONLY a valid JSON object matching this structure:
        {
            "name": "Concise product name",
            "category": "Suggested category (e.g. Beverages, Electronics, Snacks, Office Supplies, Household)",
            "estimated_price": 0.00
        }
        Do not include markdown or extra commentary. Output raw JSON only.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[img, prompt]
        )

        clean_json = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"AI Extraction failed: {e}")
        return None


def ask_inventory_ai(user_query, df):
    """Answers natural language questions about the current inventory using Gemini."""
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Missing GEMINI_API_KEY in environment/secrets!"

    try:
        client = genai.Client(api_key=api_key)
        
        inventory_context = df.to_json(orient="records") if not df.empty else "[]"
        
        prompt = f"""
        You are an intelligent inventory management assistant.
        Below is the current inventory dataset in JSON format:
        {inventory_context}
        
        User Question: "{user_query}"
        
        Instructions:
        1. Base your answer STRICTLY on the provided inventory data.
        2. If the data is empty, mention that the inventory is currently empty.
        3. Be concise, professional, and directly answer the question using clear formatting (bullet points, bold text, etc.).
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error contacting AI: {e}"


# --- HELPER: FETCH DATA ---
def get_cloud_inventory():
    try:
        res = supabase.table("inventory").select("*").eq("user_id", st.session_state.user.id).execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            cols = [c for c in ["id", "name", "category", "price", "quantity"] if c in df.columns]
            return df[cols]
        return pd.DataFrame(columns=["id", "name", "price", "quantity", "category"])
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame(columns=["id", "name", "price", "quantity", "category"])


is_logged_in = st.session_state.user is not None

if is_logged_in:
    inventory_df = get_cloud_inventory()
else:
    inventory_df = st.session_state.guest_inventory


# --- SIDEBAR: AUTHENTICATION & AI ASSISTANT ---
st.sidebar.title("🔐 Account & Tools")

if st.session_state.user is None:
    st.sidebar.info("💡 **Guest Mode Active**\nChanges persist in RAM during session.")
    
    tab_login, tab_signup = st.sidebar.tabs(["Log In", "Sign Up"])
    
    with tab_login:
        login_email = st.text_input("Email", key="log_email")
        login_pass = st.text_input("Password", type="password", key="log_pass")
        if st.sidebar.button("Log In"):
            try:
                res = supabase.auth.sign_in_with_password({"email": login_email, "password": login_pass})
                st.session_state.user = res.user
                st.sidebar.success("Logged in successfully!")
                st.rerun()
            except Exception as e:
                st.sidebar.error("Invalid email or password.")

    with tab_signup:
        signup_email = st.text_input("Email", key="sign_email")
        signup_pass = st.text_input("Password", type="password", key="sign_pass")
        if st.sidebar.button("Create Account"):
            try:
                res = supabase.auth.sign_up({"email": signup_email, "password": signup_pass})
                st.sidebar.success("Account created! Select 'Log In' tab to sign in.")
            except Exception as e:
                st.sidebar.error(f"Error creating account: {e}")

else:
    st.sidebar.success(f"Logged in as:\n**{st.session_state.user.email}**")
    if st.sidebar.button("Log Out"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

st.sidebar.markdown("---")

# --- SIDEBAR ACCESSIBLE AI CHATBOT ---
with st.sidebar.expander("🤖 **AI Inventory Assistant**", expanded=True):
    st.caption("Ask questions about stock, valuation, or low inventory.")
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! Ask me anything about your stock."}
        ]

    chat_container = st.container(height=250)
    with chat_container:
        for msg in st.session_state.chat_messages:
            st.chat_message(msg["role"]).write(msg["content"])

    if user_prompt := st.chat_input("Ask AI..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        
        reply = ask_inventory_ai(user_prompt, inventory_df)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()


# --- MAIN DASHBOARD HEADER & KPI BANNER ---
st.title("📦 Smart Inventory Manager")

if is_logged_in:
    st.caption("☁️ Connected to **Supabase Cloud Database**")
else:
    st.caption("🧪 Operating in **Temporary Guest Session**")

# Migration Option for Guests Logging In
if is_logged_in and not st.session_state.guest_inventory.empty:
    if st.button("📥 Import Guest Items to Cloud Account"):
        for _, row in st.session_state.guest_inventory.iterrows():
            try:
                supabase.table("inventory").insert({
                    "id": str(row["id"]),
                    "name": row["name"],
                    "price": float(row["price"]),
                    "quantity": int(row["quantity"]),
                    "category": row["category"],
                    "user_id": st.session_state.user.id
                }).execute()
            except Exception as e:
                st.error(f"Failed to migrate '{row['name']}': {e}")
        st.session_state.guest_inventory = pd.DataFrame(columns=["id", "name", "price", "quantity", "category"])
        st.success("Guest items migrated into Cloud!")
        st.rerun()

# --- PROFESSIONAL KPI METRICS BANNER ---
total_items = len(inventory_df) if not inventory_df.empty else 0
total_qty = int(inventory_df["quantity"].sum()) if not inventory_df.empty else 0
total_val = float((inventory_df["price"].astype(float) * inventory_df["quantity"].astype(int)).sum()) if not inventory_df.empty else 0.0
low_stock_count = len(inventory_df[inventory_df["quantity"].astype(int) <= 5]) if not inventory_df.empty else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Unique Products", f"{total_items}")
m2.metric("Total Stock Count", f"{total_qty} units")
m3.metric("Total Inventory Value", f"${total_val:,.2f}")
m4.metric("Low Stock Items (≤5)", f"{low_stock_count}", delta_color="inverse")

st.markdown("---")

# --- CONSOLIDATED TOP NAVIGATION TABS ---
tab_view, tab_add, tab_manage, tab_alerts, tab_export = st.tabs([
    "📋 Inventory Stock", 
    "➕ Add Product", 
    "⚙️ Operations (Sale/Update/Delete)", 
    "⚠️ Low Stock Monitor", 
    "📥 Reports & Export"
])

# ==========================================
# TAB 1: VIEW INVENTORY
# ==========================================
with tab_view:
    st.subheader("Current Inventory Stock")
    if not inventory_df.empty:
        col_search, col_filter = st.columns([3, 1])
        search_query = col_search.text_input("🔍 Search products by name or category")
        
        filtered_df = inventory_df
        if search_query:
            filtered_df = inventory_df[
                inventory_df["name"].astype(str).str.contains(search_query, case=False, na=False) |
                inventory_df["category"].astype(str).str.contains(search_query, case=False, na=False)
            ]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("Inventory is currently empty.")

# ==========================================
# TAB 2: ADD PRODUCT (WITH AI VISION AUTOFILL)
# ==========================================
with tab_add:
    st.subheader("Add New Product")

    with st.expander("📸 Smart Auto-fill: Upload product image for AI extraction", expanded=False):
        uploaded_image = st.file_uploader("Upload product photo", type=["jpg", "jpeg", "png", "webp"])
        if uploaded_image is not None:
            st.image(uploaded_image, caption="Uploaded Product", width=180)
            if st.button("✨ Extract Details with Gemini Vision"):
                with st.spinner("Analyzing image..."):
                    result = analyze_product_image(uploaded_image)
                    if result:
                        st.session_state.ai_name = result.get("name", "")
                        st.session_state.ai_category = result.get("category", "")
                        st.session_state.ai_price = float(result.get("estimated_price", 0.0))
                        st.success("Extracted details! Form pre-filled below.")
                        st.rerun()

    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        prod_id = col1.text_input("Product ID (e.g. 101)")
        name = col2.text_input("Product Name", value=st.session_state.ai_name)
        category = col1.text_input("Category", value=st.session_state.ai_category)
        price = col2.number_input("Price ($)", min_value=0.0, value=st.session_state.ai_price, step=0.5)
        quantity = col1.number_input("Initial Quantity", min_value=0, value=10, step=1)
        
        if st.form_submit_button("Add Item to Inventory"):
            if not name.strip() or not prod_id.strip():
                st.error("Please provide both Product ID and Product Name.")
            else:
                if is_logged_in:
                    try:
                        supabase.table("inventory").insert({
                            "id": str(prod_id),
                            "name": name,
                            "price": float(price),
                            "quantity": int(quantity),
                            "category": category,
                            "user_id": st.session_state.user.id
                        }).execute()
                        st.success(f"Saved '{name}' to Cloud Database!")
                    except Exception as e:
                        st.error(f"Database error: {e}")
                else:
                    new_row = pd.DataFrame([{
                        "id": str(prod_id),
                        "name": name,
                        "price": float(price),
                        "quantity": int(quantity),
                        "category": category
                    }])
                    st.session_state.guest_inventory = pd.concat([st.session_state.guest_inventory, new_row], ignore_index=True)
                    st.success(f"Added '{name}' to session memory!")
                
                st.session_state.ai_name = ""
                st.session_state.ai_category = ""
                st.session_state.ai_price = 0.0
                st.rerun()

# ==========================================
# TAB 3: OPERATIONS (SALE / UPDATE / DELETE)
# ==========================================
with tab_manage:
    st.subheader("Manage Inventory Operations")
    
    if not inventory_df.empty:
        op_sale, op_update, op_delete = st.tabs(["💰 Process Sale", "🔄 Restock / Adjust", "🗑️ Delete Product"])
        
        with op_sale:
            selected_item = st.selectbox("Select Product to Sell", inventory_df["name"].tolist(), key="sale_item")
            item_data = inventory_df[inventory_df["name"] == selected_item].iloc[0]
            current_qty = int(item_data["quantity"])
            
            st.write(f"**Current Stock:** {current_qty} | **Price:** ${float(item_data['price']):.2f}")
            sale_qty = st.number_input("Quantity Sold", min_value=1, max_value=max(1, current_qty), step=1)
            
            if st.button("Complete Transaction"):
                new_qty = current_qty - sale_qty
                if is_logged_in:
                    supabase.table("inventory").update({"quantity": new_qty}).eq("id", str(item_data["id"])).eq("user_id", st.session_state.user.id).execute()
                else:
                    st.session_state.guest_inventory.loc[st.session_state.guest_inventory["name"] == selected_item, "quantity"] = new_qty
                
                total_sale = sale_qty * float(item_data["price"])
                st.success(f"Sold {sale_qty} x '{selected_item}' for ${total_sale:.2f}!")
                st.rerun()

        with op_update:
            update_item = st.selectbox("Select Product", inventory_df["name"].tolist(), key="update_select")
            item_data = inventory_df[inventory_df["name"] == update_item].iloc[0]
            new_stock = st.number_input("Set New Quantity", min_value=0, value=int(item_data["quantity"]), step=1)
            
            if st.button("Update Stock Quantity"):
                if is_logged_in:
                    supabase.table("inventory").update({"quantity": int(new_stock)}).eq("id", str(item_data["id"])).eq("user_id", st.session_state.user.id).execute()
                else:
                    st.session_state.guest_inventory.loc[st.session_state.guest_inventory["name"] == update_item, "quantity"] = int(new_stock)
                st.success(f"Updated quantity of '{update_item}' to {new_stock}!")
                st.rerun()

        with op_delete:
            delete_item = st.selectbox("Select Product to Remove", inventory_df["name"].tolist(), key="delete_select")
            if st.button("Delete Product", type="primary"):
                del_data = inventory_df[inventory_df["name"] == delete_item].iloc[0]
                if is_logged_in:
                    supabase.table("inventory").delete().eq("id", str(del_data["id"])).eq("user_id", st.session_state.user.id).execute()
                else:
                    st.session_state.guest_inventory = st.session_state.guest_inventory[st.session_state.guest_inventory["name"] != delete_item]
                st.success(f"Removed '{delete_item}' from database.")
                st.rerun()
    else:
        st.info("No items in inventory to operate on.")

# ==========================================
# TAB 4: LOW STOCK MONITOR
# ==========================================
with tab_alerts:
    st.subheader("⚠️ Low Stock Monitor")
    threshold = st.number_input("Set Alert Threshold Quantity", min_value=1, value=5, step=1)
    
    if not inventory_df.empty:
        low_stock_items = inventory_df[inventory_df["quantity"].astype(int) <= threshold]
        if not low_stock_items.empty:
            st.warning(f"Found {len(low_stock_items)} product(s) at or below threshold ({threshold}):")
            st.dataframe(low_stock_items, use_container_width=True)
        else:
            st.success("All products currently have healthy stock levels!")
    else:
        st.info("Inventory is empty.")

# ==========================================
# TAB 5: REPORTS & EXPORT
# ==========================================
with tab_export:
    st.subheader("📥 Export Reports")
    if not inventory_df.empty:
        csv_buffer = io.StringIO()
        inventory_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download Inventory CSV Report",
            data=csv_buffer.getvalue(),
            file_name="inventory_report.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available to export.")