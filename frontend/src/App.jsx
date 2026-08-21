import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "https://url-shortener-api-.onrender.com";

function App() {
  const [url, setUrl] = useState("");
  const [shortUrl, setShortUrl] = useState("");
  const [urls, setUrls] = useState([]);

  const [search, setSearch] = useState("");

  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [copiedId, setCopiedId] = useState(null);

  const [darkMode, setDarkMode] = useState(false);


  // --------------------------------------------------
  // Load URL history
  // --------------------------------------------------

  const loadUrls = async (searchValue = "") => {
    try {
      setHistoryLoading(true);

      const response = await axios.get(
        `${API_URL}/urls`,
        {
          params: searchValue
            ? { search: searchValue }
            : {}
        }
      );

      setUrls(response.data);

    } catch (error) {

      console.error(error);

      setError(
        "Unable to load URL history."
      );

    } finally {

      setHistoryLoading(false);
    }
  };


  // Load history when page opens
  useEffect(() => {
    loadUrls();
  }, []);


  // --------------------------------------------------
  // Shorten URL
  // --------------------------------------------------

  const shortenUrl = async () => {

    setError("");
    setSuccess("");
    setShortUrl("");

    if (!url.trim()) {

      setError(
        "Please enter a URL."
      );

      return;
    }


    // Frontend validation
    try {

      const parsedUrl = new URL(url);

      if (
        parsedUrl.protocol !== "http:" &&
        parsedUrl.protocol !== "https:"
      ) {

        setError(
          "Please enter a valid HTTP or HTTPS URL."
        );

        return;
      }

    } catch {

      setError(
        "Please enter a valid URL, for example https://google.com"
      );

      return;
    }


    try {

      setLoading(true);

      const response = await axios.post(
        `${API_URL}/shorten`,
        {
          url: url
        }
      );

      setShortUrl(
        response.data.short_url
      );

      setSuccess(
        "URL shortened successfully!"
      );

      setUrl("");

      // Refresh history
      loadUrls();

    } catch (error) {

      console.error(error);

      if (error.response?.data?.detail) {

        setError(
          error.response.data.detail
        );

      } else {

        setError(
          "Unable to shorten URL."
        );
      }

    } finally {

      setLoading(false);
    }
  };


  // --------------------------------------------------
  // Copy URL
  // --------------------------------------------------

  const copyUrl = async (
    value,
    id = "new"
  ) => {

    try {

      await navigator.clipboard.writeText(
        value
      );

      setCopiedId(id);

      setTimeout(() => {
        setCopiedId(null);
      }, 2000);

    } catch {

      setError(
        "Unable to copy URL."
      );
    }
  };


  // --------------------------------------------------
  // Delete URL
  // --------------------------------------------------

  const deleteUrl = async (id) => {

    const confirmed = window.confirm(
      "Are you sure you want to delete this shortened URL?"
    );

    if (!confirmed) {
      return;
    }


    try {

      await axios.delete(
        `${API_URL}/urls/${id}`
      );

      setSuccess(
        "URL deleted successfully!"
      );

      loadUrls(search);

    } catch (error) {

      console.error(error);

      setError(
        "Unable to delete URL."
      );
    }
  };


  // --------------------------------------------------
  // Search
  // --------------------------------------------------

  const handleSearch = (event) => {

    const value = event.target.value;

    setSearch(value);

    loadUrls(value);
  };


  // --------------------------------------------------
  // Format Date
  // --------------------------------------------------

  const formatDate = (date) => {

    return new Date(date).toLocaleString(
      "en-IN",
      {
        dateStyle: "medium",
        timeStyle: "short"
      }
    );
  };


  return (
    <div
      className={
        darkMode
          ? "app dark"
          : "app"
      }
    >

      {/* Header */}

      <header className="header">

        <div>
          <h1>
            🔗 URL Shortener
          </h1>

          <p>
            Create short and simple links instantly.
          </p>
        </div>


        <button
          className="theme-button"
          onClick={() =>
            setDarkMode(!darkMode)
          }
        >
          {darkMode
            ? "☀️ Light"
            : "🌙 Dark"}
        </button>

      </header>


      <main className="main">


        {/* Shorten Card */}

        <section className="shorten-card">

          <h2>
            Shorten your URL
          </h2>

          <p className="description">
            Enter a long URL and create a
            short link.
          </p>


          <div className="input-container">

            <input
              type="text"
              value={url}
              placeholder="https://example.com/very-long-url"
              onChange={(event) =>
                setUrl(event.target.value)
              }
              onKeyDown={(event) => {

                if (event.key === "Enter") {
                  shortenUrl();
                }

              }}
            />


            <button
              className="shorten-button"
              onClick={shortenUrl}
              disabled={loading}
            >

              {loading
                ? "Shortening..."
                : "Shorten URL"}

            </button>

          </div>


          {/* Error */}

          {error && (

            <div className="message error">
              ⚠️ {error}
            </div>

          )}


          {/* Success */}

          {success && (

            <div className="message success">
              ✅ {success}
            </div>

          )}


          {/* Generated URL */}

          {shortUrl && (

            <div className="generated">

              <div>

                <span>
                  Your shortened URL
                </span>

                <a
                  href={shortUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {shortUrl}
                </a>

              </div>


              <button
                onClick={() =>
                  copyUrl(shortUrl)
                }
              >

                {copiedId === "new"
                  ? "✓ Copied!"
                  : "📋 Copy"}

              </button>

            </div>

          )}

        </section>


        {/* History */}

        <section className="history-card">

          <div className="history-header">

            <div>

              <h2>
                📊 URL History
              </h2>

              <p>
                Manage your shortened URLs.
              </p>

            </div>


            <input
              className="search"
              type="text"
              placeholder="🔍 Search URLs..."
              value={search}
              onChange={handleSearch}
            />

          </div>


          {historyLoading ? (

            <div className="empty">
              Loading...
            </div>

          ) : urls.length === 0 ? (

            <div className="empty">

              <div className="empty-icon">
                🔗
              </div>

              <h3>
                No URLs found
              </h3>

              <p>
                Create your first shortened URL.
              </p>

            </div>

          ) : (

            <div className="table-wrapper">

              <table>

                <thead>

                  <tr>

                    <th>
                      Original URL
                    </th>

                    <th>
                      Short URL
                    </th>

                    <th>
                      Visits
                    </th>

                    <th>
                      Created
                    </th>

                    <th>
                      Actions
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {urls.map((item) => (

                    <tr key={item.id}>

                      <td>

                        <div className="original-url">

                          {item.original_url}

                        </div>

                      </td>


                      <td>

                        <a
                          href={item.short_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="short-link"
                        >
                          {item.short_url}
                        </a>

                      </td>


                      <td>

                        <span className="visits">
                          🔢 {item.click_count}
                        </span>

                      </td>


                      <td>

                        <span className="date">
                          📅 {formatDate(
                            item.created_at
                          )}
                        </span>

                      </td>


                      <td>

                        <div className="actions">

                          <button
                            className="copy-button"
                            onClick={() =>
                              copyUrl(
                                item.short_url,
                                item.id
                              )
                            }
                          >

                            {copiedId === item.id
                              ? "✓ Copied!"
                              : "📋 Copy"}

                          </button>


                          <button
                            className="delete-button"
                            onClick={() =>
                              deleteUrl(item.id)
                            }
                          >
                            🗑️
                          </button>

                        </div>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

        </section>

      </main>


      <footer>

        <p>
          URL Shortener • FastAPI + React + PostgreSQL
        </p>

      </footer>

    </div>
  );
}

export default App;