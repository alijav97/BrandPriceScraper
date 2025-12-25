"""
Data processing and formatting utilities
"""

import pandas as pd
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and format scraped data"""
    
    def __init__(self):
        self.currency_symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'CNY': '¥',
            'ARS': '$',
            'JPY': '¥',
            'INR': '₹',
        }
    
    def process_products(self, products: List[Dict]) -> pd.DataFrame:
        """
        Convert raw product list to DataFrame with formatting
        """
        if not products:
            return pd.DataFrame()
        
        df = pd.DataFrame(products)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['title', 'site'], keep='first')
        
        # Sort by price
        df = df.sort_values('current_price', ascending=True, na_position='last')
        
        return df
    
    def format_for_display(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Format DataFrame for display in Streamlit
        """
        if df.empty:
            return df
        
        display_df = df.copy()
        
        # Format prices with currency
        display_df['Price (Current)'] = display_df.apply(
            lambda row: self._format_price(row['current_price'], row['currency']), 
            axis=1
        )
        
        display_df['Price (Original)'] = display_df.apply(
            lambda row: self._format_price(row['original_price'], row['currency']), 
            axis=1
        )
        
        # Calculate discount if available
        display_df['Discount %'] = display_df.apply(
            lambda row: self._calculate_discount(row['original_price'], row['current_price']),
            axis=1
        )
        
        # Select and rename columns for display
        display_columns = {
            'title': 'Product',
            'site': 'Site',
            'region': 'Region',
            'Price (Current)': 'Current Price',
            'Price (Original)': 'Original Price',
            'Discount %': 'Discount',
            'currency': 'Currency Code',
        }
        
        return display_df[[col for col in display_columns.keys() if col in display_df.columns]].rename(
            columns=display_columns
        )
    
    @staticmethod
    def _format_price(price: float, currency: str) -> str:
        """
        Format price with currency
        """
        if not price or pd.isna(price):
            return 'N/A'
        
        symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'CNY': '¥',
            'ARS': '$', 'JPY': '¥', 'INR': '₹',
        }
        
        symbol = symbols.get(currency, currency)
        return f"{symbol}{price:.2f} {currency}"
    
    @staticmethod
    def _calculate_discount(original: float, current: float) -> str:
        """
        Calculate discount percentage
        """
        if not original or not current or pd.isna(original) or pd.isna(current):
            return 'N/A'
        
        if original == 0:
            return 'N/A'
        
        discount = ((original - current) / original) * 100
        
        if discount > 0:
            return f"{discount:.1f}% OFF"
        elif discount < 0:
            return f"{abs(discount):.1f}% UP"
        else:
            return "No Change"
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for the data
        """
        if df.empty:
            return {}
        
        stats = {
            'Total Products': len(df),
            'Sites Searched': df['site'].nunique(),
            'Regions Covered': df['region'].nunique(),
            'Avg Price': df['current_price'].mean(),
            'Min Price': df['current_price'].min(),
            'Max Price': df['current_price'].max(),
        }
        
        return stats
    
    def export_to_csv(self, df: pd.DataFrame, filename: str) -> str:
        """
        Export data to CSV
        """
        try:
            df.to_csv(filename, index=False)
            logger.info(f"Data exported to {filename}")
            return f"✓ Data exported to {filename}"
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return f"✗ Error exporting data: {e}"
