"""
Smart Brand Price Tracker - Dynamic Search Edition
Searches for brand sites across regions and compares prices automatically
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Import modules
from src.search_engine import SmartSiteSelector, BrandSearchEngine
from src.product_finder import ProductFinder, ProductAggregator
from utils.openai_analyzer import PriceAnalyzer

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
Enter any brand name. We'll search the web to find official stores and retailers 
across all regions, then compare product prices globally for you.
""")

# ============================================================================
# SIDEBAR - BRAND SEARCH
# ============================================================================

st.sidebar.header("🔍 Search Brand")

brand_input = st.sidebar.text_input(
    "Enter brand name",
    placeholder="e.g., Lululemon, Nike, Adidas...",
    help="Type any brand you want to track"
)

search_button = st.sidebar.button("🔍 Search Across Web", use_container_width=True)

# Initialize session state
if 'brand_sites' not in st.session_state:
    st.session_state.brand_sites = None
if 'selected_brand' not in st.session_state:
    st.session_state.selected_brand = None
if 'search_engine' not in st.session_state:
    st.session_state.search_engine = SmartSiteSelector()
if 'featured_products' not in st.session_state:
    st.session_state.featured_products = None

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
                st.session_state.selected_brand = brand_input
                
                # Count sites found
                total_sites = sum(len(sites) for sites in brand_sites.values())
                total_regions = len(brand_sites)
                
                st.success(f"✅ Found {total_sites} sites in {total_regions} regions!")
                
                # Fetch featured products
                aggregator = ProductAggregator()
                featured = aggregator.get_featured_products(
                    brand_sites,
                    selector.search_engine.regions,
                    limit=15
                )
                
                if featured:
                    st.session_state.featured_products = featured
                    st.info(f"📦 Found {len(featured)} featured products")
                else:
                    st.warning("⚠️ Could not fetch products from these sites. Sites may have protections.")
            
            else:
                st.warning(f"⚠️ No sites found for '{brand_input}'. Try a different brand name.")
        
        except Exception as e:
            st.error(f"❌ Error searching: {str(e)}")
            st.info("Tip: Try a more specific brand name or try another brand")

# ============================================================================
# RESULTS
# ============================================================================

if st.session_state.brand_sites:
    selector = st.session_state.search_engine
    
    # Show regions found
    st.divider()
    st.subheader(f"🌍 Regions Found for {st.session_state.selected_brand}")
    
    col_regions = st.columns(len(st.session_state.brand_sites))
    
    for idx, (region, sites) in enumerate(st.session_state.brand_sites.items()):
        with col_regions[idx]:
            region_info = selector.search_engine.get_region_info(region)
            region_name = region_info.get('name', region) if region_info else region
            currency = region_info.get('code', '') if region_info else ''
            
            with st.container():
                st.metric(
                    region_name,
                    f"{len(sites)} site{'s' if len(sites) != 1 else ''}"
                )
                
                with st.expander(f"View sites in {region}"):
                    for site in sites:
                        badge = "🏢" if site.get('type') == 'official' else "🛒"
                        st.write(f"{badge} [{site['domain']}]({site['url']})")
    
    st.divider()
    
    # ========== FEATURED PRODUCTS ==========
    
    if st.session_state.featured_products:
        st.subheader("📦 Featured Products")
        
        # Product selection
        featured = st.session_state.featured_products
        product_names = [p['name'] for p in featured]
        
        selected_product_idx = st.selectbox(
            "Select a product to see prices across regions:",
            range(len(featured)),
            format_func=lambda x: featured[x]['name'][:50]
        )
        
        if selected_product_idx is not None:
            selected_product = featured[selected_product_idx]
            
            st.divider()
            st.subheader(f"💰 Price Comparison: {selected_product['name']}")
            
            # Aggregate prices across regions
            aggregator = ProductAggregator()
            product_data = aggregator.aggregate_product_prices(
                selected_product['name'],
                st.session_state.brand_sites,
                selector.search_engine.regions
            )
            
            if product_data['prices']:
                # Create comparison table
                comparison_data = []
                
                for region, price_info in product_data['prices'].items():
                    region_info = selector.search_engine.get_region_info(region)
                    region_name = region_info.get('name', region) if region_info else region
                    
                    comparison_data.append({
                        '🌍 Region': region_name,
                        '💵 Price': f"{price_info['currency_code']}{price_info['price']:.2f}",
                        '💱 Currency': price_info['currency'],
                        '🔗 Link': price_info['site'][:50] + '...' if len(price_info['site']) > 50 else price_info['site']
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                
                # Find best deal
                best_region = min(
                    product_data['prices'].items(),
                    key=lambda x: x[1]['price']
                )
                
                st.success(f"✅ Best price: {best_region[1]['currency_code']}{best_region[1]['price']:.2f} in {best_region[0]}")
                
                # Export option
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = comparison_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Comparison",
                        data=csv,
                        file_name=f"{selected_product['name']}_prices.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    if st.button("🔄 Search Another Product"):
                        st.rerun()
            
            else:
                st.warning("⚠️ Could not find this product across regions")
    
    else:
        st.info("📦 Featured products are loading or not available. Try searching for a specific product below.")
    
    # ========== CUSTOM PRODUCT SEARCH ==========
    
    st.divider()
    st.subheader("🔎 Search for Specific Product")
    
    custom_search = st.text_input(
        "What product are you looking for?",
        placeholder="e.g., running shoes, jacket, etc...",
        help="We'll search all discovered sites for this product"
    )
    
    if st.button("Search Product", use_container_width=True):
        if custom_search:
            with st.spinner(f"🔎 Searching for '{custom_search}' across all sites..."):
                try:
                    aggregator = ProductAggregator()
                    product_data = aggregator.aggregate_product_prices(
                        custom_search,
                        st.session_state.brand_sites,
                        selector.search_engine.regions
                    )
                    
                    if product_data['prices']:
                        st.success(f"✅ Found '{custom_search}' in {len(product_data['prices'])} regions!")
                        
                        # Show results
                        results = []
                        for region, price_info in product_data['prices'].items():
                            region_info = selector.search_engine.get_region_info(region)
                            region_name = region_info.get('name', region) if region_info else region
                            
                            results.append({
                                '🌍 Region': region_name,
                                '💵 Price': f"{price_info['currency_code']}{price_info['price']:.2f}",
                                '💱 Currency': price_info['currency'],
                            })
                        
                        results_df = pd.DataFrame(results)
                        st.dataframe(results_df, use_container_width=True, hide_index=True)
                        
                        # Download
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results",
                            data=csv,
                            file_name=f"{custom_search}_prices.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning(f"⚠️ Product '{custom_search}' not found on these sites")
                
                except Exception as e:
                    st.error(f"Error searching: {str(e)}")
        
        else:
            st.warning("Please enter a product name")

else:
    # Initial state
    st.info("👈 Enter a brand name and click 'Search Across Web' to get started!")
    
    st.markdown("""
    ### How it works:
    1. **Enter a brand** (Nike, Lululemon, Adidas, etc.)
    2. **We search** for official sites and retailers across regions
    3. **Pick a product** from featured items
    4. **See prices** in all regions and currencies
    5. **Find best deals** instantly
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.85em;'>
    <p>🛍️ Smart Brand Price Tracker | Dynamic Web Search Edition</p>
    <p>Powered by Web Search + Web Scraping + AI</p>
</div>
""", unsafe_allow_html=True)
