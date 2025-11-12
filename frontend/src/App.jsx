import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [url, setUrl] = useState("");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (results.length > 0) setResults([]);
  }, [url, query]);

  const handleSearch = async () => {
    if (!url || !query) {
      setError("Please enter both Website URL and Search Query.");
      return;
    }
    setError("");
    setLoading(true);
    setResults([]);
    try {
      const res = await axios.get("http://127.0.0.1:8000/search", {
        params: { url: encodeURI(url.trim()), query: query.trim() },
      });
      if (res.data.error) {
        setError(res.data.error);
        setResults([]);
      } else {
        setResults(res.data.results || []);
      }
    } catch (err) {
      if (err.response && err.response.data) {
        setError(JSON.stringify(err.response.data));
      } else {
        setError("Network / backend error: " + err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 flex flex-col items-center p-8">
      <h1 className="text-4xl font-bold mb-6">Website Content Search</h1>

      <div className="w-full max-w-3xl bg-white p-6 rounded-xl shadow">
        <input
          className="w-full border rounded px-4 py-3 mb-3"
          placeholder="Enter Website URL (https://example.com)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <input
          className="w-full border rounded px-4 py-3 mb-3"
          placeholder="Enter Search Query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="flex gap-3">
          <button
            onClick={handleSearch}
            disabled={loading}
            className={`px-4 py-2 rounded bg-blue-600 text-white font-medium ${
              loading ? "opacity-60 cursor-not-allowed" : "hover:bg-blue-700"
            }`}
          >
            {loading ? "🔍 Searching..." : "Search"}
          </button>
        </div>

        {error && <div className="mt-3 text-red-600 font-medium">{error}</div>}
      </div>

      {results.length > 0 && (
        <div className="w-full max-w-3xl mt-6 space-y-4">
          <h2 className="text-xl font-semibold">Search Results</h2>
          {results.map((r, i) => (
            <div
              key={i}
              className="bg-white border rounded p-4 shadow-sm"
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-semibold text-lg">{r.content.slice(0, 120)}{r.content.length > 120 ? "..." : ""}</div>
                  <div className="text-sm text-gray-500 mt-1">Path: {r.path || "/"}</div>
                </div>
                <div className="text-right">
                  <div className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm font-medium">
                    {r.score ? `${r.score}% match` : "—"}
                  </div>
                </div>
              </div>

              <div className="mt-3">
                <button
                  className="text-sm text-blue-600 hover:underline"
                  onClick={(e) => {
                    // expand scroll to code
                    const codeEl = document.getElementById(`html-${i}`);
                    if (codeEl) {
                      codeEl.scrollIntoView({ behavior: "smooth", block: "center" });
                    }
                  }}
                >
                  View HTML ⌄
                </button>

                <div id={`html-${i}`} className="mt-2 border rounded bg-gray-50 p-2 overflow-auto max-h-56">
                  <pre className="whitespace-pre-wrap text-sm text-gray-800">{r.html}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
