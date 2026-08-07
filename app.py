import os
import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# --- CONNECT TO SUPABASE ---
url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# --- SESSION STATE INITIALIZATION ---
if "user" not in st.session_state:
    st.session_state.user = None

if "guest_inventory" not in st.session_state:
    st.session_state.guest_inventory = pd.DataFrame(
        columns=["product_id", "name", "price", "quantity", "category"]
    )

# --- SIDEBAR: AUTHENTICATION PORTAL ---
st.sidebar.title("🔐 User Portal")

if st.session_state.user is None:
    st.sidebar.info("💡 **You are in Guest Mode**\nTry testing features! Your changes will disappear when you close or refresh the tab.")
    
    tab1, tab2 = st.sidebar.tabs(["Log In", "Sign Up"])
    
    with tab1:
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

    with tab2:
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

# --- MAIN DASHBOARD AREA ---
st.title("📦 Python Inventory System")

# ==========================================
# MODE 1: GUEST MODE (Temporary Memory Only)
# ==========================================
if st.session_state.user is None:
    st.subheader("🧪 Guest Workspace")
    st.caption("Data added here stays in browser RAM memory and will NOT save to Supabase.")

    with st.form("guest_add_form"):
        col1, col2 = st.columns(2)
        prod_id = col1.text_input("Product ID (e.g. PRD001)")
        name = col2.text_input("Product Name")
        category = col1.text_input("Category")
        price = col2.number_input("Price ($)", min_value=0.0)
        quantity = col1.number_input("Quantity", min_value=0)
        
        if st.form_submit_button("Add Temporary Item"):
            if not name.strip():
                st.error("Please enter a Product Name.")
            else:
                new_row = pd.DataFrame([{
                    "product_id": prod_id, 
                    "name": name, 
                    "price": price, 
                    "quantity": quantity, 
                    "category": category
                }])
                st.session_state.guest_inventory = pd.concat([st.session_state.guest_inventory, new_row], ignore_index=True)
                st.success(f"Added '{name}' to temporary memory!")
                st.rerun()

    # Display Guest Data Table
    st.dataframe(st.session_state.guest_inventory, use_container_width=True)
    
    if not st.session_state.guest_inventory.empty:
        if st.button("🗑️ Clear Temporary Data"):
            st.session_state.guest_inventory = pd.DataFrame(columns=["product_id", "name", "price", "quantity", "category"])
            st.rerun()

# ==========================================
# MODE 2: LOGGED-IN MODE (Permanent Cloud Storage)
# ==========================================
else:
    st.subheader("☁️ Your Saved Cloud Inventory")

    # Migration prompt for guest items
    if not st.session_state.guest_inventory.empty:
        if st.button("📥 Save Guest Items to Your Cloud Account"):
            for _, row in st.session_state.guest_inventory.iterrows():
                try:
                    supabase.table("inventory").insert({
                        "product_id": row["product_id"],
                        "name": row["name"],
                        "price": row["price"],
                        "quantity": row["quantity"],
                        "category": row["category"],
                        "user_id": st.session_state.user.id
                    }).execute()
                except Exception as e:
                    st.error(f"Failed to migrate item '{row['name']}': {e}")
            st.session_state.guest_inventory = pd.DataFrame(columns=["product_id", "name", "price", "quantity", "category"])
            st.success("Guest items migrated into your Supabase database!")
            st.rerun()

    # Cloud Add Form
    with st.form("cloud_add_form"):
        col1, col2 = st.columns(2)
        prod_id = col1.text_input("Product ID (e.g. PRD001)")
        name = col2.text_input("Product Name")
        category = col1.text_input("Category")
        price = col2.number_input("Price ($)", min_value=0.0)
        quantity = col1.number_input("Quantity", min_value=0)
        
        if st.form_submit_button("Save Item to Cloud"):
            if not name.strip():
                st.error("Please enter a Product Name.")
            else:
                try:
                    supabase.table("inventory").insert({
                        "product_id": prod_id,
                        "name": name,
                        "price": price,
                        "quantity": quantity,
                        "category": category,
                        "user_id": st.session_state.user.id
                    }).execute()
                    st.success(f"Saved '{name}' to your account!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving to Supabase: {e}")

    # Query items for logged in user
    try:
        response = supabase.table("inventory").select("*").eq("user_id", st.session_state.user.id).execute()
        db_data = pd.DataFrame(response.data)
        
        if not db_data.empty:
            # Display relevant columns
            cols_to_show = [col for col in ["product_id", "name", "category", "price", "quantity"] if col in db_data.columns]
            st.dataframe(db_data[cols_to_show], use_container_width=True)
            
            with st.expander("🗑️ Delete Product"):
                item_to_delete = st.selectbox("Select product to delete", db_data["name"].tolist())
                if st.button("Delete Selected Item"):
                    supabase.table("inventory").delete().eq("name", item_to_delete).eq("user_id", st.session_state.user.id).execute()
                    st.success(f"Deleted '{item_to_delete}'")
                    st.rerun()
        else:
            st.info("Your cloud inventory is empty right now. Add an item above to get started!")
    except Exception as e:
        st.error(f"Error fetching data from database: {e}")