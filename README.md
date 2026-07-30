# 📦 Python Inventory System

A cloud-connected inventory management system built with Python and Supabase.

---

## 🚀 Features
- **Cloud Database Integration:** Real-time data storage powered by Supabase (PostgreSQL).
- **Secure Credentials:** Environment variables managed via `python-dotenv` and ignored by Git.
- **Clean Architecture:** Standardized CRUD operations for managing product inventory.

---

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **Database:** Supabase Cloud (PostgreSQL)
- **Version Control:** Git & GitHub

---

## ⚙️ Setup & Installation

1. **Clone the repository:**
   ```bash
git clone [https://github.com/omprasad2405-prog/Python_Inventory_System.git](https://github.com/omprasad2405-prog/Python_Inventory_System.git)
cd Python_Inventory_System

2.  **Install dependencies:**

    Bash
    pip install supabase python-dotenv
    
   (i) Configure Environment Variables:
       Create a .env file in the root directory based on .env.example:

   Code snippet
     SUPABASE_URL=your_supabase_project_url
     SUPABASE_KEY=your_supabase_anon_key
      
   (ii) Run the Application:

   Bash
    python inventory.py

3. ### How to Commit and Push your Updated README

   Once you paste and save the updated text in `README.md`, run these 3 commands in your VS Code terminal to sync it with GitHub:
       ```powershell
   git add README.md
   git commit -m "docs: update README with Supabase setup and project overview"
   git push origin main
