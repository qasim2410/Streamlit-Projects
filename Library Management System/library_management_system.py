import streamlit as st
import json
import pandas as pd

# Load or initialize library
def load_library():
    try:
        with open("library.txt", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_library(library):
    with open("library.txt", "w") as file:
        json.dump(library, file, indent=4)

library = load_library()

# Page config
st.set_page_config(page_title="📚 Personal Library Manager", page_icon="📖", layout="wide")

# Custom CSS for premium look
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #232526, #414345);
            font-family: 'Segoe UI', sans-serif;
        }
        .title {
            text-align: center;
            color: #f5f5f5;
            font-size: 40px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, #4facfe, #00f2fe);
            color: white;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            background: linear-gradient(90deg, #00f2fe, #4facfe);
        }
        .card {
            padding: 15px;
            border-radius: 12px;
            background: rgba(255,255,255,0.07);
            margin-bottom: 15px;
            box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<div class='title'>📚 Personal Library Manager</div>", unsafe_allow_html=True)

# Sidebar menu
menu = st.sidebar.radio("📌 Menu", ["Add Book", "Remove Book", "Search Book", "View All Books", "Statistics", "Save Library", "Load Library", "Exit"])

# Add book
if menu == "Add Book":
    st.subheader("➕ Add a New Book")
    with st.form("add_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        year = st.text_input("Publication Year")
        genre = st.text_input("Genre")
        read = st.selectbox("Have you read it?", ["Yes", "No"])
        submitted = st.form_submit_button("Add Book")
        if submitted:
            book = {
                "title": title,
                "author": author,
                "year": year,
                "genre": genre,
                "read": read == "Yes"
            }
            library.append(book)
            st.success("✅ Book added successfully!")

# Remove book
elif menu == "Remove Book":
    st.subheader("🗑 Remove a Book")
    if library:
        titles = [book["title"] for book in library]
        choice = st.selectbox("Select a book to remove", titles)
        if st.button("Remove"):
            library = [book for book in library if book["title"] != choice]
            st.success(f"✅ '{choice}' removed successfully!")
    else:
        st.warning("⚠️ No books available to remove.")

# Search book
elif menu == "Search Book":
    st.subheader("🔎 Search Book")
    query = st.text_input("Enter title to search")
    if query:
        results = [book for book in library if query.lower() in book["title"].lower()]
        if results:
            for book in results:
                st.markdown(f"<div class='card'>📖 **{book['title']}** by *{book['author']}* ({book['year']})<br>📚 Genre: {book['genre']}<br>✅ Read: {book['read']}</div>", unsafe_allow_html=True)
        else:
            st.error("❌ No books found with that title.")

# View all books
elif menu == "View All Books":
    st.subheader("📖 All Books in Library")
    if library:
        df = pd.DataFrame(library)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ No books in library.")

# Statistics
elif menu == "Statistics":
    st.subheader("📊 Library Statistics")
    total = len(library)
    read_books = sum(1 for book in library if book["read"])
    unread_books = total - read_books

    col1, col2, col3 = st.columns(3)
    col1.metric("📚 Total Books", total)
    col2.metric("✅ Books Read", read_books)
    col3.metric("⏳ Books Unread", unread_books)

# Save library
elif menu == "Save Library":
    save_library(library)
    st.success("✅ Library saved successfully!")

# Load library
elif menu == "Load Library":
    library = load_library()
    st.success("✅ Library loaded successfully!")

# Exit (just a goodbye message)
elif menu == "Exit":
    st.info("👋 Goodbye! Thanks for using Personal Library Manager.")

# Auto-save on every action
save_library(library)

















