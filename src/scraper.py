"""
Web scraper for extracting product prices from various e-commerce sites
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from datetime import datetime
import logging
from config.settings import USER_AGENTS, TIMEOUT, RETRY_ATTEMPTS, MAX_PRODUCTS_PER_SITE
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceScraper:
    """Scraper for fetching product prices from e-commerce websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.products = []
        
    def get_headers(self) -> Dict:
        """Get random user agent headers"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def scrape_amazon(self, brand_name: str, region: str = 'US') -> List[Dict]:
        """
        Scrape Amazon for brand products
        
        Args:
            brand_name: Brand name to search
            region: Region code (US, UK, DE)
            
        Returns:
            List of product dictionaries with price info
        """
        try:
            if region == 'US':
                url = 'https://www.amazon.com/s'
            elif region == 'UK':
                url = 'https://www.amazon.co.uk/s'
            elif region == 'DE':
                url = 'https://www.amazon.de/s'
            else:
                url = 'https://www.amazon.com/s'
            
            params = {'k': brand_name}
            
            response = self.session.get(url, params=params, headers=self.get_headers(), timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers
            for item in soup.find_all('div', {'data-component-type': 's-search-result'})[:MAX_PRODUCTS_PER_SITE]:
                try:
                    title_elem = item.find('h2', {'class': 'a-size-mini'})
                    title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                    
                    # Current price
                    price_whole = item.find('span', {'class': 'a-price-whole'})
                    current_price = price_whole.get_text(strip=True) if price_whole else 'N/A'
                    
                    # Product link
                    link_elem = item.find('a', {'class': 'a-link-normal'})
                    product_url = link_elem.get('href', '') if link_elem else 'N/A'
                    
                    product = {
                        'brand': brand_name,
                        'site': 'Amazon',
                        'region': region,
                        'title': title,
                        'current_price': self._clean_price(current_price),
                        'original_price': self._clean_price(current_price),  # Would need additional logic
                        'currency': 'USD' if region == 'US' else 'GBP' if region == 'UK' else 'EUR',
                        'url': product_url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    products.append(product)
                except Exception as e:
                    logger.warning(f"Error parsing Amazon product: {e}")
                    continue
            
            return products
            
        except requests.RequestException as e:
            logger.error(f"Error scraping Amazon: {e}")
            return []
    
    def scrape_ebay(self, brand_name: str) -> List[Dict]:
        """
        Scrape eBay for brand products
        """
        try:
            url = 'https://www.ebay.com/sch/i.html'
            params = {'_nkw': brand_name}
            
            response = self.session.get(url, params=params, headers=self.get_headers(), timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Find product containers
            for item in soup.find_all('div', {'class': 's-item'})[:MAX_PRODUCTS_PER_SITE]:
                try:
                    title_elem = item.find('h2', {'class': 's-item__title'})
                    title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                    
                    # Price
                    price_elem = item.find('span', {'class': 's-item__price'})
                    current_price = price_elem.get_text(strip=True) if price_elem else 'N/A'
                    
                    # Product link
                    link_elem = item.find('a', {'class': 's-item__link'})
                    product_url = link_elem.get('href', '') if link_elem else 'N/A'
                    
                    product = {
                        'brand': brand_name,
                        'site': 'eBay',
                        'region': 'US',
                        'title': title,
                        'current_price': self._clean_price(current_price),
                        'original_price': self._clean_price(current_price),
                        'currency': 'USD',
                        'url': product_url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    products.append(product)
                except Exception as e:
                    logger.warning(f"Error parsing eBay product: {e}")
                    continue
            
            return products
            
        except requests.RequestException as e:
            logger.error(f"Error scraping eBay: {e}")
            return []
    
    def scrape_multiple_sites(self, brand_name: str) -> List[Dict]:
        """
        Scrape multiple sites for a brand
        
        Args:
            brand_name: Brand to search for
            
        Returns:
            Combined list of products from all sites
        """
        all_products = []
        
        # Scrape Amazon regions
        for region in ['US', 'UK', 'DE']:
            logger.info(f"Scraping Amazon {region} for {brand_name}...")
            amazon_products = self.scrape_amazon(brand_name, region)
            all_products.extend(amazon_products)
        
        # Scrape eBay
        logger.info(f"Scraping eBay for {brand_name}...")
        ebay_products = self.scrape_ebay(brand_name)
        all_products.extend(ebay_products)
        
        return all_products
    
    @staticmethod
    def _clean_price(price_str: str) -> Optional[float]:
        """
        Clean and extract numeric price from string
        """
        if not price_str or price_str == 'N/A':
            return None
        
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[^\d.,]', '', price_str.strip())
        cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except ValueError:
            return None


class DataCollector:
    """Collect and manage scraped data"""
    
    def __init__(self):
        self.scraper = PriceScraper()
    
    def collect_brand_data(self, brand_name: str) -> List[Dict]:
        """
        Collect data for a brand from multiple sources
        """
        logger.info(f"Starting data collection for brand: {brand_name}")
        products = self.scraper.scrape_multiple_sites(brand_name)
        logger.info(f"Collected {len(products)} products")
        return products
