"""
Regional Data Processor - Organizes products by name with regional prices
"""

import pandas as pd
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegionalDataProcessor:
    """Process and format regional product data for display"""
    
    def __init__(self):
        self.currencies = {
            'USD': '$',
            'GBP': '£',
            'EUR': '€',
            'CAD': 'C$',
            'AED': 'د.إ',
            'AUD': 'A$',
            'CNY': '¥',
            'JPY': '¥',
            'INR': '₹',
            'MXN': '$',
            'BRL': 'R$'
        }
    
    def process_regional_products(self, products: List[Dict], brand_name: str) -> pd.DataFrame:
        """
        Process products into a DataFrame organized by product name
        with prices across regions
        
        Args:
            products: List of product dicts from regional scraper
            brand_name: Brand name
            
        Returns:
            DataFrame with products and regional prices
        """
        if not products:
            return pd.DataFrame()
        
        # Create a list to store processed data
        processed_data = []
        
        for product in products:
            name = product.get('name', 'Unknown')
            prices = product.get('prices', {})
            links = product.get('links', {})
            
            # Create a row with product name and prices per region
            row = {'Product Name': name, 'Brand': brand_name}
            
            # Add prices for each region
            for region, price_info in prices.items():
                price = price_info.get('price', 0)
                currency_code = price_info.get('currency_code', '')
                row[f'{region} Price'] = price
                row[f'{region} Display'] = f"{currency_code}{price:,.2f}"
                row[f'{region} Link'] = links.get(region, '')
            
            processed_data.append(row)
        
        df = pd.DataFrame(processed_data)
        
        # Sort by product name
        if not df.empty:
            df = df.sort_values('Product Name').reset_index(drop=True)
        
        return df
    
    def get_price_comparison(self, df: pd.DataFrame) -> Dict:
        """
        Get price comparison statistics across regions
        
        Args:
            df: DataFrame with regional prices
            
        Returns:
            Dictionary with comparison statistics
        """
        if df.empty:
            return {}
        
        # Extract price columns (those ending with ' Price')
        price_cols = [col for col in df.columns if col.endswith(' Price')]
        
        if not price_cols:
            return {}
        
        comparison = {}
        
        for product_name in df['Product Name']:
            product_row = df[df['Product Name'] == product_name].iloc[0]
            prices = {col.replace(' Price', ''): product_row[col] 
                     for col in price_cols if pd.notna(product_row[col])}
            
            if prices:
                min_price = min(prices.values())
                max_price = max(prices.values())
                cheapest_region = min(prices, key=prices.get)
                most_expensive_region = max(prices, key=prices.get)
                price_difference = max_price - min_price
                
                comparison[product_name] = {
                    'cheapest': {'region': cheapest_region, 'price': min_price},
                    'most_expensive': {'region': most_expensive_region, 'price': max_price},
                    'difference': price_difference,
                    'all_prices': prices
                }
        
        return comparison
    
    def format_for_display(self, df: pd.DataFrame, regions: List[str]) -> pd.DataFrame:
        """
        Format DataFrame for display in Streamlit
        
        Args:
            df: Raw DataFrame with prices
            regions: List of regions being displayed
            
        Returns:
            Formatted DataFrame for display
        """
        if df.empty:
            return df
        
        display_df = df[['Product Name', 'Brand']].copy()
        
        # Add formatted price columns for selected regions
        for region in regions:
            display_col = f'{region} Price'
            if display_col in df.columns:
                display_df[region] = df[display_col]
        
        return display_df
    
    def export_to_csv(self, df: pd.DataFrame, filename: str = 'regional_prices.csv'):
        """
        Export DataFrame to CSV
        
        Args:
            df: DataFrame to export
            filename: Output filename
            
        Returns:
            CSV bytes for download
        """
        return df.to_csv(index=False).encode('utf-8')
    
    def get_summary_statistics(self, df: pd.DataFrame, brand_name: str) -> Dict:
        """
        Get summary statistics for the data
        
        Args:
            df: DataFrame with prices
            brand_name: Brand name
            
        Returns:
            Dictionary with statistics
        """
        price_cols = [col for col in df.columns if col.endswith(' Price')]
        
        if not price_cols:
            return {'products_found': 0, 'regions_found': 0, 'avg_price': 0}
        
        # Flatten all prices
        all_prices = []
        for col in price_cols:
            prices = df[col].dropna().values
            all_prices.extend(prices)
        
        return {
            'products_found': len(df),
            'regions_found': len(price_cols),
            'avg_price': sum(all_prices) / len(all_prices) if all_prices else 0,
            'min_price': min(all_prices) if all_prices else 0,
            'max_price': max(all_prices) if all_prices else 0,
            'brand': brand_name
        }


class PriceComparisonAnalyzer:
    """Analyze price differences across regions"""
    
    @staticmethod
    def calculate_best_deal(product: Dict) -> Optional[str]:
        """
        Find the best deal for a product
        
        Args:
            product: Product dictionary with prices across regions
            
        Returns:
            Region with best (lowest) price or None
        """
        prices = product.get('prices', {})
        if not prices:
            return None
        
        min_region = min(prices.items(), key=lambda x: x[1]['price'])[0]
        return min_region
    
    @staticmethod
    def calculate_price_markup(product: Dict) -> Dict[str, float]:
        """
        Calculate price markup percentage across regions
        
        Args:
            product: Product dictionary with prices
            
        Returns:
            Dictionary with region: markup_percentage
        """
        prices = product.get('prices', {})
        if not prices or len(prices) < 2:
            return {}
        
        min_price = min(p['price'] for p in prices.values())
        markups = {}
        
        for region, price_info in prices.items():
            price = price_info['price']
            markup = ((price - min_price) / min_price) * 100
            markups[region] = markup
        
        return markups
