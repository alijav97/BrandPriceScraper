"""
Product Finder - Finds products on discovered brand sites
Uses multiple strategies: search pages, category pages, and direct scraping
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import random
import time
from config.settings import USER_AGENTS, TIMEOUT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductFinder:
    """Find products on brand websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_headers(self) -> Dict:
        """Get random user agent headers"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def get_top_products(self, site_url: str, brand_name: str, limit: int = 10) -> List[Dict]:
        """
        Get top products from a site via search/category pages
        
        Args:
            site_url: Website URL
            brand_name: Brand name
            limit: Number of products to fetch
            
        Returns:
            List of product dictionaries
        """
        products = []
        
        # Try different strategies to find products
        strategies = [
            ('search_all', self._search_products_on_site(site_url, "all", limit)),
            ('shop_page', self._scrape_shop_page(site_url, limit)),
            ('category_page', self._scrape_category_page(site_url, limit)),
            ('collections', self._scrape_collections_page(site_url, limit)),
        ]
        
        for strategy_name, strategy_products in strategies:
            if strategy_products and len(strategy_products) >= 3:
                logger.info(f"Found products via {strategy_name}: {len(strategy_products)} items")
                return strategy_products[:limit]
        
        logger.info(f"Found {len(products)} total products on {site_url}")
        return products
    
    def _search_products_on_site(self, site_url: str, query: str = "all", limit: int = 10) -> List[Dict]:
        """Try to search for products on the site"""
        products = []
        base_url = site_url.rstrip('/')
        
        # Common search URL patterns
        search_patterns = [
            f"{base_url}/search?q={query}",
            f"{base_url}/search?query={query}",
            f"{base_url}/products?search={query}",
            f"{base_url}/shop?search={query}",
            f"{base_url}/collections/all",  # Common Shopify pattern
            f"{base_url}/products",  # Direct products page
        ]
        
        for search_url in search_patterns:
            try:
                logger.debug(f"Trying {search_url}")
                time.sleep(random.uniform(0.5, 1.5))  # Rate limiting
                
                response = self.session.get(search_url, headers=self.get_headers(), timeout=TIMEOUT)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    products = self._extract_products_from_page(soup, site_url, limit)
                    
                    if len(products) >= 3:
                        return products
            except Exception as e:
                logger.debug(f"Error trying {search_url}: {e}")
                continue
        
        return products
    
    def _scrape_shop_page(self, site_url: str, limit: int = 10) -> List[Dict]:
        """Try to scrape a shop/products page"""
        products = []
        base_url = site_url.rstrip('/')
        
        shop_urls = [
            f"{base_url}/shop",
            f"{base_url}/products",
            f"{base_url}/catalog",
            f"{base_url}/store",
            base_url  # Try homepage
        ]
        
        for shop_url in shop_urls:
            try:
                logger.debug(f"Scraping {shop_url}")
                time.sleep(random.uniform(0.5, 1.5))
                
                response = self.session.get(shop_url, headers=self.get_headers(), timeout=TIMEOUT)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    products = self._extract_products_from_page(soup, site_url, limit)
                    
                    if len(products) >= 3:
                        return products
            except Exception as e:
                logger.debug(f"Error scraping {shop_url}: {e}")
                continue
        
        return products
    
    def _scrape_category_page(self, site_url: str, limit: int = 10) -> List[Dict]:
        """Try to scrape a category page"""
        products = []
        base_url = site_url.rstrip('/')
        
        try:
            # First, find category pages
            time.sleep(random.uniform(0.5, 1.5))
            response = self.session.get(base_url, headers=self.get_headers(), timeout=TIMEOUT)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find category links
                category_links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()
                    
                    # Look for category/collection links
                    if any(word in href.lower() for word in ['category', 'collection', 'men', 'women', 'product']):
                        if len(text) > 2 and len(text) < 30 and text not in ['home', 'about', 'contact']:
                            category_links.append(href if href.startswith('http') else base_url + ('' if href.startswith('/') else '/') + href)
                
                # Try first few categories
                for cat_url in category_links[:3]:
                    try:
                        logger.debug(f"Trying category: {cat_url}")
                        time.sleep(random.uniform(0.5, 1.5))
                        
                        cat_response = self.session.get(cat_url, headers=self.get_headers(), timeout=TIMEOUT)
                        if cat_response.status_code == 200:
                            cat_soup = BeautifulSoup(cat_response.content, 'html.parser')
                            products = self._extract_products_from_page(cat_soup, site_url, limit)
                            
                            if len(products) >= 3:
                                return products
                    except:
                        continue
        
        except Exception as e:
            logger.debug(f"Error scraping categories: {e}")
        
        return products
    
    def _scrape_collections_page(self, site_url: str, limit: int = 10) -> List[Dict]:
        """Try Shopify collections pattern"""
        products = []
        base_url = site_url.rstrip('/')
        
        collections_urls = [
            f"{base_url}/collections/all",
            f"{base_url}/collections/products",
        ]
        
        for coll_url in collections_urls:
            try:
                logger.debug(f"Trying collections: {coll_url}")
                time.sleep(random.uniform(0.5, 1.5))
                
                response = self.session.get(coll_url, headers=self.get_headers(), timeout=TIMEOUT)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    products = self._extract_products_from_page(soup, site_url, limit)
                    
                    if len(products) >= 3:
                        return products
            except:
                continue
        
        return products
    
    def _extract_products_from_page(self, soup: BeautifulSoup, site_url: str, limit: int) -> List[Dict]:
        """
        Extract products from a page using multiple strategies
        """
        products = []
        
        # Strategy 1: Common product containers
        selectors = [
            'div[class*="product"]',
            'article[class*="product"]',
            'li[class*="product"]',
            'div[class*="item"]',
            'article[class*="item"]',
            'div[data-product-id]',
            'article[data-product]',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if len(elements) >= 3:
                logger.debug(f"Found {len(elements)} elements with selector: {selector}")
                for element in elements[:limit]:
                    product = self._extract_product_from_element(element, site_url)
                    if product:
                        products.append(product)
                
                if len(products) >= 3:
                    return products
        
        # Strategy 2: Find all price elements and work backwards
        if not products:
            products = self._extract_by_prices(soup, site_url, limit)
        
        return products
    
    def _extract_by_prices(self, soup: BeautifulSoup, site_url: str, limit: int) -> List[Dict]:
        """Extract products by finding prices and working backwards"""
        products = []
        
        # Find all price-like patterns
        price_pattern = r'\$[\d,]+\.?\d*|€[\d,]+\.?\d*|£[\d,]+\.?\d*'
        
        for element in soup.find_all(['div', 'article', 'li', 'span', 'p']):
            text = element.get_text(strip=True)
            
            # If element contains a price, try to extract product info
            if re.search(price_pattern, text):
                # Get parent context
                parent = element.parent
                parent_text = parent.get_text(strip=True) if parent else text
                
                # Extract name (first line or title nearby)
                name = ""
                for child in element.find_all(['h2', 'h3', 'h4', 'a', 'span'], limit=1):
                    name = child.get_text(strip=True)
                    if len(name) > 5:
                        break
                
                if not name:
                    name = parent_text[:50] if parent else text[:50]
                
                # Extract price
                price_match = re.search(price_pattern, text)
                if price_match:
                    price_str = price_match.group()
                    try:
                        price = float(re.sub(r'[^\d.]', '', price_str))
                    except:
                        price = 0
                    
                    if price > 0 and len(name) > 5:
                        product = {
                            'name': name,
                            'price': price,
                            'currency': 'USD' if '$' in price_str else ('EUR' if '€' in price_str else 'GBP'),
                            'url': site_url,
                            'image': ''
                        }
                        
                        # Check if we already have this product
                        if not any(p['name'].lower() == product['name'].lower() for p in products):
                            products.append(product)
                        
                        if len(products) >= limit:
                            return products
        
        return products
    
    def _extract_product_from_element(self, element, site_url: str) -> Optional[Dict]:
        """Extract product info from a single element"""
        try:
            product = {'url': site_url, 'image': ''}
            
            # Extract name
            name_elem = element.find(['h2', 'h3', 'h4', 'a'])
            product['name'] = name_elem.get_text(strip=True) if name_elem else 'Product'
            
            # Extract price
            price = 0
            price_patterns = [
                r'[\$£€][\s]*[\d,]+\.?\d*',
                r'[\d,]+\.?\d*[\s]*(?:USD|EUR|GBP)',
            ]
            
            element_text = element.get_text()
            for pattern in price_patterns:
                match = re.search(pattern, element_text)
                if match:
                    try:
                        price_str = match.group()
                        price = float(re.sub(r'[^\d.]', '', price_str))
                        if price > 0:
                            break
                    except:
                        pass
            
            product['price'] = price
            
            # Extract currency
            element_text_upper = element.get_text().upper()
            if '€' in element.get_text() or 'EUR' in element_text_upper:
                product['currency'] = 'EUR'
            elif '£' in element.get_text() or 'GBP' in element_text_upper:
                product['currency'] = 'GBP'
            else:
                product['currency'] = 'USD'
            
            # Extract image
            img = element.find('img')
            if img:
                product['image'] = img.get('src', '')
            
            if product['price'] > 0:
                return product
            
        except Exception as e:
            logger.debug(f"Error extracting product: {e}")
        
        return None
    
    def search_products(self, site_url: str, search_query: str, brand_name: str, retry_count: int = 2) -> List[Dict]:
        """
        Search for specific products on a site
        
        Args:
            site_url: Website URL
            search_query: Product name/query to search
            brand_name: Brand name
            retry_count: Number of retries
            
        Returns:
            List of matching products
        """
        products = []
        base_url = site_url.rstrip('/')
        
        # Try to search
        search_urls = [
            f"{base_url}/search?q={search_query.replace(' ', '+')}",
            f"{base_url}/search?query={search_query.replace(' ', '+')}",
            f"{base_url}/products?search={search_query.replace(' ', '+')}",
            f"{base_url}/shop?search={search_query.replace(' ', '+')}",
        ]
        
        for search_url in search_urls:
            try:
                logger.info(f"Searching '{search_query}' on {site_url}...")
                time.sleep(random.uniform(0.5, 1.5))
                
                response = self.session.get(search_url, headers=self.get_headers(), timeout=TIMEOUT)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_products = self._extract_products_from_page(soup, site_url, limit=5)
                    
                    # Filter by search query
                    for p in page_products:
                        if search_query.lower() in p.get('name', '').lower():
                            products.append(p)
                    
                    if products:
                        logger.info(f"Found {len(products)} products matching '{search_query}'")
                        return products
            
            except Exception as e:
                logger.debug(f"Error searching: {e}")
                continue
        
        logger.info(f"Found {len(products)} products matching '{search_query}'")
        return products


class ProductAggregator:
    """Aggregate product prices across regions"""
    
    def aggregate_product_prices(self, sites_by_region: Dict, product_name: str) -> Dict:
        """
        Aggregate prices for a product across all regions
        
        Args:
            sites_by_region: Dict of {region: [sites]}
            product_name: Product to search for
            
        Returns:
            Aggregated price data by region
        """
        aggregated = {}
        finder = ProductFinder()
        
        logger.info(f"Aggregating prices for '{product_name}' across {len(sites_by_region)} regions...")
        
        for region, sites in sites_by_region.items():
            region_prices = []
            
            for site_info in sites:
                site_url = site_info['url'] if isinstance(site_info, dict) else site_info
                
                try:
                    products = finder.search_products(site_url, product_name, region)
                    
                    for product in products:
                        if product['price'] > 0:
                            region_prices.append({
                                'site': site_url,
                                'price': product['price'],
                                'currency': product.get('currency', 'USD'),
                                'name': product.get('name', product_name)
                            })
                
                except Exception as e:
                    logger.debug(f"Error fetching from {site_url}: {e}")
                    continue
            
            if region_prices:
                aggregated[region] = region_prices
        
        return aggregated
    
    def get_featured_products(self, sites_by_region: Dict, limit: int = 5) -> Dict:
        """
        Get featured products from all sites across regions
        
        Args:
            sites_by_region: Dict of {region: [sites]}
            limit: Products per site
            
        Returns:
            Featured products by region
        """
        featured = {}
        finder = ProductFinder()
        
        for region, sites in sites_by_region.items():
            all_products = []
            
            for site_info in sites:
                site_url = site_info['url'] if isinstance(site_info, dict) else site_info
                
                try:
                    products = finder.get_top_products(site_url, region, limit)
                    all_products.extend(products)
                
                except Exception as e:
                    logger.debug(f"Error fetching products from {site_url}: {e}")
                    continue
            
            if all_products:
                featured[region] = all_products[:limit]
        
        return featured
