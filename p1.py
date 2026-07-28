# --- INITIAL DATA (Stored in Memory) ---
inventory = {
    "101": {"name": "Wireless Mouse", "price": 499.0, "quantity": 12, "category": "Electronics"},
    "102": {"name": "USB-C Cable", "price": 299.0, "quantity": 3, "category": "Electronics"},
    "103": {"name": "Notebook", "price": 80.0, "quantity": 25, "category": "Stationery"}
}


def display_inventory():
    """Component 1: View All Stock"""
    print("\n" + "=" * 55)
    print(f"{'ID':<6} | {'Product Name':<20} | {'Price (₹)':<10} | {'Stock':<6}")
    print("=" * 55)
    for prod_id, info in inventory.items():
        print(f"{prod_id:<6} | {info['name']:<20} | ₹{info['price']:<9.2f} | {info['quantity']:<6}")
    print("=" * 55)


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
            print(f"⚠️  ALERT: {info['name']} (ID: {prod_id}) - Only {info['quantity']} left!")
            found = True
    if not found:
        print("✅ All items have sufficient stock.")


def generate_bill():
    """Component 4: Customer Checkout Simulator"""
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

    print("\n" + "-" * 30)
    print("      RECEIPT SUMMARY      ")
    print("-" * 30)
    print(f"Item: {inventory[prod_id]['name']}")
    print(f"Quantity: {buy_qty}")
    print(f"Price per unit: ₹{inventory[prod_id]['price']}")
    print(f"Total Amount: ₹{total_cost:.2f}")
    print("-" * 30)
    print("✅ Purchase complete! Inventory updated.")


# --- MAIN PROGRAM LOOP ---
def main():
    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM ===")
        print("1. View All Products")
        print("2. Add New Product")
        print("3. Check Low Stock Warnings")
        print("4. Process Customer Sale / Bill")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            display_inventory()
        elif choice == "2":
            add_product()
        elif choice == "3":
            check_low_stock()
        elif choice == "4":
            generate_bill()
        elif choice == "5":
            print("\nExiting program... Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()