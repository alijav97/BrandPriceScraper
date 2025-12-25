"""
Regional Brand Price Tracker App
Tracks product prices across official brand regional websites
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Import regional scraper and processor
from src.regional_scraper import RegionalDataCollector
from utils.regional_processor import RegionalDataProcessor, PriceComparisonAnalyzer
from utils.openai_analyzer import PriceAnalyzer, PricePrediction

# Load environment variables
load_dotenv()

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Regional Brand Price Tracker",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {padding: 2rem;}
    .stTabs [data-baseweb="tab-list"] button {font-size: 1.1em;}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# TITLE & DESCRIPTION
# ============================================================================

st.title("🌍 Regional Brand Price Tracker")
st.markdown("""
Compare product prices from your favorite brands across different regions and countries.
See which region offers the best deals and make informed purchasing decisions.
""")

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.header("⚙️ Search Settings")

# Initialize data collector
@st.cache_resource
def get_data_collector():
    return RegionalDataCollector()

collector = get_data_collector()
available_brands = collector.get_brands_list()

# Brand selection
selected_brand = st.sidebar.selectbox(
    "🏷️ Select Brand",
    options=available_brands,
    help="Choose a brand to track"
)

# Region selection
if selected_brand:
    available_regions = collector.scraper.get_available_regions(selected_brand)
    default_regions = available_regions[:2] if len(available_regions) > 1 else available_regions
    
    selected_regions = st.sidebar.multiselect(
        "🗺️ Select Regions",
        options=available_regions,
        default=default_regions,
        help="Choose regions to compare prices"
    )
    
    if not selected_regions:
        st.sidebar.warning("Please select at least one region")
else:
    selected_regions = []

# Search button
search_button = st.sidebar.button(
    "🔍 Search Prices",
    use_container_width=True,
    key="search_button"
)

# AI Analysis toggle
enable_ai = st.sidebar.checkbox(
    "🤖 Enable AI Analysis",
    value=True,
    help="Get AI-powered insights about prices and trends"
)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Initialize session state
if 'products_data' not in st.session_state:
    st.session_state.products_data = None
if 'brand_searched' not in st.session_state:
    st.session_state.brand_searched = None
if 'regions_searched' not in st.session_state:
    st.session_state.regions_searched = None

# Handle search
if search_button and selected_brand and selected_regions:
    with st.spinner(f"🔍 Searching {selected_brand} prices in {', '.join(selected_regions)}..."):
        try:
            products_data = collector.collect_brand_data(selected_brand, selected_regions)
            
            if products_data:
                st.session_state.products_data = products_data
                st.session_state.brand_searched = selected_brand
                st.session_state.regions_searched = selected_regions
                st.success(f"✅ Found {len(products_data)} products!")
            else:
                st.warning("⚠️ No products found. The brand website might be protected or temporarily unavailable.")
        
        except Exception as e:
            st.error(f"❌ Error during search: {str(e)}")
            st.info("Tip: Some websites require special handling. Try another brand or region.")

# Display results
if st.session_state.products_data:
    processor = RegionalDataProcessor()
    
    # Process data
    df = processor.process_regional_products(
        st.session_state.products_data,
        st.session_state.brand_searched
    )
    
    # Display summary
    col1, col2, col3, col4 = st.columns(4)
    stats = processor.get_summary_statistics(df, st.session_state.brand_searched)
    
    with col1:
        st.metric("📦 Products Found", stats['products_found'])
    with col2:
        st.metric("🗺️ Regions", stats['regions_found'])
    with col3:
        st.metric("💰 Average Price", f"${stats['avg_price']:.2f}")
    with col4:
        st.metric("💾 Range", f"${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Price Comparison",
        "🏆 Best Deals",
        "📈 Price Analysis",
        "🤖 AI Insights",
        "⬇️ Export Data"
    ])
    
    # ========== TAB 1: Price Comparison ==========
    with tab1:
        st.subheader("Product Prices by Region")
        
        # Create comparison table
        display_cols = ['Product Name']
        for region in st.session_state.regions_searched:
            display_cols.append(f'{region} Display')
        
        if all(col in df.columns for col in display_cols):
            display_df = df[display_cols].copy()
            display_df.columns = ['Product'] + [col.replace(' Display', '') for col in display_cols[1:]]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Price data not available for selected regions")
    
    # ========== TAB 2: Best Deals ==========
    with tab2:
        st.subheader("🏆 Best Deals by Product")
        
        analyzer = PriceComparisonAnalyzer()
        comparison = processor.get_price_comparison(df)
        
        if comparison:
            for product_name, deal_info in comparison.items():
                with st.expander(f"📦 {product_name}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        best = deal_info['cheapest']
                        st.write(f"**✅ Best Deal:**")
                        st.write(f"{best['region']}: **${best['price']:.2f}**")
                    
                    with col2:
                        worst = deal_info['most_expensive']
                        st.write(f"**❌ Most Expensive:**")
                        st.write(f"{worst['region']}: **${worst['price']:.2f}**")
                    
                    with col3:
                        st.write(f"**💰 Savings Potential:**")
                        st.write(f"**${deal_info['difference']:.2f}**")
                    
                    # Markup percentages
                    markups = analyzer.calculate_price_markup({'prices': {
                        region: {'price': price}
                        for region, price in deal_info['all_prices'].items()
                    }})
                    
                    if markups:
                        st.write("**Price Markup by Region:**")
                        for region, markup in markups.items():
                            st.write(f"{region}: {markup:.1f}% markup")
        else:
            st.info("No price data available for comparison")
    
    # ========== TAB 3: Price Analysis ==========
    with tab3:
        st.subheader("📈 Detailed Price Analysis")
        
        # Extract numeric price columns
        price_cols = [col for col in df.columns if col.endswith(' Price')]
        
        if price_cols:
            # Summary statistics
            st.write("**Price Statistics by Region:**")
            
            stats_data = []
            for col in price_cols:
                region = col.replace(' Price', '')
                prices = df[col].dropna()
                
                if len(prices) > 0:
                    stats_data.append({
                        'Region': region,
                        'Avg Price': f"${prices.mean():.2f}",
                        'Min': f"${prices.min():.2f}",
                        'Max': f"${prices.max():.2f}",
                        'Count': len(prices)
                    })
            
            if stats_data:
                stats_df = pd.DataFrame(stats_data)
                st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
            # Price distribution chart
            st.write("**Price Distribution:**")
            price_chart_data = {}
            for col in price_cols:
                region = col.replace(' Price', '')
                prices = df[col].dropna()
                if len(prices) > 0:
                    price_chart_data[region] = prices.values
            
            if price_chart_data:
                # Create a simple bar chart
                chart_df = pd.DataFrame({
                    region: pd.Series(prices).mean()
                    for region, prices in price_chart_data.items()
                }, index=['Average Price'])
                
                st.bar_chart(chart_df.T)
        else:
            st.info("No price data available")
    
    # ========== TAB 4: AI Insights ==========
    with tab4:
        if enable_ai:
            st.subheader("🤖 AI-Powered Insights")
            
            openai_key = os.getenv("OPENAI_API_KEY")
            
            if openai_key:
                try:
                    analyzer = PriceAnalyzer()
                    
                    # Prepare data for AI
                    ai_df = df[[col for col in df.columns if not col.startswith(('Brand', 'Product'))]].copy()
                    
                    ai_col1, ai_col2 = st.columns(2)
                    
                    with ai_col1:
                        if st.button("📊 Get Market Insights"):
                            with st.spinner("Analyzing market data..."):
                                insights = analyzer._get_insights()
                                st.success(insights)
                    
                    with ai_col2:
                        if st.button("✅ Get Smart Recommendations"):
                            with st.spinner("Generating recommendations..."):
                                recommendations = analyzer._get_recommendations()
                                st.success(recommendations)
                
                except Exception as e:
                    st.warning(f"AI analysis unavailable: {str(e)}")
            else:
                st.info("🔑 Add your OpenAI API key to enable AI insights")
        else:
            st.info("AI Analysis is disabled. Enable it in Settings to see insights.")
    
    # ========== TAB 5: Export Data ==========
    with tab5:
        st.subheader("⬇️ Export Your Data")
        
        # CSV Export
        csv_data = processor.export_to_csv(df)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name=f"{st.session_state.brand_searched}_prices.csv",
            mime="text/csv"
        )
        
        # Summary Export
        st.write("**Price Summary:**")
        summary_text = f"""
        Brand: {st.session_state.brand_searched}
        Regions: {', '.join(st.session_state.regions_searched)}
        Products Found: {stats['products_found']}
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Average Price: ${stats['avg_price']:.2f}
        Price Range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}
        """
        
        st.download_button(
            label="📄 Download Summary",
            data=summary_text,
            file_name=f"{st.session_state.brand_searched}_summary.txt",
            mime="text/plain"
        )

else:
    # Initial state
    if not search_button:
        st.info("👈 Select a brand and regions in the sidebar, then click 'Search Prices' to get started!")
    else:
        st.warning("Please select a brand and at least one region to search.")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.85em;'>
    <p>🌍 Regional Brand Price Tracker | Powered by Streamlit & OpenAI</p>
    <p>Made with ❤️ for savvy shoppers</p>
</div>
""", unsafe_allow_html=True)
