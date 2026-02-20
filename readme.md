# Service Status Tracker

A lightweight, production-ready Python service that monitors multiple RSS and Atom status feeds to detect and report new service incidents efficiently.

This project demonstrates scalable feed polling using conditional HTTP requests (`ETag` and `Last-Modified` headers) to minimize bandwidth usage and avoid redundant processing.

---

## 📌 Overview

Many cloud platforms and SaaS providers publish their service updates via RSS or Atom feeds.  
This application continuously monitors such feeds and reports newly published incidents without reprocessing previously seen entries.

The system is designed to be:

- Efficient
- Scalable
- Memory-safe
- Production-oriented
- Easy to deploy

---

## 🚀 Features

- Monitor multiple RSS/Atom feeds concurrently
- Detect only new incidents
- Avoid duplicate processing
- Use conditional requests (ETag & Last-Modified)
- Async architecture using `asyncio`
- Clean logging output
- Graceful error handling
- Virtual environment automation support (Windows)

---

## 🏗 Architecture Design

The tracker follows this flow:

1. Send HTTP request to feed URL
2. Include:
   - `If-None-Match` (ETag)
   - `If-Modified-Since` (Last-Modified)
3. If server responds:
   - `304 Not Modified` → Skip processing
   - `200 OK` → Parse feed and check for new entries
4. Process and log only unseen incidents
5. Repeat at configurable interval

This ensures:
- Reduced bandwidth usage
- Lower CPU overhead
- Scalable polling for large feed lists

---

## 📂 Project Structure

```
service-status-tracker/
│
├── StatusTracker.py      # Main application logic
├── requirements.txt      # Project dependencies
├── setup.bat             # Windows environment setup script
├── run.bat               # Run application
└── README.md             # Documentation
```

---

## ⚙️ Installation

### 1️⃣ Prerequisites

- Python 3.11 or higher
- Windows (for .bat automation scripts)

Verify Python:

```bash
python --version
```

---

### 2️⃣ Setup Environment

Run:

```bash
setup.bat
```

This script will:

- Create a virtual environment (if not already present)
- Upgrade pip
- Install required dependencies from `requirements.txt`

---

### 3️⃣ Run Application

```bash
run.bat
```

---

## 📦 Dependencies

Defined in `requirements.txt`:

---

## 🔧 Configuration

Inside `StatusTracker.py`, modify:

```python
FEEDS = [
    "https://status.openai.com/feed.atom",
    "https://www.githubstatus.com/history.atom"
]

POLL_INTERVAL_SECONDS = 60
```

You can:

- Add more feeds
- Adjust polling interval
- Integrate alerting systems

---

## 🧠 How Conditional Requests Work

To reduce unnecessary data transfer, the application uses:

### ETag

The server provides a unique identifier for the current version of the feed.

On next request:

```
If-None-Match: <etag>
```

If unchanged:

```
HTTP 304 Not Modified
```

---

### Last-Modified

The server indicates the last update timestamp.

On next request:

```
If-Modified-Since: <timestamp>
```

If unchanged:

```
HTTP 304 Not Modified
```

---

## 📈 Scalability

The architecture supports:

- 100+ feeds efficiently
- Non-blocking async polling
- Minimal memory footprint
- Stateless design (can be containerized easily)

For enterprise-grade scaling:

- Add Redis or database for persistent tracking
- Implement exponential backoff
- Add structured logging
- Integrate with monitoring systems
- Deploy via Docker or Kubernetes

---

## 🛡 Production Enhancements (Optional)

To further harden the system:

- Add structured logging (JSON)
- Integrate alerting (Slack, Email, Webhook)
- Add retry logic with backoff
- Add persistent storage (SQLite/PostgreSQL)
- Convert into system service
- Add Docker support
- Add CI/CD pipeline

---

## 🧪 Example Output

```
Feed    : https://status.openai.com/feed.atom
Service : Degraded Performance
Time    : 2026-02-18 16:40:22
Details : All impacted services have now fully recovered.
-------------------------------------------------------------
```

---

## 🎯 Use Cases

- SaaS monitoring
- Infrastructure alerting
- DevOps dashboards
- Service health tracking
- Reliability engineering tools

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Developed as a scalable feed monitoring system for production-style service tracking.

---

If you found this useful, feel free to extend it into a full observability tool.