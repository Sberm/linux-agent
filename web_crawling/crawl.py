from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import sys

def output_to_file(text_to_output, filename="output.txt", output_dir='./debug_output/'):
    """
    Outputs a given string to a file at the specified path.

    Args:
        text_to_output: The string that you want to write to the file.
        filepath: The full path to the file where the string will be written.
                Defaults to 'output.txt' in the current directory if not specified.
    """
    text_to_output = str(text_to_output)

    try:
        with open(output_dir + filename, 'w', encoding='UTF-8') as file:
            file.write(text_to_output)
            print(f"Successfully wrote to: {filename}")
    except Exception as e:
        print(f"An error occurred while writing to {filename}: {e}")

def get_thread_links_under_sub_archive(sub_archive_url):
    """ 
    Obtain all mails links under a sub-archive page.
    Args: 
        sub_archive_url: The URL of the sub-archive page, such as "https://lore.kernel.org/linux-perf-users/". 
    Returns: 
        a list of tuples (url, title). 
    """

    with sync_playwright() as p:
        # headless should be set to False, otherwise it will be blocked by anubis. 
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"🌐 Loading sub-archive page: {sub_archive_url}")
        page.goto(sub_archive_url, wait_until="domcontentloaded")
        # Wait until the <pre> tags appear. 
        page.wait_for_selector(selector = "pre", timeout=60000)  

        html = page.content()
        browser.close()

    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(html, 'html.parser')

    # All the mails links are under the first <pre> tag directly under <body>. 
    pre = soup.select_one('body > pre')

    if pre:
        link_soup = BeautifulSoup(pre.encode_contents(), 'html.parser')
        # links = [
        #     a['href'] if a['href'].startswith('http') else sub_archive_url + a['href']
        #     for a in link_soup.find_all('a', href=True)
        # ]
        links = []

        for a in link_soup.find_all('a', href=True):
            href = a['href']
            url = href if href.startswith('http') else sub_archive_url + href
            title = a.get_text(strip=True)
            links.append((url, title))

        print(f"✅ Found {len(links)} links in <pre> block.")
        return links

    else:
        print("❌ No <pre> block found.", file=sys.stderr)

    return None


def get_emails_under_thread(thread_url): 
    """ 
    Obtain a list of emails (stored in string) under given thread page. 
    Args: 
        thread_url: The URL of the thread page. 
    Returns: 
        A list of emails (stored in string).
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"🌐 Loading thread page: {thread_url}")
        page.goto(thread_url, timeout=60000)
        # Wait until the <pre> tags appear. 
        page.wait_for_selector(selector = "pre", timeout=60000)  
        html = page.content()
        browser.close()
    # Parse the HTML
    soup = BeautifulSoup(html, "html.parser")

    # Extract all <pre> tags directly under <body>. One email per <pre> tag. (Except for the last one)
    pre_tags = soup.select("body > pre")

    # Remove the last <pre> tag. 
    if pre_tags:
        pre_tags = pre_tags[:-1]
    else: 
        print("❌ No <pre> block found.", file=sys.stderr)

    email_content_list = []
    for pre in pre_tags: 
        lines = (pre.text + "\n").splitlines()

        # Remove all content after the last row with only '--'
        cutoff_index = None
        for i in reversed(range(len(lines))):
            if lines[i].strip() == "--":
                cutoff_index = i
                break 

        if cutoff_index is not None:
            lines = lines[:cutoff_index]

        content = str.join("\n", lines)
        email_content_list.append(content)

    return email_content_list

def get_threads():
    """ 
    Return a thread list with each entry [url, title, emails]. 
    """
    links = get_thread_links_under_sub_archive(sub_archive_url="https://lore.kernel.org/linux-perf-users/")
    
    threads = []
    
    for url, title in links:
        emails = get_emails_under_thread(thread_url=url)
        entry = {
            "url": url, 
            "title": title, 
            "emails": emails
        }
        threads.append(entry)
    
    return threads


def test():
    links = get_thread_links_under_sub_archive(sub_archive_url="https://lore.kernel.org/linux-perf-users/")
    email_content_list = get_emails_under_thread(thread_url=links[0][0])
    output_to_file(email_content_list[0], filename="one email example.txt")
    return

if __name__ == '__main__':
    # test()
    print('hello')
    # get_threads()