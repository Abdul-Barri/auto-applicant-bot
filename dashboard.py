import streamlit as st
import json
import os
import subprocess
from shutil import copyfileobj

PROFILE_PATH = "user_profile.json"

def load_profile():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    return {}

def save_profile(data):
    with open(PROFILE_PATH, "w") as f:
        json.dump(data, f, indent=2)

st.title("🤖 Auto-Applicant Bot Dashboard")

# 1. Profile Editor
st.header("📝 User Profile")
profile = load_profile()

with st.expander("Personal Info", expanded=True):
    col1, col2 = st.columns(2)
    p = profile.get("personal_info", {})
    p["first_name"] = col1.text_input("First Name", p.get("first_name", ""))
    p["last_name"] = col2.text_input("Last Name", p.get("last_name", ""))
    p["email"] = col1.text_input("Email", p.get("email", ""))
    p["phone"] = col2.text_input("Phone", p.get("phone", ""))
    p["linkedin"] = st.text_input("LinkedIn", p.get("linkedin", ""))
    profile["personal_info"] = p

with st.expander("Statements (AI Context)"):
    s = profile.get("statements", {})
    s["research_interests"] = st.text_area("Research Interests", s.get("research_interests", ""))
    s["bio"] = st.text_area("Short Bio", s.get("bio", ""))
    profile["statements"] = s

with st.expander("Credentials (Sensitive)"):
    c = profile.get("credentials", {})
    c["username"] = st.text_input("Portal Username", c.get("username", ""))
    c["password"] = st.text_input("Portal Password", c.get("password", ""), type="password")
    profile["credentials"] = c

if st.button("💾 Save Profile"):
    save_profile(profile)
    st.success("Profile saved!")

# 2. Document Upload
st.header("📄 Documents")
uploaded_cv = st.file_uploader("Upload CV (PDF)", type="pdf")
if uploaded_cv:
    with open("cv.pdf", "wb") as f:
        copyfileobj(uploaded_cv, f)
    st.success("CV updated successfully!")

# 3. Run Bot
st.header("🚀 Run Application")
target_url = st.text_input("Target Application URL", "https://ultimateqa.com/filling-out-forms/")

if st.button("Start Bot"):
    with st.spinner("Running bot... Check terminal for logs."):
        # We run the script as a subprocess
        env = os.environ.copy()
        # Pass keys if needed
        
        process = subprocess.Popen(
            ["python", "apply.py", target_url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        st.text("Output Log:")
        st.code(stdout)
        
        if process.returncode == 0:
            st.success("Bot finished successfully!")
            if os.path.exists("final_state.png"):
                st.image("final_state.png", caption="Final Screenshot")
        else:
            st.error(f"Bot failed with code {process.returncode}")
            st.code(stderr)
