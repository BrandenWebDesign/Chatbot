import streamlit as st
import fitz  # PyMuPDF
import os
from openai import OpenAI

# Retrieve the API key from environment variable or Streamlit secrets
api_key = os.getenv("OPENAI_API_KEY") or st.secrets["openai_api_key"]

# Instantiate the OpenAI client
client = OpenAI(api_key=api_key)

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(pdf_file) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Function to query the OpenAI API with a prompt for first person responses
def query_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

# Path to your PDF file
pdf_file_path = "Branden.pdf"

# Extract text from the PDF file at startup
with st.spinner("Extracting text from PDF..."):
    pdf_text = extract_text_from_pdf(pdf_file_path)

st.success("App loaded successfully!")

# Streamlit app
st.title("Ask Branden's AI Assistant")

# Use st.form to handle form submission
with st.form("question_form"):
    user_question = st.text_input("Ask a question about Branden's experience, education, goals, achievements, or something else.")

    # Handle form submission with Enter key
    submitted = st.form_submit_button("Get Answer")

    if submitted:
        if user_question:
            with st.spinner("Generating answer..."):
                prompt = f"Answer the following question based on the given text:\n\nText: {pdf_text}\n\nQuestion: {user_question}\n\nAnswer as Branden:"
                answer = query_openai(prompt)
                st.write("Branden:", answer)  # Display answer with "Branden:" prefix
        else:
            st.error("Please enter a question.")
