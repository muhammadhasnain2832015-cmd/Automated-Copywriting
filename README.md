# Automated Copywriting & Tone Transformer

**DecodeLabs | Generative AI Industrial Training Kit - Project 2**

An AI-powered application that takes a raw product description and automatically generates professional marketing copy tailored to different platforms — LinkedIn, Instagram, Facebook, WhatsApp, and Email — with adjustable tone and creativity settings.

## Features

- **Single Product Mode** — generate copy for one product via a clean web UI
- **Batch Mode** — upload a CSV of multiple products and generate copy for all of them at once
- Platform-specific rules (character limits, style, hashtags) baked into the prompt
- Adjustable `temperature` and `top_p` to control the AI's creativity
- Automatic retry with exponential backoff when the model is busy
- API key handled entirely on the backend — never exposed in the UI

## Tech Stack

- Python
- [Streamlit](https://streamlit.io/) — web UI
- [Google Gemini API](https://ai.google.dev/) — text generation
- Pandas — CSV handling

## Project Structure

```
.
├── app.py                  # Streamlit web UI (single + batch generation)
├── copywriter_gemini.py    # CLI version (single product)
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

## Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # Mac/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

5. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_key_here
   ```

## Usage

**Web UI:**
```bash
streamlit run app.py
```

**Command line (single product):**
```bash
python copywriter_gemini.py --product "Wireless Earbuds" --description "Noise cancelling, 20hr battery" --platform instagram --tone witty
```

**Batch (CSV):** Use the "Batch" tab in the web UI — a sample CSV template is available for download inside the app. Required columns: `Product_Name`, `Description`, `Platform`, `Tone`.

## Author

Built as part of the DecodeLabs Generative AI Industrial Training Kit, 2026 batch.
