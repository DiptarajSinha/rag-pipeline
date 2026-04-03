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

### Method B: Use GitHub (Permanent Connection)
If you already have a GitHub repository, follow these steps to push your new files:

1.  **Initialize Git** (if not already done):
    ```bash
    git init
    git add .
    git commit -m "Initialize Production-Ready RAG Pipeline"
    ```
2.  **Push to GitHub**:
    - Create a **New Repository** at [github.com/new](https://github.com/new).
    - Run:
    ```bash
    git remote add origin https://github.com/[your-username]/[your-repo-name].git
    git branch -M main
    git push -u origin main
    ```

3.  **Link Hugging Face to GitHub**:
    - In your Hugging Face Space, click the **Settings** tab.
    - Scroll down to the **"Connected GitHub Repository"** section.
    - Click **"Connect a GitHub repository"**.
    - Select your new repository.
    - Hugging Face will now automatically build and deploy every time you "push" to GitHub!

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
1.  Once you save your secrets and upload your code, Hugging Face will automatically detect the `README.md` frontmatter and start building the Docker image.
2.  The logs will show the progress.
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
