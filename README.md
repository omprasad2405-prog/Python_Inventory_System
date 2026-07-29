# 📦 Inventory Management System (CLI)

A feature-rich, command-line-based Inventory Management Application built with Python. Designed for small retail or stationery businesses to efficiently manage stock, track warnings, handle customer checkout, and perform search and sorting operations.

---

## 🌟 Key Features

* **📋 Stock Display:** Formatted ASCII tabular output to clearly view Product IDs, Names, Prices, and Quantities.
* **➕ Add Products:** Easily insert new products with built-in validation for duplicate IDs and data types.
* **⚠️ Low-Stock Alerts:** Automatically flags products falling below a specified inventory threshold (default `< 5`).
* **🧾 Customer Checkout Simulator:** Generates bill receipts, calculates total purchase costs, and dynamically decrements stock upon purchase.
* **🔍 Search Functionality:** Filter inventory items dynamically by matching Product Name or Category keywords.
* **📈 Sorting Options:** Sort inventory dynamically by Price (Low to High) or Quantity (Low to High).

---

## 🛠️ Project Structure

* **`p1.py`**: Main application code containing all data structures, functions, and the interactive terminal CLI loop.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.x installed on your computer.

### How to Run
1. Open your terminal or command prompt.
2. Navigate to the project directory:
   ```bash
   cd path/to/your/project

**Run the application:**
python p1.py

**Sample Menu Overview**
=== INVENTORY MANAGEMENT SYSTEM (v1.1) ===
1. View All Products
2. Add New Product
3. Check Low Stock Warnings
4. Process Customer Sale / Bill
5. Search Products
6. Sort Inventory
7. Exit
