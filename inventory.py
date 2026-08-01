import os
from dotenv import load_dotenv
from supabase import create_client, Client
from tabulate import tabulate

# 1. Load secrets from .env file
load_dotenv()

# 2. Retrieve credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 3. Security Check: Ensure environment variables exist
if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials!")
    print("👉 Please ensure you have a file named EXACTLY '.env' in your main folder.")
    exit()

# 4. Initialize Supabase Client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as err:
    print(f"❌ Failed to initialize Supabase client: {err}")
    exit()


def display_table(items_list):
    """Prints formatted ASCII table from cloud data using tabulate"""
    formatted_data = []
    for item in items_list:
        formatted_data.append([
            item['id'],
            item['name'],
            f"₹{item['price']:.2f}",
            item['quantity'],
            item.get('category', 'N/A')
        ])

    headers = ["ID", "Product Name", "Price", "Stock", "Category"]
    print("\n" + tabulate(formatted_data, headers=headers, tablefmt="fancy_grid"))


def display_inventory():
    """Fetch items directly from Supabase Cloud"""
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
    """Add a new product to Supabase Cloud"""
    print("\n--- Add New Product (Cloud) ---")
    prod_id = input("Enter Product ID: ").strip()
    name = input("Enter Product Name: ").strip()

    try:
        price = float(input("Enter Price: "))
        quantity = int(input("Enter Quantity: "))
        category = input("Enter Category: ").strip()
    except ValueError:
        print("❌ Invalid price or quantity. Must be numbers.")
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
    """Update stock in real-time on Supabase Cloud"""
    print("\n--- Customer Checkout (Cloud Sync) ---")
    prod_id = input("Enter Product ID to buy: ").strip()

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

        supabase.table("inventory").update({"quantity": new_qty}).eq("id", prod_id).execute()

        total_cost = buy_qty * product['price']
        
        receipt_data = [[product['name'], buy_qty, f"₹{product['price']:.2f}", f"₹{total_cost:.2f}"]]
        receipt_headers = ["Item Name", "Qty", "Unit Price", "Total Cost"]
        
        print("\n" + "=" * 25 + " RECEIPT SUMMARY " + "=" * 25)
        print(tabulate(receipt_data, headers=receipt_headers, tablefmt="grid"))
        print("✅ Cloud database updated in real-time!")

    except Exception as e:
        print(f"❌ Transaction failed: {e}")


def delete_product():
    """Delete a product permanently from Supabase Cloud"""
    print("\n--- Delete Product (Cloud) ---")
    prod_id = input("Enter Product ID to delete: ").strip()

    try:
        response = supabase.table("inventory").select("*").eq("id", prod_id).execute()
        items = response.data

        if not items:
            print("❌ Product not found in cloud database!")
            return

        product = items[0]
        confirm = input(f"⚠️ Are you sure you want to delete '{product['name']}'? (y/n): ").strip().lower()

        if confirm == 'y':
            supabase.table("inventory").delete().eq("id", prod_id).execute()
            print(f"✅ Success: '{product['name']}' removed from cloud database!")
        else:
            print("ℹ️ Deletion canceled.")

    except Exception as e:
        print(f"❌ Error deleting item: {e}")


def check_low_stock():
    """Fetch products where stock is below threshold (quantity < 5)"""
    print("\n--- Low Stock Alerts (< 5 items) ---")
    try:
        response = supabase.table("inventory").select("*").lt("quantity", 5).execute()
        items = response.data

        if items:
            print("⚠️ Warning: The following items need restocking!")
            display_table(items)
        else:
            print("✅ All items have sufficient stock level (5 or more).")
    except Exception as e:
        print(f"❌ Error checking low stock: {e}")


def main():
    while True:
        print("\n=== CLOUD INVENTORY MANAGEMENT (Supabase v2.0) ===")
        print("1. View All Products")
        print("2. Add New Product")
        print("3. Process Sale & Update Stock")
        print("4. Delete Product")
        print("5. Check Low-Stock Alerts")
        print("6. Exit")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            display_inventory()
        elif choice == "2":
            add_product()
        elif choice == "3":
            generate_bill()
        elif choice == "4":
            delete_product()
        elif choice == "5":
            check_low_stock()
        elif choice == "6":
            print("\nExiting cloud application... Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()