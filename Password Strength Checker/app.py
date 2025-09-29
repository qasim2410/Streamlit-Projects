import re
import streamlit as st

# Page styling
st.set_page_config(
    page_title="Password Strength Checker by Qasim Hussain",
    page_icon="🔑",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
        .main {text-align: center;}
        .password-box {
            width: 60%;
            margin: auto;
            padding: 20px;
            border-radius: 12px;
            background: #f9f9f9;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        }
        .stTextInput>div>div>input {
            text-align: center;
            font-size: 18px;
            border-radius: 8px;
            border: 1px solid #ccc;
            padding: 10px;
        }
        .stButton button {
            width: 100%;
            background: linear-gradient(90deg, #4CAF50, #2E8B57);
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
            transition: 0.3s;
        }
        .stButton button:hover {
            background: linear-gradient(90deg, #45a049, #1e7e34);
            transform: scale(1.02);
        }
        .strength-bar {
            height: 30px;
            border-radius: 8px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Page title and description
st.markdown("<h1 style='text-align: center; color: #2E8B57;'>🔐 Password Strength Checker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Enter your password to check its security level. 🔍</p>", unsafe_allow_html=True)

# Function to check password strength
def password_strength(password):
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("❌ Password should be at least **8 characters long**.")

    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("❌ Password should include **both uppercase (A-Z) and lowercase (a-z) letters**.")

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("❌ Password should include **numbers (0-9)**.")

    if re.search(r"[!@#$%^&*]", password):
        score += 1
    else:
        feedback.append("❌ Password should include **at least one special character (!@#$%^&*)**.")

    return score, feedback

# Password input inside a styled box
with st.container():
    st.markdown("<div class='password-box'>", unsafe_allow_html=True)

    password = st.text_input("Enter Password", type="password", help="Ensure your password is strong and secure. 🔒")

    if st.button("Check Strength"):
        if password:
            score, feedback = password_strength(password)

            # Strength bar colors and labels
            strength_colors = {0: "red", 1: "orange", 2: "gold", 3: "blue", 4: "green"}
            strength_labels = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Medium", 4: "Strong"}

            st.markdown(f"""
                <div style="width: 100%; background-color: #ddd; border-radius: 8px; margin-top: 15px;">
                    <div class="strength-bar" style="width: {score*25}%; background-color: {strength_colors[score]}; text-align: center; color: white;">
                        {strength_labels[score]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Show result message
            if score == 4:
                st.success("✅ **Strong Password** - Your password is strong and secure. 🔒")
            elif score == 3:
                st.info("⚠️ **Medium Password** - Consider improving security by adding more features. 🔓")
            else:
                st.error("❌ **Weak Password** - Please make your password more secure. 🔑")

            # Feedback section
            if feedback:
                with st.expander("🔍 Tips to Improve Your Password"):
                    for item in feedback:
                        st.write(item)
        else:
            st.warning("⚠️ Please enter a password first!")

    st.markdown("</div>", unsafe_allow_html=True)

