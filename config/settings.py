"""
Configuration settings for Brand Price Scraper
"""

# Website configurations for scraping
WEBSITES = {
    'amazon': {
        'url': 'https://www.amazon.com/s',
        'search_param': 'k',
        'enabled': True,
        'region': 'US',
        'currency': 'USD'
    },
    'amazon_uk': {
        'url': 'https://www.amazon.co.uk/s',
        'search_param': 'k',
        'enabled': True,
        'region': 'UK',
        'currency': 'GBP'
    },
    'amazon_de': {
        'url': 'https://www.amazon.de/s',
        'search_param': 'k',
        'enabled': True,
        'region': 'Germany',
        'currency': 'EUR'
    },
    'ebay': {
        'url': 'https://www.ebay.com/sch/i.html',
        'search_param': '_nkw',
        'enabled': True,
        'region': 'US',
        'currency': 'USD'
    },
    'alibaba': {
        'url': 'https://www.alibaba.com/trade/search',
        'search_param': 'SearchText',
        'enabled': True,
        'region': 'China',
        'currency': 'CNY'
    },
    'mercadolibre': {
        'url': 'https://listado.mercadolibre.com.ar',
        'search_param': '_as',
        'enabled': True,
        'region': 'Argentina',
        'currency': 'ARS'
    },
}

# Headers for requests
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
]

# Scraping settings
TIMEOUT = 10
MAX_PRODUCTS_PER_SITE = 5
RETRY_ATTEMPTS = 3

# Data storage
DATA_FOLDER = 'data'
CACHE_DURATION = 3600  # 1 hour in seconds
