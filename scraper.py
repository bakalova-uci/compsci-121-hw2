import re
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
from analytics import analytics

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    extracted_links = []

    if resp.status != 200 or not resp.raw_response or not resp.raw_response.content:
        return extracted_links

    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

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

        valid_roots = [
            'ics.uci.edu', 
            'cs.uci.edu', 
            'informatics.uci.edu', 
            'stat.uci.edu'
        ]

        if not any(domain == root or domain.endswith('.' + root) for root in valid_roots):
            return False
        
        decoded_path = unquote(parsed.path.lower())

        defunct_subdomains = {
            'ibook.ics.uci.edu', 'cybert.ics.uci.edu', 
            'tippers.ics.uci.edu', 'auge.ics.uci.edu',
            'graphmod.ics.uci.edu', 'sli.ics.uci.edu', 
            'duke.ics.uci.edu', 'dblp.ics.uci.edu', 
            'chime.ics.uci.edu', 'cherry.ics.uci.edu',
            'coronavirustwittermap.ics.uci.edu', 'jujube.ics.uci.edu', 
            'news.nacs.uci.edu', 'asterixdb.ics.uci.edu', 'psearch.ics.uci.edu',
            'sourcerer.ics.uci.edu', 'gonet.genomics.ics.uci.edu', 
            'motifmap.ics.uci.edu', 'cgvw.ics.uci.edu', 'tippersweb.ics.uci.edu', 
            'seraja.ics.uci.edu', 'mt-live.ics.uci.edu', 'hombao.ics.uci.edu', 
            'www.isg.ics.uci.edu', 'tutors.ics.uci.edu'
        }

        if domain in defunct_subdomains:
            return False
        
        if 'flamingo.ics.uci.edu' in domain and '/localsearch/fuzzysearch' in decoded_path:
            return False
        if 'asterix.ics.uci.edu' in domain and '/fuzzyjoin-mapreduce' in decoded_path:
            return False

        crashing_dirs = [
            '~lboyles', '~alirezs1', '~rvernica', '~sjavanma', '~yonghuaw',
            '~jabbarvr', '~rares', '~shengyuj', '~yganjisa', '~jianlinc',
            '~akoratti', '~slan', '~ychen', '~agelfand', '~xzhu', '~iypark', 
            '~qliu1', '~akhavans', '~pjsadows', '~gghiasi', '~ajfrank', 
            '~sforouza', '~radum', '~welling', '~abehm', '~salsubai', 
            '~hshirani', '~ics214', '~icetindi', '~yunh', '~wengl', 
            '~nageshvh', '~ahmadia', '~jianfenj', '~taewok2',
            '~mahesh', '~jwickram', '~chair/research', '~ivan', '~cvondric', 
            '~dramanan', '~peiyunh', '~rjuang', '~bsajadi', '~shallman', 
            '~mkhademi', '~iporteou', '~hamidb', '~johnsong', '~dorendor', 
            '~rasadi', '~mamadoud', '~yyang8'
        ]
        if any(dir_name in decoded_path for dir_name in crashing_dirs):
            return False

        if 'cecs.uci.edu' in domain and ('/enews' in decoded_path or '/publications' in decoded_path):
            return False

        if re.search(r'/\d{4}-\d{2}-\d{2}', decoded_path):
            return False
        if re.search(r'/\d{4}/\d{2}/\d{2}', decoded_path):
            return False

        if 'wics.ics.uci.edu' in domain and '/events' in decoded_path:
            return False

        if re.search(r't?sld\d+\.htm', decoded_path):
            return False

        trap_patterns = [
            'doku.php', 'events/list', 'calendar', 'action=', 'share=', 'version=',      
            '?replytocom=', 'ical=', 'outlook-ical=', 'mac-ical=', '/day/', '/month/', '/week/',
            '/events/page/', 'marvin_wsgi_application.py', 'jmepopupweb.py', 'parentform=', 
            'filter%5b', 'filter[', 'enews-volume', 'search=', 'keywords=', 
            'orderby=', 'sort=', 'order=', 'mailman/', 'extreme-stories-',
            'timeline?from=', '&precision=', '/raw-attachment/', '/attachment/', '/zip-attachment/',
            '?format=txt', 'wp-login.php', 'redirect_to=', '?eventdisplay=', '?login='
        ]

        if any(trap in url.lower() for trap in trap_patterns):
            return False
        
        if re.search(r'\?C=[NMSD];O=[AD]', url):
            return False
        
        path_page_match = re.search(r'/page/(\d+)', url.lower())
        if path_page_match and int(path_page_match.group(1)) > 10:
            return False

        query_page_match = re.search(r'\?page=(\d+)', url.lower())
        if query_page_match and int(query_page_match.group(1)) > 10:
            return False

        query_traps = ['baldipage=', '?p=', '?page_id=']
        if any(q in url.lower() for q in query_traps):
            return False

        if len(url) > 175:
            return False
            
        path_segments = parsed.path.strip('/').split('/')
        if len(path_segments) > 12:
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|py|psp|seq|bib|nb|sql|apk|img|war"
            + r"|ppsx|tsv|xml|txt|java|class|sh|conf|svg|pps|fig|cls)$", decoded_path)

    except TypeError:
        print ("TypeError for ", parsed)
        raise
