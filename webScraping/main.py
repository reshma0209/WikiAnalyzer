import requests
from bs4 import BeautifulSoup
import sqlite3
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import re

# Database setup
def setup_database(db_name="wiki_scraped_data.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT
        )
    """)
    conn.commit()
    return conn

# Function to scrape and process Wikipedia data
def scrape_and_process_wikipedia(url, db_name="wiki_scraped_data.db"):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract title and main content
        title = soup.find("h1", {"id": "firstHeading"}).get_text()
        content_div = soup.find("div", {"class": "mw-parser-output"})
        paragraphs = content_div.find_all("p")
        content = "\n".join([p.get_text() for p in paragraphs if p.get_text().strip()])

        # Save data to database
        conn = setup_database(db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO articles (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        print(f"Data saved to database: {db_name}")

        # Perform word analysis
        analyze_content(content, title)

    except Exception as e:
        print(f"Error occurred: {e}")

# Function to analyze and visualize word frequency
def analyze_content(content, title):
    # Clean and tokenize text
    words = re.findall(r'\w+', content.lower())
    word_count = Counter(words)

    # Display top 10 words
    top_words = word_count.most_common(10)
    print("Top 10 Words:")
    for word, freq in top_words:
        print(f"{word}: {freq}")

    # Generate and save a word cloud
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(word_count)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(f"Word Cloud for '{title}'", fontsize=16)
    plt.savefig(f"{title}_wordcloud.png")
    plt.show()

# Example usage
if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Orbital_(novel)"  # Replace with any Wikipedia URL
    scrape_and_process_wikipedia(url)
