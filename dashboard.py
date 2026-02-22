import streamlit as st
import json
import os
import subprocess

st.set_page_config(page_title="Auto-Applicant Bot", page_icon="🤖")

st.title("🤖 Auto-Applicant Bot")

# 1. Profile Editor
st.header("1. Your Profile")
profile_path = "user_profile.json"

if os.path.exists(profile_path):
    with open(profile_path, "r") as f:
        profile_data = json.load(f)
else:
    profile_data = {}

with st.expander("Edit Personal Info"):
    profile_data["personal_info"]["first_name"] = st.text_input("First Name", profile_data["personal_info"].get("first_name"))
    profile_data["personal_info"]["last_name"] = st.text_input("Last Name", profile_data["personal_info"].get("last_name"))
    profile_data["personal_info"]["email"] = st.text_input("Email", profile_data["personal_info"].get("email"))

if st.button("Save Profile"):
    with open(profile_path, "w") as f:
        json.dump(profile_data, f, indent=2)
    st.success("Profile saved!")

# 2. File Uploader
st.header("2. Documents")
uploaded_cv = st.file_uploader("Upload CV (PDF)", type="pdf")
if uploaded_cv:
    with open("cv.pdf", "wb") as f:
        f.write(uploaded_cv.getbuffer())
    st.success("CV Updated: cv.pdf")

# 3. Runner
st.header("3. Run Bot")
target_url = st.text_input("Target Application URL", "https://ultimateqa.com/filling-out-forms/")

if st.button("🚀 Launch Bot"):
    st.info("Starting Docker container...")
    # This assumes docker is installed and reachable
    cmd = f"docker run --rm -v {os.getcwd()}:/app auto-applicant python apply.py '{target_url}'"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    st.text_area("Logs", stdout.decode())
    if stderr:
        st.error(stderr.decode())
    
    if os.path.exists("final_state.png"):
        st.image("final_state.png", caption="Final Screenshot")
