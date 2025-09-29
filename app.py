from io import BytesIO
import streamlit as st
import pandas as pd
import os  

# 🎨 Custom Styling
st.set_page_config(page_title="Data Sweeper", layout="wide")

st.markdown(
    """
    <style>
    body { font-family: Arial, sans-serif; }
    .stButton>button { 
        background-color: #007BFF; color: white; font-size: 16px; 
        padding: 10px 24px; border-radius: 8px; border: none;
    }
    .stDownloadButton>button { 
        background-color: #28A745; color: white; font-size: 16px; 
        padding: 10px 24px; border-radius: 8px; border: none;
    }
    .stDataFrame { border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True
)

# 🏆 App Title
st.title("🚀 Data Sweeper")
st.write("Transform your files between **CSV** and **Excel** formats with built-in **data cleaning & visualization**!")

# 📂 File Upload Section
uploaded_files = st.file_uploader("📤 Upload your files (CSV or Excel)", type=['csv', 'xlsx'], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[1].lower()
        file_name = file.name

        # 📌 Read File Based on Type
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file, engine="openpyxl")
        else:
            st.error(f"❌ Unsupported file type: {file_ext}")
            continue  

        # 📝 Display File Info
        st.write(f"**📂 File:** `{file_name}`")
        st.write(f"**📏 File Size:** `{file.getbuffer().nbytes / 1024:.2f} KB`")

        # 🔍 Show Data Preview
        st.subheader("👀 Data Preview")
        st.dataframe(df.head())

        # 🛠️ Data Cleaning Options
        st.subheader("🛠️ Data Cleaning")

        if st.checkbox(f"🧹 Clean Data for `{file_name}`"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🗑️ Remove Duplicates from `{file_name}`"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates removed!")

            with col2:
                if st.button(f"🩹 Fill Missing Values for `{file_name}`"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing values filled!")

        # 🎯 Column Selection
        st.subheader("🎯 Select Columns to Keep")
        selected_columns = st.multiselect(f"📌 Select Columns for `{file_name}`", df.columns, default=df.columns)
        df = df[selected_columns]  

        # 📊 Data Visualization
        st.subheader("📊 Data Visualization")

        if st.checkbox(f"📍 Show Visualization for `{file_name}`"):
            numeric_df = df.select_dtypes(include=['number'])

            if not numeric_df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    chart_type = st.radio("📊 Select Chart Type", ["Bar Chart", "Line Chart", "Area Chart"], key=f"chart_{file_name}")
                with col2:
                    x_axis = st.selectbox("📌 Select X-axis", df.columns, key=f"x_{file_name}")
                    y_axis = st.selectbox("📌 Select Y-axis", numeric_df.columns, key=f"y_{file_name}")

                if x_axis and y_axis:
                    if df[x_axis].nunique() > 1:
                        chart_data = df[[x_axis, y_axis]].dropna()

                        if not chart_data.empty:
                            if chart_type == "Bar Chart":
                                st.bar_chart(chart_data.set_index(x_axis))
                            elif chart_type == "Line Chart":
                                st.line_chart(chart_data.set_index(x_axis))
                            elif chart_type == "Area Chart":
                                st.area_chart(chart_data.set_index(x_axis))
                        else:
                            st.warning("⚠️ No valid data points for the selected columns.")
                    else:
                        st.warning("⚠️ X-axis must have multiple unique values.")
                else:
                    st.warning("⚠️ Please select valid X and Y-axis columns.")
            else:
                st.warning("⚠️ No numeric columns available for visualization.")

        # 🔄 File Conversion
        st.subheader(f"🔄 Convert `{file_name}` to Another Format")
        conversion_type = st.radio(f"Convert `{file_name}` to:", ["CSV", "Excel"], key=file_name)

        if st.button(f"🔄 Convert `{file_name}`"):
            buffer = BytesIO()

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                converted_file_name = file_name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False, engine="openpyxl")
                converted_file_name = file_name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)

            # 📥 Download Button
            st.download_button(
                label=f"📥 Download `{converted_file_name}`",
                data=buffer,
                file_name=converted_file_name,
                mime=mime_type
            )

        st.success("✅ All files processed successfully!")

