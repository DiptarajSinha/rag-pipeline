# Setting Up Supabase for RAG Persistence

This project uses **Supabase** (PostgreSQL + pgvector) to provide permanent cloud storage for your document metadata and vector embeddings. This ensures your data is preserved even when your hosting (Koyeb) restarts.

---

## 1. Create a Supabase Project
1.  Go to **[Supabase.com](https://supabase.com/)** and sign up for a free account.
2.  Click **"New Project"**.
3.  Fill in the **Project Name** (e.g., `rag-pipeline`) and **Database Password**.
    - *Save the password! You'll need it for the connection string.*
4.  Wait for the project to finish provisioning.

---

## 2. Enable pgvector Extension
The `pgvector` extension allows Postgres to handle high-dimensional AI vectors.
1.  In the Supabase Sidebar, go to **SQL Editor**.
2.  Paste the following command and click **Run**:
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```

---

## 3. Get Your Connection String (URI)
You need the **DB_URL** to connect your app to the database.
1.  In the Sidebar, go to **Project Settings** -> **Database**.
2.  Scroll down to **Connection String**.
3.  Select the **URI** tab.
4.  Copy the URL. It will look like this:
    `postgresql://postgres:[YOUR-PASSWORD]@[HOST]:5432/postgres`
5.  **Replace `[YOUR-PASSWORD]`** with the real password you set in Step 1.

---

## 4. Environment Configuration
When deploying to **Koyeb**, add this connection string as an environment variable:

- **Key**: `DB_URL`
- **Value**: `postgresql://postgres:yourpassword@db.xxxxxx.supabase.co:5432/postgres`

---

## 5. (Self-Correction) Connection Pooling
Note: Supabase provides a connection pooler if you run out of direct connections. For small projects, the direct connection (Step 3) is fine. If you see "connection limit exceeded" errors, switch to the **Pooler** connection string on port `6543`.
