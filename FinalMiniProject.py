import streamlit as st
import hashlib
from bs4 import BeautifulSoup
import requests
import os

# User database (for demonstration purposes)
USER_DATABASE = {
    'user1': hashlib.sha256('password1'.encode()).hexdigest(),
    'user2': hashlib.sha256('password2'.encode()).hexdigest()
}

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login function
def login(username, password):
    hashed_password = USER_DATABASE.get(username)
    if hashed_password and hashed_password == hash_password(password):
        return True
    else:
        return False

# Signup function
def signup(username, password):
    if username not in USER_DATABASE:
        USER_DATABASE[username] = hash_password(password)
        return True
    else:
        return False

@st.cache_data
def get_quotes():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    URL = 'https://www.goodreads.com/quotes'
    webpage = requests.get(URL, headers=headers)
    soup = BeautifulSoup(webpage.text, 'html.parser')
    quoteText = soup.find_all('div', attrs={'class': 'quoteText'})
    quotes = []
    authors = []
    for i in quoteText:
        quote = i.text.strip().split('\n')[0]
        author = i.find('span', attrs={'class': 'authorOrTitle'}).text.strip().lower()
        quotes.append(quote)
        authors.append(author)
    return quotes, authors

def search_by_author(quotes, authors, search_author):
    index = [idx for idx, author in enumerate(authors) if search_author.lower() in author]
    if index:
        st.success(f"Quotes by {search_author}:")
        return [quotes[idx] for idx in index], [authors[idx] for idx in index]
    else:
        st.warning(f"No quotes found for author: {search_author}")
        return [], []

def search_by_keyword(quotes, authors, search_keyword):
    filtered_quotes = []
    filtered_authors = []
    for idx, quote in enumerate(quotes):
        if search_keyword.lower() in quote.lower():
            filtered_quotes.append(quote)
            filtered_authors.append(authors[idx])
    if filtered_quotes:
        st.success(f"Quotes containing '{search_keyword}':")
        return filtered_quotes, filtered_authors
    else:
        st.warning(f"No quotes found containing keyword: {search_keyword}")
        return [], []

def display_quotes(quotes, authors):
    liked_quotes = st.session_state.get('liked_quotes', {})
    if isinstance(liked_quotes, list):
        liked_quotes = {q: 1 for q in liked_quotes}
        st.session_state['liked_quotes'] = liked_quotes

    for quote, author in zip(quotes, authors):
        like_count = liked_quotes.get(quote, 0)
        like_button_color = 'white' if like_count == 0 else 'red'
        st.write(f"- {quote} - {author} (Likes: {like_count})")
        like_clicked = st.button(f"Like", key=f"like_button_{quote}", on_click=like_quote, args=(quote, liked_quotes))

@st.cache_data
def like_quote(quote, liked_quotes):
    if quote in liked_quotes:
        liked_quotes[quote] += 1
    else:
        liked_quotes[quote] = 1
    st.session_state['liked_quotes'] = liked_quotes

def main():
    st.title("QuotesInn")
    if 'liked_quotes' not in st.session_state:
        st.session_state['liked_quotes'] = {}

    # Page navigation
    page = st.sidebar.radio("Navigation", ["Login", "Signup", "Quotes"])

    if page == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login(username, password):
                st.success("Login successful!")
                st.sidebar.success(f"Logged in as {username}")
                st.session_state.logged_in = True
            else:
                st.error("Invalid username or password")

    elif page == "Signup":
        st.subheader("Signup")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Signup"):
            if new_password == confirm_password:
                if signup(new_username, new_password):
                    st.success("Signup successful! You can now login.")
                else:
                    st.error("Username already exists.")
            else:
                st.error("Passwords do not match.")

    elif page == "Quotes":
        if st.session_state.get('logged_in'):
            st.sidebar.write(f"Logged in as: {st.session_state.get('username')}")
            if st.sidebar.button("Logout"):
                st.session_state.pop("logged_in", None)
                st.session_state.pop("username", None)
                st.sidebar.warning("You have been logged out")

            option = st.radio("Select search option:", ("Search by Author", "Search by Keyword", "Show All Quotes"))
            quotes, authors = get_quotes()

            if option == "Search by Author":
                search_author = st.text_input("Enter the name of the author:")
                if st.button("Search"):
                    if search_author:
                        filtered_quotes, filtered_authors = search_by_author(quotes, authors, search_author)
                        display_quotes(filtered_quotes, filtered_authors)

            elif option == "Search by Keyword":
                search_keyword = st.text_input("Enter the keyword to find a quote:")
                if st.button("Search"):
                    if search_keyword:
                        filtered_quotes, filtered_authors = search_by_keyword(quotes, authors, search_keyword)
                        display_quotes(filtered_quotes, filtered_authors)

            elif option == "Show All Quotes":
                display_quotes(quotes, authors)
        else:
            st.warning("Please log in to access the quotes.")

if __name__ == "__main__":
    main()