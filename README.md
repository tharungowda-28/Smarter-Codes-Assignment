# 🌐 Website Content Search Engine

An intelligent web content search tool that allows users to search through website text using **semantic similarity** powered by embeddings and **Weaviate vector database**.
The system scrapes the given website, indexes meaningful content sections as vector embeddings, and retrieves the most relevant results based on the search query.

---

## 🚀 Features

* FastAPI backend for dynamic scraping, chunking, and semantic search
* React.js frontend with clean UI and TailwindCSS styling
* Vector similarity search using **Weaviate Cloud**
* Automatic HTML extraction and deduplication of content
* Semantic ranking using **SentenceTransformers (all-MiniLM-L6-v2)**
* Collapsible “View HTML” for source snippet preview
* Real-time query with smooth loading and error handling

---

## ⚙️ Tech Stack

**Frontend:** React (Vite) + TailwindCSS + Axios
**Backend:** FastAPI (Python 3.10+)
**AI Model:** SentenceTransformers — all-MiniLM-L6-v2
**Database:** Weaviate Cloud (Vector Database)
**Others:** BeautifulSoup4, Requests, tiktoken

---

## 🧩 Folder Structure

```
Smarter Codes/
│
├── backend/
│   ├── main.py                # FastAPI server
│   ├── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # React app
│   │   ├── index.css          # Tailwind styles
│   └── package.json           # Frontend dependencies
│
├── smartenv/                  # Virtual environment (optional local use)
└── README.md
```

---

## 🧱 Prerequisites

Make sure you have the following installed:

| Tool                       | Version | Description                       |
| -------------------------- | ------- | --------------------------------- |
| **Python**                 | ≥ 3.10  | For backend server                |
| **Node.js**                | ≥ 18.x  | For frontend (Vite)               |
| **pip**                    | latest  | Python package manager            |
| **npm**                    | latest  | Node package manager              |
| **Weaviate Cloud Account** | -       | To create vector database cluster |

---

## 🔧 Backend Setup

1. **Navigate to backend folder:**

   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv smartenv
   smartenv\Scripts\activate     # on Windows
   # or
   source smartenv/bin/activate  # on Mac/Linux
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   **requirements.txt**

   ```txt
   fastapi
   uvicorn
   weaviate-client==3.26.7
   sentence-transformers
   beautifulsoup4
   requests
   tiktoken
   numpy
   ```

4. **Run the FastAPI server:**

   ```bash
   uvicorn main:app --reload
   ```

   The server runs by default at → **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 💡 Vector Database Setup (Weaviate Cloud)

1. Go to [Weaviate Cloud Console](https://console.weaviate.cloud)
2. Create a **free Sandbox cluster**
3. Copy the **REST endpoint** and **API key**
4. Replace them in `main.py`:

   ```python
   WEAVIATE_URL = "https://YOUR-CLUSTER-ID.c0.asia-southeast1.gcp.weaviate.cloud"
   WEAVIATE_APIKEY = "YOUR_API_KEY"
   ```

> ⚠️ **Important:**
>
> * Ensure your cluster is **active** (not expired).
> * The API key must match your cluster (401 Unauthorized = invalid key).

---

## 🖥️ Frontend Setup

1. **Navigate to frontend folder:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Run development server:**

   ```bash
   npm run dev
   ```

4. Open the UI at → **[http://localhost:5173](http://localhost:5173)**

---

## 🧠 How It Works

1. **User Input:**
   Enter a website URL and a query in the UI.

2. **Backend Workflow:**

   * Fetches and parses website HTML
   * Extracts content chunks (deduplicated and tokenized)
   * Generates embeddings using `SentenceTransformer`
   * Stores embeddings + metadata in Weaviate

3. **Semantic Search:**

   * Encodes the query into an embedding
   * Finds top-N most semantically similar chunks
   * Returns results with similarity score and HTML preview

4. **Frontend Display:**

   * Shows result cards with match percentage
   * “View HTML” dropdown reveals snippet source

---

## 🧭 Example Query

| Input        | Example                 |
| ------------ | ----------------------- |
| Website URL  | `https://smarter.codes` |
| Search Query | `AI`                    |

Response displays semantic matches like:

* *“Digital Robotics for your Company 2.0 – Deploy automations powered by AI, Big Data…”*
* *“AI-powered automation tools for enterprise…”*

---

## 🧹 Common Issues

| Issue              | Cause / Fix                                                  |
| ------------------ | ------------------------------------------------------------ |
| `401 unauthorized` | Wrong or expired Weaviate API key                            |
| No results         | Website text may be too short or inaccessible                |
| Repeated chunks    | Ensure you’re running the latest deduplication logic         |
| Slow first query   | SentenceTransformer loads model on first call (cached after) |

---

## 📦 Deployment Notes

* You can deploy backend on **Render**, **Railway**, or **Vercel Serverless**.
* Frontend can be deployed to **Vercel** or **Netlify**.
* Update API endpoint in `App.jsx` if deploying to the cloud.

---

## 🧑‍💻 Author

**Tharun B**

---