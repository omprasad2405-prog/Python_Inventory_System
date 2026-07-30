from supabase import create_client, Client

# --- SUPABASE CLOUD CREDENTIALS ---
# Replace these strings with your actual credentials from Supabase Dashboard
SUPABASE_URL = "YOUR_SUPABASE_URL_HERE"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY_HERE"

# Initialize Cloud Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def display_table(items_list):
    """Helper function to print formatted tables from cloud data"""
    print("\n" + "=" * 55)
    print(f"{'ID':<6} | {'Product Name':<20} | {'Price (₹)':<10} | {'Stock':<6}")
    print("=" * 55)
    for item in items_list:
        print(f"{item['id']:<6} | {item['name']:<20} | ₹{item['price']:<9.2f} | {item['quantity']:<6}")
    print("=" * 55)


def display_inventory():
    """Fetch and view all items directly from the Cloud Database"""
    try:
        response = supabase.table("inventory").select("*").execute()
        items = response.data
        if items:
            display_table(items)
        else:
            print("ℹ️ Cloud database is currently empty.")
    except Exception as e:
        print(f"❌ Error fetching from cloud: {e}")


def add_product():
    """Add a new product directly to the Cloud Database"""
    print("\n--- Add New Product (Cloud) ---")
    prod_id = input("Enter Product ID: ").strip()
    name = input("Enter Product Name: ").strip()

    try:
        price = float(input("Enter Price: "))
        quantity = int(input("Enter Quantity: "))
        category = input("Enter Category: ").strip()
    except ValueError:
        print("❌ Invalid price or quantity.")
        return

    new_item = {
        "id": prod_id,
        "name": name,
        "price": price,
        "quantity": quantity,
        "category": category
    }

    try:
        supabase.table("inventory").insert(new_item).execute()
        print(f"✅ Success: '{name}' added directly to Supabase Cloud!")
    except Exception as e:
        print(f"❌ Error adding item to cloud: {e}")


def generate_bill():
    """Update stock in real-time on the Cloud Database"""
    print("\n--- Customer Checkout (Cloud Sync) ---")
    prod_id = input("Enter Product ID to buy: ").strip()

    # Fetch product from cloud
    try:
        response = supabase.table("inventory").select("*").eq("id", prod_id).execute()
        items = response.data

        if not items:
            print("❌ Product not found in cloud database!")
            return

        product = items[0]
        buy_qty = int(input("Enter Quantity to buy: "))

        if buy_qty > product['quantity']:
            print(f"❌ Not enough stock! Only {product['quantity']} available.")
            return

        new_qty = product['quantity'] - buy_qty

        # Update quantity on the cloud server
        supabase.table("inventory").update({"quantity": new_qty}).eq("id", prod_id).execute()

        total_cost = buy_qty * product['price']
        print("\n" + "-" * 30)
        print("      RECEIPT SUMMARY      ")
        print("-" * 30)
        print(f"Item: {product['name']}")
        print(f"Quantity: {buy_qty}")
        print(f"Total Amount: ₹{total_cost:.2f}")
        print("-" * 30)
        print("✅ Cloud database updated in real-time!")

    except Exception as e:
        print(f"❌ Transaction failed: {e}")


def main():
    while True:
        print("\n=== CLOUD INVENTORY MANAGEMENT (Supabase v2.0) ===")
        print("1. View All Products (from Cloud)")
        print("2. Add New Product (to Cloud)")
        print("3. Process Sale & Update Cloud Stock")
        print("4. Exit")

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            display_inventory()
        elif choice == "2":
            add_product()
        elif choice == "3":
            generate_bill()
        elif choice == "4":
            print("\nExiting cloud application... Goodbye!")
            break
        else:
            print("❌ Invalid choice.")


if __name__ == "__main__":
    main()
