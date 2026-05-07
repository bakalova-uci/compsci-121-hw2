import re
from collections import Counter
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

class CrawlerAnalytics:
    def __init__(self, stopwords_file="stopwords.txt"):
        self.unique_urls = set()
        self.longest_page = {"url": "", "word_count": 0}
        self.word_frequencies = Counter()
        self.subdomains = Counter()
        self.stop_words = self._load_stopwords(stopwords_file)
    
    def _load_stopwords(self, filepath):
        stop_words = set()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        stop_words.add(word)
            print(f"Succsesfully loaded {len(stop_words)} stop words from {filepath}")
        except FileNotFoundError:
            print(f"Warning: file for stop words not found: '{filepath}'")
        return stop_words
    
    def process_page(self, url, text):
        self.unique_urls.add(url)

        words = re.findall(r'[a-zA-Z0-9]{2,}', text.lower())
        word_count = len(words)

        if word_count > self.longest_page["word_count"]:
            self.longest_page = {"url": url, "word_count": word_count}
        
        valid_words = [w for w in words if w not in self.stop_words]
        self.word_frequencies.update(valid_words)

        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if domain.endswith("ics.uci.edu"):
            self.subdomains[domain] += 1
    
    def print_report(self):
        print("\n" + "="*50)
        print("CRAWLER ANALYTICS REPORT")
        print("="*50)
        print(f"1. Unique pages found: {len(self.unique_urls)}")
        print(f"2. Longest page: {self.longest_page['url']} ({self.longest_page['word_count']} words)")
        
        print("\n3. Top 50 most common words:")
        for word, count in self.word_frequencies.most_common(50):
            print(f"   {word}: {count}")
            
        print("\n4. Subdomains found in ics.uci.edu:")
        for subdomain, count in sorted(self.subdomains.items()):
            print(f"   {subdomain}, {count}")
        print("="*50 + "\n")

analytics = CrawlerAnalytics()