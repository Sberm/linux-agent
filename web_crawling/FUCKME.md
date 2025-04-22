# Web Crawling Document

run this shit command: 

```
xvfb-run python ./web_crawling/crawl.py
```
Currently it's just a simple demo. You can see one email example under `./web_crawling/ouput/` directory. 

To change the output directory, change the parameter in line 6. 

Enjoy your pained ass!

## Current Problems

I have set a timeout so that the crawling speed is too slow.


## How I crawl these pages?

The website is protected by anubis, a tool that can identify bots. 

Generally, I use playwright to obtain html pages.

```python
with sync_playwright() as p:
    # headless should be set to False, otherwise it will be blocked by anubis. 
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto(url, timeout=60000)
    # Wait until the <pre> tags appear. 
    page.wait_for_selector(selector = "pre", timeout=60000)  

    html = page.content()
    browser.close()
```

And use BeautifulSoup APIs to parse the HTML to text file. 

To be fulfilled

