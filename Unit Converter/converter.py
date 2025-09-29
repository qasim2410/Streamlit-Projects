import streamlit as st
st.markdown(
    """
<style>
body {
      background-color: #1e1e2f;
      color: white;
}
.stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3);
}
h1 {
    text-align: center;
    font-size: 30px;
    color: white;
}
.stButton>button {
                  background: linear-gradient(45deg, #0b5394, #351c75);
                  color: white;
                  font-size: 18px;
                  paddingL 10px 20px;
                  border-radius: 10px;
                  transition: 0.3s;
                  box-shadow: 0px 5px 15px rgba(0, 201, 255, 0.4);
                  }
.stButton>button:hover {
                        transform: scale(1.05);
                        background: linear-gradient(45deg, #92fe9d, #00c9ff);
                        color: black;
                        }                 
.result-box {
    font-size: 20px;
    font-weight: bold;
    text-align: center;
    background: rgba(255, 255, 255, 0.1);
    padding: 25px;
    border-radius: 10px;
    margin-top: 20px;
    box-shadow: 0px 5px 15px rgba(0, 201, 255, 0.3);
    }
    .footer {
    text-align: center;
    margin-top: 50px;
    font-size: 14px;
    color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# title and description
st.markdown("<h1>Unit Converter using Python and Streamlit</h1>", unsafe_allow_html=True)
st.write("Easily convert between different units of length, weight and temperature ")

#sidebar menu

conversion_type = st.sidebar.selectbox("Select the conversion type", ["Length", "Weight", "Temperature"])                                                                                                                                           
value = st.number_input("Enter Value", value=0.0, min_value=0.0, step=0.1)

col1, col2 = st.columns(2)

if conversion_type == "Length":
    with col1:
        from_unit = st.selectbox("From", ["Meters", "Kilometers", "Centimeters", "Millimeters", "Miles", "Yards", "Feet", "Inches"])
    with col2:
        to_unit = st.selectbox("To", ["Meters", "Kilometers", "Centimeters", "Millimeters", "Miles", "Yards", "Feet", "Inches"])
elif conversion_type == "Weight":
    with col1:
        from_unit = st.selectbox("From", ["Kilograms", "Grams", "Milligrams", "Pounds", "Ounces"])
    with col2:
        to_unit = st.selectbox("To", ["Kilograms", "Grams", "Milligrams", "Pounds", "Ounces"])
elif conversion_type == "Temperature":
    with col1:
        from_unit = st.selectbox("From", ["Celsius", "Fahrenheit", "Kelvin"])
    with col2:  
        to_unit = st.selectbox("To", ["Celsius", "Fahrenheit", "Kelvin"])

# conversion logic
def length_converter(value, from_unit, to_unit):
  length_units = {
      "Meters": 1,
      "Kilometers": 1000,
      "Centimeters": 0.01,
      "Millimeters": 0.001,
      "Miles": 1609.34,
      "Yards": 0.9144,
      "Feet": 0.3048,
    "Inches": 0.0254
  }
  return value * length_units[from_unit] / length_units[to_unit]

def weight_converter(value, from_unit, to_unit):
  weight_units = {
      "Kilograms": 1,
      "Grams": 0.001,
      "Milligrams": 0.000001,
      "Pounds": 0.453592,
      "Ounces": 0.0283495
  }
  return value * weight_units[from_unit] / weight_units[to_unit]

def temperature_converter(value, from_unit, to_unit):
    if from_unit == "Celsius":
       return (value - 32) * 5.0/9.0 if to_unit == "Fahrenheit" else value + 273.15
    elif from_unit == "Fahrenheit":
        return (value - 273.15) if to_unit == "Celsius" else (value - 32) * 5.0/9.0     
    elif from_unit == "Kelvin":
        return (value - 273.15) * 9.0/5.0 + 32 if to_unit == "Fahrenheit" else value - 273.15
    return value

if st.button("Convert"):
    if conversion_type == "Length":
        result = length_converter(value, from_unit, to_unit)
    elif conversion_type == "Weight":
        result = weight_converter(value, from_unit, to_unit)
    elif conversion_type == "Temperature":
        result = temperature_converter(value, from_unit, to_unit)

    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="footer">
        <p>Created  by Qasim Hussain ❤️</p>
        </div>
        """,
        unsafe_allow_html=True
    )     

    
        