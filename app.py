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


# Function to query the OpenAI API with a prompt for concise first person responses as Branden
def query_openai(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are Branden, responding in the first person as yourself. Please keep your answers concise and no more than 300 words."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,  # Lower token count to encourage brevity
        temperature=0.7,
    )
    content = response.choices[0].message.content.strip()

    # Ensure the response does not start with "As Branden"
    if content.startswith("As Branden,"):
        content = content[len("As Branden,"):].strip()
    elif content.startswith("As Branden"):
        content = content[len("As Branden"):].strip()

    # Ensure the response ends at a word boundary
    while len(content) > 0 and content[-1] not in ['.', '!', '?']:
        content = content[:-1]

    return content


# Path to your PDF file
pdf_file_path = "Branden.pdf"

# Extract text from the PDF file at startup
with st.spinner("Loading..."):
    pdf_text = extract_text_from_pdf(pdf_file_path)

st.success("App loaded successfully!")

# Streamlit app
st.title("Ask Branden")

# Use st.form to handle form submission
with st.form("question_form"):
    user_question = st.text_input(
        "Ask about Branden's favorite things, experience, education, achievements, or how to navigate his portfolio.")

    # Handle form submission with Enter key
    submitted = st.form_submit_button("Get Answer")

    if submitted:
        if user_question:
            with st.spinner("Generating answer..."):
                prompt = f"Answer the following question based on the given text. Please keep the response concise and no more than 300 words:\n\nText: {pdf_text}\n\nQuestion: {user_question}\n\nAnswer in the first person as Branden:"
                answer = query_openai(prompt)
                st.write("Branden: " + answer)  # Display answer with "Branden:" prefix
        else:
            st.error("Please enter a question.")
