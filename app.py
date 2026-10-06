"""
Automated Copywriting & Tone Transformer - Professional UI (Streamlit)
----------------------------------------------------------------------
Ye ek professional web-based UI hai jo:
  1. Ek single product ke liye marketing copy generate karti hai
  2. Ek CSV file se MULTIPLE products ek sath (batch) process karti hai

Kaise chalayein:
    1. pip install streamlit pandas google-genai
    2. Is file wali folder mein ".env" file banao aur likho:
       GEMINI_API_KEY=your_key_here
    3. Terminal mein: streamlit run app.py
    4. Browser mein khud khul jayega (usually http://localhost:8501)
"""

import os
import time
import io
import pandas as pd
import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors


# ----------------------------------------------------------------------
# SETUP: .env file se API key load karna (extra library ki zaroorat nahi)
# ----------------------------------------------------------------------
def load_env_file(filepath=".env"):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


load_env_file()

PLATFORM_RULES = {
    "LinkedIn": "Professional tone. Max 3000 characters. End with 1-2 relevant hashtags.",
    "Instagram": "Catchy and visual. Max 2200 characters. Use 3-5 hashtags and some emojis.",
    "Facebook": "Friendly and conversational. Max 500 characters. Encourage likes/comments/shares.",
    "WhatsApp": "Short and personal, like a message to a friend. Max 300 characters. No hashtags.",
    "Email": "Formal structure with Subject line, Greeting, Body, and a clear Call-to-Action. Max 500 words.",
}

MODEL_NAME = "gemini-3.8-flash"


# ----------------------------------------------------------------------
# CORE LOGIC (same engine as the CLI version)
# ----------------------------------------------------------------------
def build_prompt(product_name, platform, tone, description):
    rules = PLATFORM_RULES.get(platform, "Write general marketing copy.")
    prompt = f"""
You are a professional marketing copywriter.

Product Name: {product_name}
Product Description: {description}
Target Platform: {platform}
Tone: {tone}

Platform Rules: {rules}

Write marketing copy for this product following the platform rules and tone above.
"""
    return prompt.strip()


def generate_copy(client, prompt, temperature, top_p, max_attempts=4):
    wait_seconds = 5
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=top_p,
                ),
            )
            return response.text
        except errors.ServerError:
            if attempt == max_attempts:
                return "[ERROR: Model server busy hai, baad mein try karein]"
            time.sleep(wait_seconds)
            wait_seconds *= 2
        except Exception as e:
            return f"[ERROR: {e}]"


# ----------------------------------------------------------------------
# STREAMLIT UI
# ----------------------------------------------------------------------
st.set_page_config(page_title="AI Copywriting Transformer", page_icon="✍️", layout="wide")

st.title("✍️ Automated Copywriting & Tone Transformer")
st.caption("DecodeLabs | Project 2 - Generative AI Industrial Training Kit")

# --- Sidebar: settings only (API key ab sirf backend/.env se aati hai) ---
with st.sidebar:
    st.header("⚙️ Settings")
    temperature = st.slider("Temperature (creativity)", 0.0, 1.0, 0.7, 0.05)
    top_p = st.slider("Top_P", 0.0, 1.0, 1.0, 0.05)
    st.caption("Kam Temperature = seedha-sada text | Zyada Temperature = creative/witty text")

# API key backend se (.env file) load hoti hai, frontend pe kahin nahi dikhti/type nahi hoti
api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    st.error(
        "GEMINI_API_KEY nahi mili. Is app wali folder mein '.env' file banayein aur "
        "usme likhein: GEMINI_API_KEY=your_key_here"
    )
    st.stop()

client = genai.Client(api_key=api_key)

# --- Main tabs ---
tab1, tab2 = st.tabs(["📝 Single Product", "📊 Batch (CSV se Multiple Products)"])

# ========================================================================
# TAB 1: SINGLE PRODUCT
# ========================================================================
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input("Product Name", placeholder="e.g. Wireless Earbuds")
        description = st.text_area(
            "Product Description",
            placeholder="e.g. Noise cancelling, 20hr battery life, sweat-proof",
            height=100,
        )
        platform = st.selectbox("Platform", list(PLATFORM_RULES.keys()))
        tone = st.text_input("Tone", placeholder="e.g. witty, professional, casual, persuasive")

        generate_btn = st.button("🚀 Generate Copy", type="primary", use_container_width=True)

    with col2:
        st.subheader("Generated Marketing Copy")
        if generate_btn:
            if not product_name or not description or not tone:
                st.error("Product Name, Description, aur Tone sab zaroori hain.")
            else:
                with st.spinner("AI copy likh raha hai..."):
                    prompt = build_prompt(product_name, platform, tone, description)
                    result = generate_copy(client, prompt, temperature, top_p)
                st.text_area("Result", value=result, height=300)
                st.download_button(
                    "⬇️ Download as .txt",
                    data=result,
                    file_name=f"{product_name}_{platform}.txt",
                )
        else:
            st.info("Left side mein details bhar kar 'Generate Copy' dabayein.")

# ========================================================================
# TAB 2: BATCH (CSV)
# ========================================================================
with tab2:
    st.subheader("CSV se Bohat Saare Products Ek Sath Process Karein")
    st.markdown(
        """
        CSV file mein ye columns hone chahiye (exact spelling ke sath):
        `Product_Name`, `Description`, `Platform`, `Tone`

        Platform values in mein se koi ek honi chahiye: **LinkedIn, Instagram, Facebook, WhatsApp, Email**
        """
    )

    # Sample CSV template download
    sample_df = pd.DataFrame(
        {
            "Product_Name": ["Wireless Earbuds", "Smart Watch"],
            "Description": ["Noise cancelling, 20hr battery", "Fitness tracking, heart rate monitor"],
            "Platform": ["Instagram", "LinkedIn"],
            "Tone": ["witty", "professional"],
        }
    )
    st.download_button(
        "⬇️ Sample CSV Template Download Karein",
        data=sample_df.to_csv(index=False),
        file_name="sample_products.csv",
        mime="text/csv",
    )

    uploaded_file = st.file_uploader("Apni CSV file upload karein", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        required_cols = {"Product_Name", "Description", "Platform", "Tone"}

        if not required_cols.issubset(df.columns):
            st.error(f"CSV mein ye columns missing hain: {required_cols - set(df.columns)}")
        else:
            st.success(f"{len(df)} products load ho gaye. Preview neeche hai:")
            st.dataframe(df, use_container_width=True)

            if st.button("🚀 Sab Products Process Karein", type="primary"):
                results = []
                progress_bar = st.progress(0, text="Shuru ho raha hai...")

                for i, row in df.iterrows():
                    progress_bar.progress(
                        (i + 1) / len(df),
                        text=f"Processing {i + 1}/{len(df)}: {row['Product_Name']}",
                    )
                    prompt = build_prompt(row["Product_Name"], row["Platform"], row["Tone"], row["Description"])
                    copy_text = generate_copy(client, prompt, temperature, top_p)
                    results.append(
                        {
                            "Product_Name": row["Product_Name"],
                            "Platform": row["Platform"],
                            "Tone": row["Tone"],
                            "Generated_Copy": copy_text,
                        }
                    )

                progress_bar.progress(1.0, text="Mukammal ho gaya! ✅")

                results_df = pd.DataFrame(results)
                st.subheader("Results")
                st.dataframe(results_df, use_container_width=True)

                st.download_button(
                    "⬇️ Results CSV Download Karein",
                    data=results_df.to_csv(index=False),
                    file_name="generated_copy_results.csv",
                    mime="text/csv",
                )