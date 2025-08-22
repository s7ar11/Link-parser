# Website Link Collector

Simple Tkinter GUI tool that collects links from a webpage, filters out anchors and symbol/unsupported schemes (e.g. `#`, `javascript:`, `mailto:`), normalizes relative URLs to absolute, deduplicates results, and saves them to `links.json`.

Usage
1. Install dependencies:
   pip install -r requierments.txt

2. Run the app:
   python stage.py

How it works
- Normalizes and validates the entered URL (adds `http://` if missing).
- Uses a requests Session for connection pooling.
- Converts relative links to absolute with urljoin.
- Filters out fragments and non-http(s) schemes.
- Deduplicates links while preserving order.
- Saves results to `links.json` in the same folder as `stage.py`.

Notes
- Use the Stop button to signal cancellation (best-effort; long-running network calls may still finish).
- The GUI displays a status and shows collected links in the scrollable text area.
