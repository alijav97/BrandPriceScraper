"""
Product Finder - Finds products on discovered brand sites
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import random
from config.settings import USER_AGENTS, TIMEOUT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductFinder:
    """Find products on brand websites"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_headers(self) -> Dict:
        """Get random user agent headers"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def get_top_products(self, site_url: str, brand_name: str, limit: int = 10) -> List[Dict]:
        """
        Get top products from a site (homepage/featured products)
        
        Args:
            site_url: Website URL
            brand_name: Brand name
            limit: Number of products to fetch
            
        Returns:
            List of product dictionaries
        """
        products = []
        
        try:
            logger.info(f"Fetching top products from {site_url}...")
            
            headers = self.get_headers()
            response = self.session.get(site_url, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try common product container selectors
            selectors = [
                'div[class*="product"]',
                'article[class*="product"]',
                'li[class*="product"]',
                'div[data-product]',
                '[class*="item-card"]',
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if len(elements) >= 5:  # Found products
                    for element in elements[:limit]:
                        product = self._extract_product_from_element(element, site_url)
                        if product:
                            products.append(product)
                    break
            
            logger.info(f"Found {len(products)} products on {site_url}")
            
        except Exception as e:
            logger.error(f"Error fetching products from {site_url}: {e}")
        
        return products
    
    def search_products(self, site_url: str, search_query: str, brand_name: str) -> List[Dict]:
        """
        Search for products on a site
        
        Args:
            site_url: Website URL
            search_query: Product name/query to search
            brand_name: Brand name
            
        Returns:
            List of matching products
        """
        products = []
        
        try:
            logger.info(f"Searching '{search_query}' on {site_url}...")
            
            # Try to construct search URL (varies by site)
            search_urls = [
                f"{site_url}?q={search_query.replace(' ', '+')}",
                f"{site_url}?search={search_query.replace(' ', '+')}",
                f"{site_url}/search?query={search_query.replace(' ', '+')}",
                f"{site_url}/search/{search_query.replace(' ', '%20')}",
            ]
            
            headers = self.get_headers()
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, headers=headers, timeout=TIMEOUT)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract products
                        selectors = [
                            'div[class*="product"]',
                            'article[class*="product"]',
                            'li[class*="product"]',
                        ]
                        
                        for selector in selectors:
                            elements = soup.select(selector)
                            if elements:
                                for element in elements[:5]:  # Limit to 5 per URL
                                    product = self._extract_product_from_element(element, site_url)
                                    if product and search_query.lower() in product.get('name', '').lower():
                                        products.append(product)
                                break
                        
                        if products:
                            break
                
                except:
                    continue
            
            logger.info(f"Found {len(products)} products matching '{search_query}'")
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
        
        return products
    
    def _extract_product_from_element(self, element, base_url: str) -> Optional[Dict]:
        """
        Extract product info from HTML element
        
        Args:
            element: BeautifulSoup element
            base_url: Base URL for relative links
            
        Returns:
            Product dictionary or None
        """
        try:
            # Extract product name
            name = None
            name_selectors = [
                'h1', 'h2', 'h3', 'span[class*="name"]',
                'a[class*="title"]', '[class*="product-name"]'
            ]
            
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    if name and len(name) > 3:
                        break
            
            if not name:
                return None
            
            # Extract price
            price = None
            price_selectors = [
                '[class*="price"]', 'span[class*="price"]',
                'div[class*="price"]', '[data-price]',
                '[class*="amount"]'
            ]
            
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    # Extract numbers
                    match = re.search(r'[\d,]+\.?\d*', price_text)
                    if match:
                        try:
                            price = float(match.group().replace(',', ''))
                            break
                        except:
                            continue
            
            if price is None:
                price = 0  # Still include if no price found
            
            # Extract link
            link = None
            link_elem = element.find('a', href=True)
            if link_elem:
                link = link_elem.get('href', '')
                if not link.startswith('http'):
                    link = base_url.rstrip('/') + ('' if link.startswith('/') else '/') + link
            
            # Extract image
            image = None
            img_elem = element.find('img')
            if img_elem:
                image = img_elem.get('src', '')
            
            return {
                'name': name,
                'price': price,
                'link': link,
                'image': image,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.debug(f"Error extracting product: {e}")
            return None


class ProductAggregator:
    """Aggregate products from multiple sites"""
    
    def __init__(self):
        self.finder = ProductFinder()
    
    def aggregate_product_prices(self, product_name: str, sites: Dict[str, List[Dict]], 
                                regions: Dict[str, Dict]) -> Dict:
        """
        Find a product across multiple sites and regions
        
        Args:
            product_name: Product name to search for
            sites: Dictionary of region: list of site URLs
            regions: Dictionary of region information
            
        Returns:
            Aggregated product data with prices across regions
        """
        logger.info(f"Aggregating prices for '{product_name}' across {len(sites)} regions...")
        
        product_data = {
            'name': product_name,
            'prices': {},
            'links': {},
            'images': {}
        }
        
        for region, region_sites in sites.items():
            best_match = None
            best_price = float('inf')
            
            for site_info in region_sites:
                try:
                    # Search for product on this site
                    products = self.finder.search_products(
                        site_info['url'],
                        product_name,
                        brand_name=''
                    )
                    
                    if products:
                        # Get best match (lowest price or first match)
                        product = min(products, key=lambda x: x.get('price', float('inf')))
                        
                        if product['price'] < best_price:
                            best_match = product
                            best_price = product['price']
                
                except Exception as e:
                    logger.debug(f"Error searching on {site_info.get('url')}: {e}")
                    continue
            
            if best_match:
                region_info = regions.get(region, {})
                currency_code = region_info.get('code', '$')
                currency = region_info.get('currency', 'USD')
                
                product_data['prices'][region] = {
                    'price': best_match['price'],
                    'currency': currency,
                    'currency_code': currency_code,
                    'site': best_match.get('link', '')
                }
                product_data['links'][region] = best_match.get('link', '')
                product_data['images'][region] = best_match.get('image', '')
        
        return product_data
    
    def get_featured_products(self, brand_sites: Dict[str, List[Dict]], 
                            regions: Dict[str, Dict], limit: int = 10) -> List[Dict]:
        """
        Get featured products from brand sites
        
        Args:
            brand_sites: Dictionary of region: list of site info
            regions: Region information
            limit: Number of products to fetch
            
        Returns:
            List of featured products
        """
        products = []
        
        for region, sites in brand_sites.items():
            if not sites:
                continue
            
            # Use the official site (usually first) to get featured products
            official_site = None
            for site in sites:
                if site.get('type') == 'official':
                    official_site = site
                    break
            
            if not official_site and sites:
                official_site = sites[0]
            
            if official_site:
                try:
                    region_products = self.finder.get_top_products(
                        official_site['url'],
                        brand_name='',
                        limit=limit
                    )
                    
                    for product in region_products:
                        region_info = regions.get(region, {})
                        product['region'] = region
                        product['currency_code'] = region_info.get('code', '$')
                        product['currency'] = region_info.get('currency', 'USD')
                        products.append(product)
                
                except Exception as e:
                    logger.error(f"Error getting featured products from {official_site}: {e}")
        
        # Remove duplicates based on name
        seen = set()
        unique_products = []
        for product in products:
            name = product.get('name', '').lower()
            if name not in seen:
                seen.add(name)
                unique_products.append(product)
        
        return unique_products[:limit]
