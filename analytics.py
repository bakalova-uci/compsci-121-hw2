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

analytics = CrawlerAnalytics()

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    extracted_links = []

    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        return extracted_links
    
    try:
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')

        text_content = soup.get_text(separator=' ', strip=True)
        analytics.process_page(url, text_content)

        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(url, href)
                defragmented_url = absolute_url.split('#')[0]
                extracted_links.append(defragmented_url)
    except Exception as e:
        print(f"Error parsing {url}: {e}")
    
    return extracted_links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        domain = parsed.netloc.lower()

        allowed_domains = [
            ".ics.uci.edu",
            "ics.uci.edu",
            ".cs.uci.edu",
            "cs.uci.edu",
            ".informatics.uci.edu",
            "informatics.uci.edu",
            ".stat.uci.edu",
            "stat.uci.edu"
        ]

        if not any(domain == d or domain.endswith(d) for d in allowed_domains):
            return False
            
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
