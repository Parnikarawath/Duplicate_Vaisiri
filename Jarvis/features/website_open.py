import webbrowser
import re

POPULAR_WEBSITES = {
    'google': 'https://www.google.com',
    'youtube': 'https://www.youtube.com',
    'gmail': 'https://mail.google.com',
    'github': 'https://www.github.com',
    'stackoverflow': 'https://stackoverflow.com',
    'stack overflow': 'https://stackoverflow.com',
    'chatgpt': 'https://chatgpt.com',
    'openai': 'https://openai.com',
    'gemini': 'https://gemini.google.com',
    'reddit': 'https://www.reddit.com',
    'facebook': 'https://www.facebook.com',
    'instagram': 'https://www.instagram.com',
    'twitter': 'https://www.x.com',
    'x': 'https://www.x.com',
    'linkedin': 'https://www.linkedin.com',
    'amazon': 'https://www.amazon.com',
    'flipkart': 'https://www.flipkart.com',
    'netflix': 'https://www.netflix.com',
    'wikipedia': 'https://www.wikipedia.org',
    'whatsapp': 'https://web.whatsapp.com',
    'whatsapp web': 'https://web.whatsapp.com'
}

TLD_PATTERN = r'\.(com|in|org|net|edu|gov|io|co|ai|dev|info|biz|me|app|xyz|tech|online|store|site|club|live)\b'


def clean_domain(domain):
    if not domain:
        return ""
    domain = domain.strip().lower()
    # Remove leading phrases: "the website", "website", "the site", "site", "webpage", "the page", "page", "url", "link"
    domain = re.sub(r'^(the\s+)?(website|site|webpage|page|url|link|web|domain)\s+', '', domain, flags=re.IGNORECASE).strip()
    # Remove "dot" spoken as word e.g. "vimtech dot in" -> "vimtech.in"
    domain = re.sub(r'\s+dot\s+', '.', domain)
    # Remove any stray spaces within domain
    domain = domain.replace(' ', '')
    return domain


def website_opener(domain):
    """
    Cleans domain and opens the exact intended website in the default browser.
    """
    try:
        clean = clean_domain(domain)
        if not clean:
            return False

        if clean in POPULAR_WEBSITES:
            url = POPULAR_WEBSITES[clean]
            webbrowser.open(url)
            return True

        if clean.startswith("http://") or clean.startswith("https://"):
            webbrowser.open(clean)
            return True

        if re.search(TLD_PATTERN, clean, re.IGNORECASE) or "." in clean:
            url = f"https://www.{clean}" if not clean.startswith("www.") else f"https://{clean}"
        else:
            url = f"https://www.{clean}.com"

        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Website opener error: {e}")
        return False