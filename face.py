import streamlit as st
import base64
import requests
import json

API_URL = "https://z53hsi1xe9.execute-api.ap-south-1.amazonaws.com/verify-face"

st.set_page_config(page_title="Face Login", page_icon="🔐", layout="centered")

st.title("Career Copilot - Secure Face Login")

# initialize state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

student_id = st.text_input("Enter Student ID")
uploaded_file = st.file_uploader("Upload a selfie", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded selfie", width=200)

if st.button("Verify Face"):
    if not student_id:
        st.error("Please enter Student ID")
    elif not uploaded_file:
        st.error("Please upload an image")
    else:
        st.info("Verifying face... Please wait...")

        img_bytes = uploaded_file.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        payload = {"student_id": student_id, "image": img_b64}

        try:
            response = requests.post(API_URL, json=payload)
        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()

        if response.status_code == 200:
            data = response.json()
            if "body" in data:
                data = json.loads(data["body"])

            if data.get("match"):
                st.session_state.authenticated = True
                st.success(f"🎉 Login Successful! Similarity: {data.get('similarity', 0):.2f}%")
            else:
                st.error(f"❌ Login Failed: {data.get('message')}")
        else:
            st.error(f"API Error: {response.status_code}")

# show dashboard button only if logged in
if st.session_state.authenticated:
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dash.py")
