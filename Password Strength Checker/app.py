import re
import streamlit as st

# Page config
st.set_page_config(
    page_title="Password Strength Checker by Qasim Hussain",
    page_icon="🔑",
    layout="centered"
)

# Glassmorphism CSS
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
            font-family: 'Segoe UI', sans-serif;
        }
        .main {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            border-radius: 15px;
            padding: 30px;
            margin-top: 20px;
            box-shadow: 0px 8px 25px rgba(0,0,0,0.5);
        }
        .stTextInput input {
            border-radius: 12px;
            border: 2px solid #4CAF50;
            font-size: 18px;
            padding: 10px;
            text-align: center;
        }
        .stButton button {
            width: 60%;
            border-radius: 12px;
            background: linear-gradient(90deg, #ff6a00, #ee0979);
            color: white;
            font-size: 18px;
            font-weight: bold;
            transition: 0.3s;
            padding: 10px;
        }
        .stButton button:hover {
            transform: scale(1.05);
            background: linear-gradient(90deg, #ee0979, #ff6a00);
        }
        .strength-bar {
            height: 28px;
            border-radius: 12px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align:center;'>🚀 Boss-Level Password Strength Checker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Enter your password and instantly see how strong it is 🔍</p>", unsafe_allow_html=True)

# Password strength function
def password_strength(password):
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("❌ At least **8 characters** required.")

    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("❌ Use **both uppercase & lowercase letters**.")

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("❌ Add some **numbers (0-9)**.")

    if re.search(r"[!@#$%^&*]", password):
        score += 1
    else:
        feedback.append("❌ Add a **special character (!@#$%^&*)**.")

    return score, feedback

# Input
password = st.text_input("Enter Password", type="password")

# Button
if st.button("🔥 Check Strength"):
    if password:
        score, feedback = password_strength(password)

        # Boss-Level Progress Bar
        colors = {0: "#ff0033", 1: "#ff6600", 2: "#ffcc00", 3: "#3399ff", 4: "#33cc33"}
        labels = {0: "💀 Very Weak", 1: "⚠ Weak", 2: "😐 Fair", 3: "🔒 Medium", 4: "🚀 Strong"}

        st.markdown(f"""
            <div style="width:100%; background:#333; border-radius:12px;">
                <div class="strength-bar" 
                     style="width:{score*25}%; background:{colors[score]}; text-align:center; color:white;">
                    {labels[score]}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Result
        if score == 4:
            st.success("✅ Your password is **boss-level strong!** 🔥")
        elif score == 3:
            st.info("⚠️ Not bad, but can be stronger 💡")
        else:
            st.error("❌ Weak — hackers are laughing 😅")

        # Feedback tips
        if feedback:
            st.subheader("🔧 Improve Your Password:")
            for item in feedback:
                st.write(item)
    else:
        st.warning("⚠️ Please enter a password first!")
