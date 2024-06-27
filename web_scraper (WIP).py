import requests
from bs4 import BeautifulSoup
from transformers import pipeline

def fetch_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract the main content of the article
    article_content = soup.find('div', class_='entry-content')
    if article_content:
        paragraphs = article_content.find_all('p')
        full_text = ' '.join([para.get_text() for para in paragraphs])
        return full_text
    return None

def get_security_news(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    for item in soup.find_all('h2', class_='entry-title'):
        title = item.get_text()
        link = item.find('a')['href']
        articles.append((title, link))

    return articles

def chunk_text(text, max_length):
    sentences = text.split('. ')
    current_chunk = []
    current_length = 0
    chunks = []
    
    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_length:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_length
        
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def summarize_text(text, summarizer):
    max_input_length = 500  # Adjust as per the model's token limit
    chunks = chunk_text(text, max_input_length)
    summary = []

    for chunk in chunks:
        summarized_chunk = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summary.append(summarized_chunk[0]['summary_text'])
    
    return ' '.join(summary)

def main():
    url = input("Please enter URL you want the summary of: ")
    print(f"Fetching latest articles from {url}")
    articles = get_security_news(url)

    summarizer = pipeline("summarization")

    if articles:
        print("Latest Security News Articles and Summaries:")
        for idx, (title, link) in enumerate(articles, start=1):
            print(f"{idx}. {title}\n   Link: {link}")

            # Fetch the article content
            article_content = fetch_article_content(link)
            if article_content:
                try:
                    # Generate a summary using the transformers library
                    article_summary = summarize_text(article_content, summarizer)
                    print(f"   Summary: {article_summary}\n")
                except Exception as e:
                    print(f"   Summary: Could not generate summary ({e})\n")
            else:
                print("   Summary: Could not fetch article content\n")
    else:
        print("No articles found or an error occurred.")

if __name__ == "__main__":
    main()
