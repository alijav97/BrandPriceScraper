"""
Regional Brand Scraper - Scrapes official brand websites across different regions
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
from datetime import datetime
import logging
import json
import random
from config.settings import USER_AGENTS, TIMEOUT, RETRY_ATTEMPTS
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegionalBrandScraper:
    """Scraper for fetching products from official brand regional websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.brand_sites = self._load_brand_sites()
        
    def _load_brand_sites(self) -> Dict:
        """Load brand regional sites from config"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'brand_sites.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading brand sites config: {e}")
            return {}
    
    def get_headers(self) -> Dict:
        """Get random user agent headers"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def get_available_brands(self) -> List[str]:
        """Get list of available brands"""
        return list(self.brand_sites.keys())
    
    def get_available_regions(self, brand_name: str) -> List[str]:
        """Get available regions for a brand"""
        if brand_name in self.brand_sites:
            return list(self.brand_sites[brand_name]['regions'].keys())
        return []
    
    def scrape_brand_regional(self, brand_name: str, regions: List[str]) -> List[Dict]:
        """
        Scrape products from a brand's regional websites
        
        Args:
            brand_name: Brand name (e.g., 'Lululemon', 'Nike')
            regions: List of regions to scrape (e.g., ['US', 'UK', 'UAE'])
            
        Returns:
            List of products with prices across regions
        """
        if brand_name not in self.brand_sites:
            logger.warning(f"Brand {brand_name} not found in config")
            return []
        
        brand_config = self.brand_sites[brand_name]
        all_products = {}
        
        for region in regions:
            if region not in brand_config['regions']:
                logger.warning(f"Region {region} not available for {brand_name}")
                continue
            
            region_info = brand_config['regions'][region]
            logger.info(f"Scraping {brand_name} from {region}...")
            
            products = self._scrape_region(
                brand_name=brand_name,
                region=region,
                url=region_info['url'],
                currency_code=region_info['currency_code'],
                currency=region_info['currency']
            )
            
            # Merge products by name
            for product in products:
                product_name = product.get('name', '').lower()
                if product_name not in all_products:
                    all_products[product_name] = {
                        'name': product['name'],
                        'prices': {},
                        'links': {}
                    }
                all_products[product_name]['prices'][region] = {
                    'price': product['price'],
                    'currency': product['currency'],
                    'currency_code': product['currency_code']
                }
                all_products[product_name]['links'][region] = product.get('link', '')
        
        # Convert dict to list
        return [
            {
                'name': product['name'],
                'brand': brand_name,
                'prices': product['prices'],
                'links': product['links'],
                'timestamp': datetime.now().isoformat()
            }
            for product in all_products.values()
        ]
    
    def _scrape_region(self, brand_name: str, region: str, url: str, 
                      currency_code: str, currency: str) -> List[Dict]:
        """
        Scrape a specific regional website
        
        Args:
            brand_name: Brand name
            region: Region code
            url: Base URL of the regional site
            currency_code: Currency symbol (e.g., '$', '£')
            currency: Currency name (USD, GBP)
            
        Returns:
            List of products from that region
        """
        products = []
        
        try:
            headers = self.get_headers()
            response = self.session.get(url, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract products using common selectors
            # Note: This is a generic approach; specific brands may need custom selectors
            
            # Look for product containers (common patterns)
            product_selectors = [
                'div[data-product]',
                'div.product-item',
                'div.product-card',
                'article.product',
                'div[class*="product"]'
            ]
            
            for selector in product_selectors:
                product_elements = soup.select(selector)
                if product_elements:
                    logger.info(f"Found {len(product_elements)} products using selector: {selector}")
                    
                    for element in product_elements[:10]:  # Limit to 10 products per region
                        product = self._extract_product_info(
                            element, brand_name, region, currency_code, currency
                        )
                        if product:
                            products.append(product)
                    break
            
            if not products:
                logger.warning(f"No products found for {brand_name} in {region}")
            
            return products
            
        except requests.RequestException as e:
            logger.error(f"Error scraping {brand_name} {region}: {e}")
            return []
    
    def _extract_product_info(self, element, brand_name: str, region: str,
                             currency_code: str, currency: str) -> Optional[Dict]:
        """
        Extract product information from HTML element
        
        Args:
            element: BeautifulSoup element
            brand_name: Brand name
            region: Region code
            currency_code: Currency symbol
            currency: Currency name
            
        Returns:
            Product dictionary or None
        """
        try:
            # Try to extract product name
            name_selectors = [
                'h2', 'h1', 'a.product-name', 'span.product-title',
                '[class*="title"]', '[class*="name"]'
            ]
            
            name = None
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    if name and len(name) > 3:  # Ensure it's not too short
                        break
            
            if not name:
                return None
            
            # Try to extract price
            price_selectors = [
                '[class*="price"]',
                'span.price',
                'div.price',
                '[data-price]',
                'p[class*="price"]'
            ]
            
            price = None
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extract numbers from price text
                    price_match = re.search(r'[\d,]+\.?\d*', price_text)
                    if price_match:
                        price_str = price_match.group().replace(',', '')
                        try:
                            price = float(price_str)
                            break
                        except ValueError:
                            continue
            
            if price is None:
                return None
            
            # Try to extract link
            link = None
            link_elem = element.find('a', href=True)
            if link_elem:
                link = link_elem.get('href', '')
                if not link.startswith('http'):
                    # Make relative URLs absolute
                    base_url = '/'.join(self.brand_sites[brand_name]['regions'][region]['url'].split('/')[:3])
                    link = base_url + link if link.startswith('/') else link
            
            return {
                'name': name,
                'brand': brand_name,
                'region': region,
                'price': price,
                'currency': currency,
                'currency_code': currency_code,
                'link': link,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.debug(f"Error extracting product info: {e}")
            return None


class RegionalDataCollector:
    """High-level interface for collecting regional brand data"""
    
    def __init__(self):
        self.scraper = RegionalBrandScraper()
    
    def collect_brand_data(self, brand_name: str, regions: Optional[List[str]] = None) -> List[Dict]:
        """
        Collect data for a brand across regions
        
        Args:
            brand_name: Brand name
            regions: Specific regions to scrape (or None for all available)
            
        Returns:
            List of products with regional prices
        """
        available_regions = self.scraper.get_available_regions(brand_name)
        
        if not available_regions:
            return []
        
        regions_to_scrape = regions if regions else available_regions
        return self.scraper.scrape_brand_regional(brand_name, regions_to_scrape)
    
    def get_brands_list(self) -> List[str]:
        """Get list of all available brands"""
        return self.scraper.get_available_brands()
