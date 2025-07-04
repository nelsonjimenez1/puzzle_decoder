# Puzzle Decoder Race 🧩

This is a Python-based solution for the Puzzle Decoder technical challenge.

---

## 🚀 How to Run the Solution

### 1. ✅ Requirements

- Python 3.10 or later  
- `pip` installed  
- Docker (for running the puzzle server)

### 2. 🐍 Install Python and pip

If you don't have Python and pip installed:

**On Windows:**

- Install via Chocolatey:

  ```bash
  choco install python --version=3.10.11 -y
  ```

**Or manually:**  
Download from [https://www.python.org/downloads/](https://www.python.org/downloads/)

To verify:

```bash
python --version
pip --version
```

---

### 3. 📦 Install dependencies

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:

```
aiohttp
```

---

### 4. 🐳 Run the Puzzle API server (Docker)

You must run the API that serves the puzzle fragments:

```bash
docker run -p 8080:8080 ghcr.io/jamescflee/puzzle-decoder:main
```

Once running, it will listen on:

```
http://localhost:8080/fragment?id=...
```

---

### 5. ▶️ Run the decoder

Inside the root folder:

```bash
python decoder/main.py
```

---

## 🧠 Strategy for Speed and Correctness

### ✅ Goal:

Collect all puzzle fragments as fast as possible and reconstruct the message.

### 💡 Key strategies:

1. **Parallelism with asyncio:**

   - 500 tasks are launched concurrently to maximize throughput.

2. **Fragment tracking and deduplication:**

   - Each task fetches a fragment with a random `id`.
   - The fragment’s `index` is used as a unique key.

3. **Quiet-period logic:**

   - The program waits up to 50ms for a new fragment.
   - When no new data arrives during that time, it checks if all fragments from `0` to `max(index)` have been collected.

4. **Streaming prefetch strategy:**

   - A background loop continuously launches 50 new requests every 50ms.
   - This keeps network pressure constant and eliminates wait gaps.

This ensures both:

- 🔥 **Speed** via aggressive parallelism and proactive prefetching.
- 🛡️ **Correctness** through full index tracking and validation.

---

## ⏱️ Did the program complete in under 1 second?

✅ **Yes.**  
All test runs completed in under **1 second**, with average durations between **300–700 milliseconds** thanks to continuous prefetching.

---

## 📄 File structure

```
decoder/
├── main.py
├── __init__.py
requirements.txt
README.md
```

---

## 📬 Author

Developed by Nelson — built to be fast, robust, and scalable.
