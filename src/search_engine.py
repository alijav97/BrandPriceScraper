"""
Dynamic Brand Search Engine - Finds official brand sites and retailers by region
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Tuple
import logging
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrandSearchEngine:
    """Search for brand official sites and retailers across regions"""
    
    def __init__(self):
        self.session = requests.Session()
        self.regions = {
            'US': {'name': 'United States', 'currency': 'USD', 'code': '$', 'domains': ['com', 'us']},
            'UK': {'name': 'United Kingdom', 'currency': 'GBP', 'code': '£', 'domains': ['co.uk', 'uk']},
            'Canada': {'name': 'Canada', 'currency': 'CAD', 'code': 'C$', 'domains': ['ca']},
            'UAE': {'name': 'United Arab Emirates', 'currency': 'AED', 'code': 'د.إ', 'domains': ['ae']},
            'Germany': {'name': 'Germany', 'currency': 'EUR', 'code': '€', 'domains': ['de']},
            'Australia': {'name': 'Australia', 'currency': 'AUD', 'code': 'A$', 'domains': ['au']},
            'France': {'name': 'France', 'currency': 'EUR', 'code': '€', 'domains': ['fr']},
            'Japan': {'name': 'Japan', 'currency': 'JPY', 'code': '¥', 'domains': ['jp']},
        }
        
        # Common official domain patterns for brands
        self.official_indicators = [
            'official', 'brand', 'store', 'shop', 'direct',
            '.com', '.co.uk', '.de', '.fr', '.ae', '.jp'
        ]
        
        # Known retailers (second priority)
        self.known_retailers = [
            'amazon', 'ebay', 'ssense', 'net-a-porter', 'farfetch',
            'asos', 'lookfantastic', 'selfridges', 'harrods',
            'sportsdirect', 'jd', 'foot locker', 'finish line',
            'dicks sporting goods', 'finish line', 'kohl',
            'nordstrom', 'saks', 'bloomingdale', 'macy'
        ]
    
    def search_brand_globally(self, brand_name: str) -> Dict[str, List[Dict]]:
        """
        Search for a brand across all regions
        
        Args:
            brand_name: Brand name to search
            
        Returns:
            Dictionary with region: list of sites (official first, then retailers)
        """
        logger.info(f"Searching for {brand_name} across regions...")
        
        brand_sites = {}
        
        for region_code, region_info in self.regions.items():
            logger.info(f"  Searching {region_info['name']}...")
            sites = self._search_region(brand_name, region_code, region_info)
            if sites:
                brand_sites[region_code] = sites
        
        return brand_sites
    
    def _search_region(self, brand_name: str, region_code: str, region_info: Dict) -> List[Dict]:
        """
        Search for brand sites in a specific region
        
        Args:
            brand_name: Brand name
            region_code: Region code
            region_info: Region information
            
        Returns:
            List of sites found (official first)
        """
        sites = []
        
        try:
            # Method 1: Try direct domain patterns first (most reliable)
            direct_urls = self._try_direct_domains(brand_name, region_info)
            
            # Method 2: If direct fails, try Google search
            if not direct_urls:
                search_queries = [
                    f"{brand_name} official store {region_info['name']}",
                    f"{brand_name} official website {region_info['name']}",
                ]
                
                found_urls = set()
                for query in search_queries:
                    urls = self._google_search(query)
                    found_urls.update(urls)
                    if found_urls:
                        break
                
                direct_urls = list(found_urls)
            
            # Categorize URLs
            official_sites = []
            retailer_sites = []
            
            for url in direct_urls:
                if not url or len(url) < 5:
                    continue
                
                site_info = {
                    'url': url,
                    'domain': self._extract_domain(url),
                    'type': self._classify_site(url, brand_name),
                    'region': region_code
                }
                
                if site_info['type'] == 'official':
                    official_sites.append(site_info)
                elif site_info['type'] == 'retailer':
                    retailer_sites.append(site_info)
            
            # Combine: official first, then retailers
            sites = official_sites + retailer_sites[:3]  # Limit retailers to top 3
            
            logger.info(f"    Found {len(sites)} sites in {region_info['name']}")
            
        except Exception as e:
            logger.error(f"Error searching {region_info['name']}: {e}")
        
        return sites
    
    def _try_direct_domains(self, brand_name: str, region_info: Dict) -> List[str]:
        """
        Try to find brand by constructing common domain patterns
        
        Args:
            brand_name: Brand name
            region_info: Region information
            
        Returns:
            List of accessible URLs
        """
        urls = []
        brand_lower = brand_name.lower().replace(' ', '')
        
        # Try common domain patterns
        domain_patterns = [
            f"https://www.{brand_lower}.com",
            f"https://{brand_lower}.com",
            f"https://www.{brand_lower}.{region_info['domains'][0]}",
            f"https://{brand_lower}.{region_info['domains'][0]}",
        ]
        
        # Add regional variations
        if len(region_info['domains']) > 1:
            for domain in region_info['domains']:
                domain_patterns.append(f"https://www.{brand_lower}.{domain}")
                domain_patterns.append(f"https://{brand_lower}.{domain}")
        
        # Test each pattern
        for url in domain_patterns:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = self.session.head(url, headers=headers, timeout=5)
                if response.status_code < 400:
                    urls.append(url)
                    logger.debug(f"Found accessible site: {url}")
            except:
                pass
        
        return urls
    
    def _google_search(self, query: str) -> List[str]:
        """
        Search Google and extract URLs (fallback method)
        
        Args:
            query: Search query
            
        Returns:
            List of URLs found
        """
        urls = []
        
        try:
            # Use a more realistic user agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
            }
            
            # Search URL
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            response = self.session.get(search_url, headers=headers, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                logger.debug(f"Google search returned status {response.status_code}")
                return urls
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple parsing methods
            # Method 1: Look for cite tags (older format)
            for cite in soup.find_all('cite'):
                url_text = cite.get_text()
                if url_text.startswith('http'):
                    urls.append(url_text)
            
            # Method 2: Look for href in search results
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/url?q='):
                    try:
                        url = href.split('/url?q=')[1].split('&')[0]
                        if url.startswith('http'):
                            urls.append(url)
                    except:
                        pass
            
            # Method 3: Look for data attributes
            for element in soup.find_all(attrs={'data-url': True}):
                url = element.get('data-url')
                if url and url.startswith('http'):
                    urls.append(url)
            
            # Remove duplicates
            urls = list(set(urls))
            
            # Limit results
            urls = urls[:10]
            
            logger.debug(f"Found {len(urls)} URLs from Google search for '{query}'")
            
        except Exception as e:
            logger.debug(f"Google search failed: {e}")
        
        return urls
    
    def _classify_site(self, url: str, brand_name: str) -> str:
        """
        Classify if site is official or retailer
        
        Args:
            url: Website URL
            brand_name: Brand name
            
        Returns:
            'official', 'retailer', or 'unknown'
        """
        domain = self._extract_domain(url)
        url_lower = url.lower()
        brand_lower = brand_name.lower()
        
        # Check if it's official (has brand name in domain)
        if brand_lower in domain:
            return 'official'
        
        # Check if it's a known retailer
        for retailer in self.known_retailers:
            if retailer in domain:
                return 'retailer'
        
        return 'unknown'
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain
        except:
            return url
    
    def verify_site_accessibility(self, url: str) -> bool:
        """
        Check if a site is accessible
        
        Args:
            url: Website URL
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = self.session.head(url, headers=headers, timeout=5)
            return response.status_code < 400
        except:
            return False
    
    def get_region_info(self, region_code: str) -> Optional[Dict]:
        """Get region information"""
        return self.regions.get(region_code)


class SmartSiteSelector:
    """Select best sites for scraping based on reliability and product availability"""
    
    def __init__(self):
        self.search_engine = BrandSearchEngine()
        self.site_scores = {}
    
    def select_best_sites(self, brand_name: str, max_sites: int = 5) -> Dict[str, List[Dict]]:
        """
        Select the best sites to scrape for a brand
        
        Args:
            brand_name: Brand name
            max_sites: Maximum sites per region
            
        Returns:
            Dictionary with region: list of sites (ranked by quality)
        """
        logger.info(f"Selecting best sites for {brand_name}...")
        
        # Search for sites
        all_sites = self.search_engine.search_brand_globally(brand_name)
        
        selected_sites = {}
        
        for region, sites in all_sites.items():
            # Verify accessibility and rank
            verified_sites = []
            
            for site in sites:
                if self.search_engine.verify_site_accessibility(site['url']):
                    # Score the site (official = higher score)
                    score = 10 if site['type'] == 'official' else 5
                    site['score'] = score
                    verified_sites.append(site)
            
            # Sort by score and limit
            verified_sites.sort(key=lambda x: x['score'], reverse=True)
            selected_sites[region] = verified_sites[:max_sites]
        
        return selected_sites
