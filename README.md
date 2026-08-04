# 📦 Cloud Inventory Management System

A full-stack Inventory Management System featuring a **Streamlit Web Dashboard**, a **Python CLI terminal interface**, and a **Supabase PostgreSQL Cloud Database**. 

🚀 **Live Demo:** [Open Web Application](https://pythoninventorysystem.streamlit.app/)) 

---

## 📌 Project Overview

This project provides a real-time inventory management tool built using Python and modern cloud infrastructure:

- **Real-Time Cloud Sync:** All stock additions, sales updates, and deletions reflect instantly across both the web app and terminal interface.
- **Automated Sales & Stock Management:** Automatically verifies remaining quantity during checkout and updates database records in real time.
- **Low-Stock Warnings:** Highlights items falling below minimum stock thresholds (under 5 units).
- **Data Export:** Exports cloud database records directly into `.csv` spreadsheet reports.

---

## 🏗️ Build Your Own Version (How It Works)

If you want to build a similar project for your portfolio, here is the architecture:

1. **Database Setup:**
   - Create a free account at [Supabase](https://supabase.com/).
   - Create a table named `inventory` with the columns: `id` (text/int), `name` (text), `price` (float), `quantity` (int), and `category` (text).

2. **Backend & CLI:**
   - Use `supabase-py` to connect Python script handles (`inventory.py`) for CRUD operations.
   - Use `python-dotenv` to keep your `SUPABASE_URL` and `SUPABASE_KEY` secure in a `.env` file.

3. **Web Dashboard:**
   - Build an interactive frontend UI with [Streamlit](https://streamlit.io/) (`app.py`).

4. **Free Cloud Deployment:**
   - Push your code to a GitHub repository (excluding your `.env` file).
   - Link your repository to [Streamlit Community Cloud](https://share.streamlit.io/) to get a free live web URL.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Database:** Supabase (PostgreSQL)
- **Language:** Python 3.x
- **Libraries:** `supabase`, `pandas`, `tabulate`, `python-dotenv`
