import streamlit as st
import os
import time as _t
import time, random
import openai  # for catching/typing API errors
from openai import OpenAI

# =====================
# Setup
# =====================
api_key = os.getenv("OPENAI_API_KEY") or st.secrets["openai_api_key"]
client = OpenAI(api_key=api_key)

# Toggle for optional debug
SHOW_DEBUG = False

# =====================
# OpenAI helper (with retries + model rotation)
# =====================
def query_openai(prompt, max_retries=4):
    """
    Calls OpenAI with retries on 429 rate limits, rotating models if needed.
    Returns a concise string. On persistent 429, returns a friendly message.
    """
    delays = [0, 2, 4, 8, 16]  # exponential backoff
    last_err = None

    for attempt, delay in enumerate(delays[:max_retries + 1]):
        try:
            if delay:
                _t.sleep(delay + random.uniform(0, 0.4))  # jitter

            # Prefer gpt-4o-mini, fallback to gpt-3.5-turbo
            candidate_models = ["gpt-4o-mini", "gpt-3.5-turbo"]
            content = None

            for m in candidate_models:
                try:
                    response = client.chat.completions.create(
                        model=m,
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are Branden, responding in the first person as yourself. "
                                    "Keep answers ≤300 words."
                                ),
                            },
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=150,
                        temperature=0.7,
                    )
                    content = response.choices[0].message.content.strip()
                    break
                except Exception:
                    continue  # try next model

            if content is None:
                raise last_err or Exception("No model succeeded.")

            # Cleanup text
            if content.startswith("As Branden,"):
                content = content[len("As Branden,"):].strip()
            elif content.startswith("As Branden"):
                content = content[len("As Branden"):].strip()

            while content and content[-1] not in ".!?":
                content = content[:-1]

            return content

        except Exception as e:
            status = getattr(e, "status_code", None)
            name = e.__class__.__name__

            if SHOW_DEBUG:
                resp = getattr(e, "response", None)
                if resp and hasattr(resp, "headers"):
                    st.info(f"OpenAI error={name}, status={status}")

            if status == 429 or "RateLimit" in name:
                last_err = e
                continue

            if SHOW_DEBUG:
                st.error(f"OpenAI error: {e}")
            raise

    return (
        "I’m getting rate-limited right now. Please try again in a moment. "
        "If this keeps happening, wait ~60 seconds between requests."
    )

# =====================
# Data: cache the big reference block
# =====================
@st.cache_data
def load_reference_text():
    return """
Branden C. Potter — AI App Reference Document
Personal Information
• Full Name: Branden Charles Potter
• Birthday: December 15, 1987
• Age: 37 years old
• Height: 5'10"
• Residence: Chatham, New Jersey
• Heritage: African American, English, Italian, Irish, German, Native American
• Religious Beliefs: Believes in God
• Personality Traits: Funny, sweet, caring, creative, hard-working, motivated, action-taker
• Political Views: Non-political

Hobbies and Interests
• Loves animals: birds, dogs, fish
• Favorite animals: sharks, penguins, tigers, dogs
• Favorite color: Blue
• Enjoys: Visiting aquariums, hiking, nature, cooking (especially spicy food)
• Favorite foods: Mexican and Italian cuisine
• Favorite dessert: Cookies
• Favorite snack: Cheese doodles
• Favorite bands: Deftones, The Beatles
• Favorite songs: Too many favorites to list one
• Favorite movies: Jaws, Goodfellas, The Master, Raging Bull, There Will Be Blood, The Godfather, Groundhog Day
• Favorite TV show: The Sopranos
• Favorite book: House of the Scorpion (Not Harry Potter)
• Favorite sports: Football, skateboarding, boxing
• Favorite teams:
  - Baseball: New York Yankees
  - Football: New York Giants
  - Hockey: New York Rangers
  - Basketball: Chicago Bulls
• Favorite boxer: Mike Tyson

Education
• New York University – Tandon School of Engineering
  Integrated Design & Media (MS) | January 2021 – May 2023
• University of Massachusetts – Amherst
  Writing for the Media (BA) | September 2017 – January 2019

Current Career (As of 2025)
• Touro University, New York City — Adjunct Professor (September 2023 – Present)
  - Teaches undergraduate and graduate courses including Web Design, Animated Typography, and Foundations of the Web.
• Frog Boyz — Special Effects Animator (November 2022 – Present)
  - Creates special effects animation and title designs for the YouTube animated series.

Past Work Experience
• UPS, Parsippany, New Jersey — Seasonal Preload Supervisor (December 2024)
  - Supervised loading operations during peak season.
• Static Media – TheDailyMeal.com — News Writer (October 2023 – February 2024)
  - Produced SEO-optimized culinary news articles.
• Static Media – Grunge.com — News and Features Writer / Talent Acquisition (June 2020 – May 2021)
  - Wrote news and feature articles; recruited new writers.
• SessionsX.com — Writer (May 2015 – September 2015)
  - Created music-related content and artist biographies.
• Paper Mill Playhouse, Millburn, New Jersey — Caller / Fundraiser / Salesman (March 2013 – July 2014)
  - Sold subscription packages and raised funds for education programs.
• UPS, Bound Brook, New Jersey — Package Handler / Seasonal Driver Helper (September 2012 – December 2012)
  - Assisted in package handling and deliveries.

Projects
• Patient Hero: The ER in VR (September 2022 – April 2023) — Creator, Developer, Designer
  - Developed a VR hospital experience to help patients understand emergency care processes.
• Frog Boyz on Troma Now! (November 2022 – January 2023) — Special Effects Animator, Concept Designer
  - Contributed special effects, titles, and concept designs for a sketch show.
• Center for Innovation, Rutgers University (May 2024) — Consultant – Web & Content Strategy
  - Provided consulting on web development and UX design for healthcare innovation.

Skills
• Development: HTML, CSS, JavaScript, Python, SEO, PHP, C#
• Design & Animation: Web Design, Graphic Design, Motion Graphics, 2D/3D Animation
• Software & Tools: Photoshop, Unity, After Effects, Illustrator, Cinema 4D, Blender
• Writing: Content Development, Copywriting, Creative Writing

Portfolio
• Writing Samples: https://brandenpotter.myportfolio.com/writing-1
• Graphic Design and Animation: https://brandenpotter.myportfolio.com/graphic-design
• Video Projects: https://brandenpotter.myportfolio.com/video
• Coding and Technology Projects: https://brandenpotter.myportfolio.com/coding
• Full Portfolio: https://brandenpotter.myportfolio.com

Special System Prompt for the AI App:
- If the user's question asks about current work, present information based only on the "Current Career" section.
- If the user's question mentions past work, previous jobs, former positions, or uses past tense phrases like "used to do," "previously worked," "old jobs," or "before," present information based only on the "Past Work Experience" section.
- For hobbies or favorite things, casually mention just a few highlights (2 to 4 favorites maximum), not a full list. Write in natural, conversational first person.
- Only mention "Personal Background" if specifically asked about personal history.
- Keep responses concise and in first person, no more than 300 words.
    """

with st.spinner("Loading..."):
    pdf_text = load_reference_text()

# =====================
# UI
# =====================
st.title("Ask Branden")

if "busy" not in st.session_state:
    st.session_state.busy = False
if "cooldown_until" not in st.session_state:
    st.session_state.cooldown_until = 0

with st.form("question_form"):
    user_question = st.text_input(
        "Ask about Branden's favorite things, experience, education, achievements, or how to navigate his portfolio."
    )
    submitted = st.form_submit_button("Get Answer")

now = _t.time()
if submitted:
    if now < st.session_state.cooldown_until:
        wait_left = int(st.session_state.cooldown_until - now)
        st.toast(f"Cooling down — try again in ~{wait_left}s.")
    elif not user_question:
        st.error("Please enter a question.")
    elif not st.session_state.busy:
        st.session_state.busy = True
        try:
            with st.spinner("Generating answer..."):
                prompt = (
                    "Answer the following question based on the given text. "
                    "Keep the response ≤300 words:\n\n"
                    f"Text: {pdf_text}\n\n"
                    f"Question: {user_question}\n\n"
                    "Answer in the first person as Branden:"
                )
                answer = query_openai(prompt)
                st.write("Branden: " + answer)

                if "rate-limited right now" in answer.lower():
                    st.toast("Model is busy — try again in ~60s.")
                    st.session_state.cooldown_until = _t.time() + 60
        finally:
            st.session_state.busy = False