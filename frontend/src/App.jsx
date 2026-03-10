import { useEffect, useState } from "react";

export default function App() {
  const [search, setSearch] = useState("");
  const [submittedSearch, setSubmittedSearch] = useState("");
  const [leftWidth, setLeftWidth] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Ask a question to get started."
    }
  ]);
  const [loading, setLoading] = useState(false);

  const handbookUrl = submittedSearch
    ? `https://livehandbook.org/search/?search=${encodeURIComponent(submittedSearch)}`
    : "https://livehandbook.org/";

  useEffect(() => {
    const handleMove = (e) => {
      if (!isDragging) return;
      const next = (e.clientX / window.innerWidth) * 100;
      setLeftWidth(Math.min(75, Math.max(25, next)));
    };

    const handleUp = () => setIsDragging(false);

    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseup", handleUp);

    return () => {
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseup", handleUp);
    };
  }, [isDragging]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = search.trim();
    if (!trimmed || loading) return;

    setSubmittedSearch(trimmed);
    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setSearch("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:7860/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: trimmed })
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || "No response returned."
        }
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Error: Could not reach the chatbot backend."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ height: "100vh", width: "100vw", display: "flex", background: "#f1f1f1", color: "#1f2a44" }}>
      <section style={{ width: `${leftWidth}%`, minHeight: 0, background: "white", borderRight: "1px solid #d8deea" }}>
        <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
          <iframe
            title="Live Handbook"
            src={handbookUrl}
            style={{ height: "100%", width: "100%", border: "none", background: "white" }}
          />
        </div>
      </section>

      <div
        onMouseDown={() => setIsDragging(true)}
        style={{ width: "8px", cursor: "col-resize", background: "#d8deea" }}
        title="Drag to resize"
      />

      <section style={{ flex: 1, minHeight: 0, background: "#f1f1f1" }}>
        <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
          <div
            style={{
              background: "#2467d6",
              color: "white",
              textAlign: "center",
              height: "36px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "18px",
              fontStyle: "italic",
              fontWeight: 400,
              fontFamily: "Montserrat, Arial, sans-serif",
              letterSpacing: "0em",
              lineHeight: 1.2
            }}
          >
            <span>An initiative of <span style={{ fontStyle: "normal", fontWeight: 500 }}>AEFP</span></span>
          </div>

          <div style={{ padding: "30px 36px 18px 36px", borderBottom: "1px solid #d8deea", background: "#f1f1f1" }}>
            <img
              src="/livehandbook-logo.png"
              alt="Live Handbook Education Policy Research"
              onError={(e) => {
                e.currentTarget.style.display = "none";
                const fallback = document.getElementById("logo-fallback");
                if (fallback) fallback.style.display = "block";
              }}
              style={{ height: "74px", width: "auto", display: "block", marginBottom: "30px", background: "transparent", mixBlendMode: "multiply" }}
            />

            <div
              id="logo-fallback"
              style={{
                display: "none",
                color: "#2e67d5",
                fontSize: "28px",
                fontWeight: 600,
                marginBottom: "30px"
              }}
            >
              Live Handbook
            </div>

            <h1
              style={{
                margin: 0,
                fontSize: "48px",
                lineHeight: 1,
                fontWeight: 300,
                letterSpacing: "-0.02em",
                color: "#0F0869",
                fontFamily: "Montserrat, Arial, sans-serif"
              }}
            >
              Ask the Handbook
            </h1>
          </div>

          <div style={{ padding: "24px 36px", background: "#f1f1f1", flex: 1, overflow: "auto", display: "flex", flexDirection: "column" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10, marginBottom: 18 }}>
              <form onSubmit={handleSubmit} style={{ display: "flex", gap: "10px", width: "100%" }}>
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Ask a question"
                  style={{
                    flex: 1,
                    padding: "14px 18px",
                    borderRadius: "18px",
                    border: "1px solid #cfd8eb",
                    background: "#f1f1f1",
                    color: "#1f2a44",
                    fontSize: "15px",
                    outline: "none"
                  }}
                />
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    padding: "14px 20px",
                    borderRadius: "16px",
                    border: "none",
                    background: "#2467d6",
                    color: "white",
                    cursor: loading ? "default" : "pointer",
                    fontWeight: 600,
                    whiteSpace: "nowrap",
                    opacity: loading ? 0.7 : 1
                  }}
                >
                  {loading ? "Thinking..." : "Ask"}
                </button>
              </form>
            </div>

            <div
              style={{
                background: "#f1f1f1",
                border: "1px solid #d8deea",
                borderRadius: "20px",
                minHeight: "520px",
                overflow: "auto",
                padding: "28px",
                display: "flex",
                flexDirection: "column",
                gap: "14px",
                flex: 1
              }}
            >
              {messages.map((message, index) => (
                <div
                  key={index}
                  style={{
                    alignSelf: message.role === "user" ? "flex-end" : "flex-start",
                    background: "#f1f1f1",
                    border: "1px solid #cfd8eb",
                    borderRadius: "18px",
                    padding: "18px 20px",
                    maxWidth: "82%",
                    color: "#1f2a44",
                    lineHeight: 1.6,
                    whiteSpace: "pre-wrap"
                  }}
                >
                  {message.content}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}