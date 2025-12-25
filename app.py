"""
Smart Brand Price Tracker - Dynamic Search Edition
Searches for brand sites across regions and compares prices automatically
"""

import os
import sys
import importlib.util

# Fix import paths FIRST before any other imports
if os.path.exists(os.path.join(os.path.dirname(__file__), 'src')):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Try standard import first, fall back to direct loading
try:
    from src.search_engine import SmartSiteSelector, BrandSearchEngine
    from src.product_finder import ProductFinder, ProductAggregator
    from utils.openai_analyzer import PriceAnalyzer
except ImportError:
    # Fallback: Direct file loading for Streamlit Cloud
    spec = importlib.util.spec_from_file_location("search_engine", os.path.join(os.path.dirname(__file__), 'src', 'search_engine.py'))
    search_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(search_module)
    SmartSiteSelector = search_module.SmartSiteSelector
    BrandSearchEngine = search_module.BrandSearchEngine
    
    spec = importlib.util.spec_from_file_location("product_finder", os.path.join(os.path.dirname(__file__), 'src', 'product_finder.py'))
    product_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(product_module)
    ProductFinder = product_module.ProductFinder
    ProductAggregator = product_module.ProductAggregator
    
    spec = importlib.util.spec_from_file_location("openai_analyzer", os.path.join(os.path.dirname(__file__), 'utils', 'openai_analyzer.py'))
    analyzer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analyzer_module)
    PriceAnalyzer = analyzer_module.PriceAnalyzer

# Load environment
load_dotenv()

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Smart Brand Price Tracker",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# TITLE
# ============================================================================

st.title("🛍️ Smart Brand Price Tracker")
st.markdown("""
**How it works:**
1. Enter a brand name → We find all their regional websites
2. Enter a specific product → We search for it across all regions  
3. See price comparison → Compare prices globally!
""")

# ============================================================================
# SESSION STATE
# ============================================================================

if 'brand_sites' not in st.session_state:
    st.session_state.brand_sites = {}
if 'current_brand' not in st.session_state:
    st.session_state.current_brand = ""

# ============================================================================
# SIDEBAR - STEP 1: BRAND SEARCH
# ============================================================================

st.sidebar.header("📍 Step 1: Search Brand")

brand_input = st.sidebar.text_input(
    "Enter brand name",
    placeholder="e.g., Lululemon, Nike, Adidas...",
    help="Type any brand you want to track"
)

search_button = st.sidebar.button("🔍 Search Brand Sites", use_container_width=True)

# Initialize session state
if 'brand_sites' not in st.session_state:
    st.session_state.brand_sites = {}
if 'current_brand' not in st.session_state:
    st.session_state.current_brand = ""
if 'search_engine' not in st.session_state:
    st.session_state.search_engine = SmartSiteSelector()

# ============================================================================
# SEARCH LOGIC
# ============================================================================

if search_button and brand_input:
    with st.spinner(f"🔍 Searching web for '{brand_input}' official sites and retailers..."):
        try:
            selector = st.session_state.search_engine
            brand_sites = selector.select_best_sites(brand_input, max_sites=3)
            
            if brand_sites:
                st.session_state.brand_sites = brand_sites
                st.session_state.current_brand = brand_input
                
                # Count sites found
                total_sites = sum(len(sites) for sites in brand_sites.values())
                total_regions = len(brand_sites)
                st.success(f"✅ Found {total_sites} sites in {total_regions} regions!")
            else:
                st.warning(f"⚠️ No sites found for '{brand_input}'.")
                st.info("**Try:** \n- Make sure brand name is spelled correctly\n- Try a more well-known brand\n- Check your internet connection")
        
        except Exception as e:
            st.error(f"❌ Error searching: {str(e)}")
            st.info("Tip: Try a more specific brand name or check your internet connection")

# ============================================================================
# STEP 2: PRODUCT SEARCH (Only show if brand was found)
# ============================================================================

if st.session_state.brand_sites:
    st.divider()
    st.sidebar.header("📦 Step 2: Search Product")
    
    brand_name = st.session_state.current_brand
    
    product_input = st.sidebar.text_input(
        "Enter product name to search",
        placeholder="e.g., Align Leggings, Air Force 1...",
        help="Specific product name to find prices for"
    )
    
    search_product_button = st.sidebar.button("🔍 Search Product", use_container_width=True)
    
    # ========== DISPLAY BRAND RESULTS ==========
    
    st.subheader(f"🌍 Regional Sites Found for {brand_name}")
    
    col_regions = st.columns(min(4, len(st.session_state.brand_sites)))
    
    for idx, (region, sites) in enumerate(st.session_state.brand_sites.items()):
        col_idx = idx % len(col_regions)
        with col_regions[col_idx]:
            with st.container(border=True):
                st.write(f"**{region}**")
                st.caption(f"🔗 {len(sites)} site{'s' if len(sites) != 1 else ''}")
                
                for site in sites:
                    badge = "🏢" if site.get('type') == 'official' else "🛒"
                    st.caption(f"{badge} {site['domain']}")
    
    # ========== PRODUCT SEARCH RESULTS ==========
    
    if search_product_button and product_input:
        st.divider()
        st.subheader(f"💰 Price Comparison: {product_input}")
        
        with st.spinner(f"🔍 Searching for '{product_input}' across all regions..."):
            try:
                # Search for product across all regions
                aggregator = ProductAggregator()
                product_data = aggregator.aggregate_product_prices(
                    st.session_state.brand_sites,
                    product_input
                )
                
                if product_data and any(product_data.values()):
                    # Build comparison table
                    comparison_data = []
                    
                    for region, prices_list in product_data.items():
                        if prices_list:
                            for price_info in prices_list:
                                try:
                                    price_val = float(price_info['price'])
                                    comparison_data.append({
                                        '🌍 Region': region,
                                        '💰 Price': f"{price_info['currency']}{price_val:.2f}",
                                        '💵 Code': price_info.get('currency', 'USD'),
                                        '🛒 Store': price_info['site'][:50],
                                        '📝 Product': price_info['name'][:60]
                                    })
                                except:
                                    pass
                    
                    if comparison_data:
                        comparison_df = pd.DataFrame(comparison_data)
                        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                        
                        # Find best deal
                        try:
                            best_entry = min(
                                comparison_data,
                                key=lambda x: float(''.join(c for c in x['💰 Price'] if c.isdigit() or c == '.'))
                            )
                            
                            st.success(f"✅ Best price: {best_entry['💰 Price']} in {best_entry['🌍 Region']}")
                            
                            # Download button
                            csv = comparison_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Comparison CSV",
                                data=csv,
                                file_name=f"{product_input}_{brand_name}_prices.csv",
                                mime="text/csv"
                            )
                        except:
                            st.info("Could not calculate best price")
                    else:
                        st.warning(f"⚠️ No prices found for '{product_input}'. Try a different product name.")
                else:
                    st.warning(f"⚠️ No results found for '{product_input}' across {brand_name} sites.")
                    st.info("**Tips:**\n- Make sure you have the exact product name\n- Try searching with different keywords\n- Some sites may block scrapers")
                    
            except Exception as e:
                st.error(f"❌ Error searching product: {str(e)}")
                st.info("Try again or use a different product name")

# ============================================================================
# INITIAL STATE MESSAGE
# ============================================================================

if not st.session_state.brand_sites:
    st.info("👈 **Enter a brand name in the sidebar to get started!**")
    st.markdown("""
    ### How to use:
    1. **Search Brand** - Enter any brand (e.g., Lululemon, Nike, Adidas)
    2. **View Sites** - See all regional websites found
    3. **Search Product** - Enter a specific product (e.g., "Align Leggings")
    4. **Compare Prices** - See prices across all regions
    
    ### Supported Regions:
    🇺🇸 United States | 🇬🇧 UK | 🇨🇦 Canada | 🇦🇪 UAE | 🇩🇪 Germany | 🇦🇺 Australia | 🇫🇷 France | 🇯🇵 Japan
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.85em;'>
    <p>🛍️ Smart Brand Price Tracker v2.0 | Dynamic Web Search</p>
    <p>Search any brand, enter a product, compare prices globally!</p>
</div>
""", unsafe_allow_html=True)
