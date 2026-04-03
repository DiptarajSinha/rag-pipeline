# Deploying RAG Pipeline to Hugging Face Spaces (No Credit Card)

This guide walks you through hosting your optimized RAG Pipeline on **Hugging Face Spaces**. This is a truly free, no-credit-card-required environment perfect for AI-powered Python apps.

---

## Prerequisites
1.  A **[Hugging Face Account](https://huggingface.co/join)** (Free).
2.  Your project pushed to a **GitHub** repository (or uploaded directly to HF).
3.  Your **Google Gemini API Key**.
4.  Your **Supabase DB_URL** (from [SUPABASE_SETUP.md](SUPABASE_SETUP.md)).

---

## Step 1: Create a New Space
1.  Log in to Hugging Face and click your profile icon -> **"New Space"**.
2.  **Space Name**: `rag-pipeline-api` (or any name you like).
3.  **License**: `apache-2.0` (or your choice).
4.  **SDK**: Select **Docker**.
5.  **Docker Template**: Select **Blank**.
6.  **Visibility**: Public or Private.
7.  Click **"Create Space"**.

---

## Step 2: Add Your Code to the Space
There are two ways to get your code into Hugging Face. **I recommend Method A** if you don't use Git.

### Method A: Upload Directly (Easiest)
1.  On your new Space page, click the **"Files and versions"** tab (near the top).
2.  Click the **"Add file"** button -> **"Upload files"**.
3.  **Drag and drop** all the local files from your project folder into the browser:
    - `app/` (the whole folder)
    - `Dockerfile`
    - `requirements.txt`
    - `README.md`
4.  Scroll down and click **"Commit changes to main"**.

### Method B: Push Directly to Hugging Face (Easiest & Most Reliable)
If you can't find the "Connect to GitHub" button, don't worry—Hugging Face is actually a Git repository itself! You can push your code directly to it from your terminal.

1.  **Get your Space's Git URL**:
    - In your Space, click the **"..."** (top right) -> **"Clone repository"**.
    - Copy the `https://huggingface.co/spaces/...` URL.

2.  **Add Hugging Face as a Remote**:
    - In your local terminal, run:
    ```bash
    git remote add hf https://huggingface.co/spaces/[your-username]/[your-space-name]
    ```

3.  **Push your code**:
    ```bash
    git push -f hf main
    ```
    - *Note: If prompted for a password, use your Hugging Face **Access Token** (from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens))*.

---

### ⚠️ IMPORTANT: How to get your "Password" (Access Token)
Hugging Face does **not** allow you to use your regular login password to push code with Git. You must use an **Access Token**.

1.  Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2.  Click **"New token"**.
3.  **Token Name**: `git-upload`
4.  **Token Type**: Select **"Write"** (Required to upload code).
5.  Click **"Create token"**.
6.  **Copy the long code** (it starts with `hf_...`).

When your terminal asks for your **Password**, simply **Paste** this token and press Enter. (The characters won't show up in the terminal while pasting—that's normal).

---

### Method C: Sync GitHub to Hugging Face (Advanced)
If you want to keep using GitHub and have it update Hugging Face automatically:
1.  Create a **GitHub Action** in your repo at `.github/workflows/sync.yml`.
2.  Use the `HF_TOKEN` secret to push from GitHub to HF. 
    *(I can help you write this script if you choose this method!)*

---

## Step 3: Add Your "Secrets" (API Keys)
This is the most important step. **The app will not start without these.**

1.  In your Space, click the **Settings** tab (top right).
2.  On the left sidebar, click **"Variables and secrets"**.
3.  Look for the section called **"Secrets"** (not Variables).
4.  Click **"New secret"** and add these one by one:

| Secret Name (Key) | Secret Value |
| :--- | :--- |
| `GOOGLE_GEMINI_API_KEY` | (Your API Key from Google AI Studio) |
| `DB_URL` | (Your Connection URI from **Supabase**) |

> [!TIP]
> **What is the DB_URL?**
> It's the long text you copied from Step 3 of the [Supabase Setup Guide](SUPABASE_SETUP.md). It looks like `postgresql://postgres:password@...`

---

## Step 4: Deployment
1.  Once you push your code (Step 2) and save your secrets (Step 3), Hugging Face will automatically start building the Docker image.
2.  Go to the **"Logs"** tab to see the progress.
3.  Once finished, your API will be live!

---

## Usage
-   Your API will be available at `https://huggingface.co/spaces/[username]/[spacename]`.
-   To use the API from code, use the **Direct Link** (e.g., `https://[username]-[spacename].hf.space`).
-   Interactive docs: `https://[username]-[spacename].hf.space/docs`.

---

## Persistence
Wait, **is it persistent?**
Yes! Because we integrated **Supabase**, your document metadata and AI search vectors are stored in the cloud. Even when the Hugging Face Space restarts, your data stays safe.
