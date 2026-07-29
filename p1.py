# --- INITIAL DATA (Stored in Memory) ---
inventory = {
    "101": {"name": "Wireless Mouse", "price": 499.0, "quantity": 12, "category": "Electronics"},
    "102": {"name": "USB-C Cable", "price": 299.0, "quantity": 3, "category": "Electronics"},
    "103": {"name": "Notebook", "price": 80.0, "quantity": 25, "category": "Stationery"},
    "104": {"name": "Gaming Headphones", "price": 1499.0, "quantity": 5, "category": "Electronics"}
}

# NEW: Transaction History Storage
sales_history = []


def display_table(items_dict):
    """Helper function to print formatted tables"""
    print("\n" + "=" * 55)
    print(f"{'ID':<6} | {'Product Name':<20} | {'Price (₹)':<10} | {'Stock':<6}")
    print("=" * 55)
    for prod_id, info in items_dict.items():
        print(f"{prod_id:<6} | {info['name']:<20} | ₹{info['price']:<9.2f} | {info['quantity']:<6}")
    print("=" * 55)


def display_inventory():
    """Component 1: View All Stock"""
    display_table(inventory)


def add_product():
    """Component 2: Add New Item"""
    print("\n--- Add New Product ---")
    prod_id = input("Enter Product ID: ").strip()

    if prod_id in inventory:
        print("❌ Error: Product ID already exists!")
        return

    name = input("Enter Product Name: ").strip()
    try:
        price = float(input("Enter Price: "))
        quantity = int(input("Enter Quantity: "))
        category = input("Enter Category: ").strip()
    except ValueError:
        print("❌ Invalid input! Price must be a number and Quantity must be an integer.")
        return

    inventory[prod_id] = {
        "name": name,
        "price": price,
        "quantity": quantity,
        "category": category
    }
    print(f"✅ Success: '{name}' added to inventory!")


def check_low_stock(threshold=5):
    """Component 3: Low-Stock Warnings"""
    print(f"\n--- Low Stock Alert (Quantity < {threshold}) ---")
    found = False
    for prod_id, info in inventory.items():
        if info['quantity'] < threshold:
            print(f"⚠️ ALERT: {info['name']} (ID: {prod_id}) - Only {info['quantity']} left!")
            found = True
    if not found:
        print("✅ All items have sufficient stock.")


def generate_bill():
    """Component 4: Customer Checkout & Sale Logging"""
    print("\n--- Customer Checkout ---")
    prod_id = input("Enter Product ID to buy: ").strip()

    if prod_id not in inventory:
        print("❌ Product not found!")
        return

    try:
        buy_qty = int(input("Enter Quantity to buy: "))
    except ValueError:
        print("❌ Quantity must be a valid integer.")
        return

    current_stock = inventory[prod_id]['quantity']
    if buy_qty > current_stock:
        print(f"❌ Not enough stock! Only {current_stock} available.")
        return

    # Process Purchase
    inventory[prod_id]['quantity'] -= buy_qty
    total_cost = buy_qty * inventory[prod_id]['price']
    item_name = inventory[prod_id]['name']

    # NEW: Log transaction details
    sales_history.append({
        "item": item_name,
        "quantity": buy_qty,
        "total": total_cost
    })

    print("\n" + "-" * 30)
    print("      RECEIPT SUMMARY      ")
    print("-" * 30)
    print(f"Item: {item_name}")
    print(f"Quantity: {buy_qty}")
    print(f"Price per unit: ₹{inventory[prod_id]['price']}")
    print(f"Total Amount: ₹{total_cost:.2f}")
    print("-" * 30)
    print("✅ Purchase complete! Sale recorded.")


def search_products():
    """Search by Name or Category"""
    print("\n--- Search Inventory ---")
    term = input("Enter product name or category to search: ").strip().lower()

    results = {}
    for prod_id, info in inventory.items():
        if term in info['name'].lower() or term in info['category'].lower():
            results[prod_id] = info

    if results:
        print(f"\n🔍 Found {len(results)} matching item(s):")
        display_table(results)
    else:
        print("❌ No matching products found.")


def sort_inventory():
    """Sort items by Price or Quantity"""
    print("\n--- Sort Options ---")
    print("1. Sort by Price (Low to High)")
    print("2. Sort by Quantity (Low to High)")
    choice = input("Select sort option (1-2): ").strip()

    if choice == "1":
        sorted_tuples = sorted(inventory.items(), key=lambda item: item[1]['price'])
        print("\n📈 Inventory Sorted by Price (Low to High):")
        display_table(dict(sorted_tuples))
    elif choice == "2":
        sorted_tuples = sorted(inventory.items(), key=lambda item: item[1]['quantity'])
        print("\n📉 Inventory Sorted by Quantity (Low to High):")
        display_table(dict(sorted_tuples))
    else:
        print("❌ Invalid sort option.")


# ==================== NEW PHASE 1.2 FEATURE ====================

def view_sales_analytics():
    """NEW FEATURE: Sales History & Revenue Dashboard"""
    print("\n--- Sales Analytics Dashboard ---")

    if not sales_history:
        print("ℹ️ No transactions recorded yet.")
        return

    total_revenue = sum(sale['total'] for sale in sales_history)
    total_units_sold = sum(sale['quantity'] for sale in sales_history)

    print("\n" + "=" * 45)
    print(f"{'Item Sold':<20} | {'Qty':<5} | {'Total (₹)':<10}")
    print("=" * 45)
    for sale in sales_history:
        print(f"{sale['item']:<20} | {sale['quantity']:<5} | ₹{sale['total']:<10.2f}")
    print("=" * 45)

    print(f"📊 Total Transactions: {len(sales_history)}")
    print(f"📦 Total Units Sold:  {total_units_sold}")
    print(f"💰 Total Revenue:     ₹{total_revenue:.2f}")


# ===============================================================

# --- MAIN PROGRAM LOOP ---
def main():
    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM (v1.2) ===")
        print("1. View All Products")
        print("2. Add New Product")
        print("3. Check Low Stock Warnings")
        print("4. Process Customer Sale / Bill")
        print("5. Search Products")
        print("6. Sort Inventory")
        print("7. View Sales Analytics (New!)")
        print("8. Exit")

        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            display_inventory()
        elif choice == "2":
            add_product()
        elif choice == "3":
            check_low_stock()
        elif choice == "4":
            generate_bill()
        elif choice == "5":
            search_products()
        elif choice == "6":
            sort_inventory()
        elif choice == "7":
            view_sales_analytics()
        elif choice == "8":
            print("\nExiting program... Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please enter a number between 1 and 8.")


if __name__ == "__main__":
    main()
