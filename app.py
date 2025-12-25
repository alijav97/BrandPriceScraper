"""
Streamlit Web App for Brand Price Scraper with AI-Powered Analysis
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

# Add src and config to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scraper import DataCollector
from utils.processor import DataProcessor
from utils.openai_analyzer import PriceAnalyzer, PricePrediction


# Page configuration
st.set_page_config(
    page_title="Brand Price Tracker",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .main {
            padding: 0rem 0rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'products_data' not in st.session_state:
        st.session_state.products_data = None
    if 'brand_searched' not in st.session_state:
        st.session_state.brand_searched = None
    if 'last_search_time' not in st.session_state:
        st.session_state.last_search_time = None


def main():
    """Main application"""
    init_session_state()
    
    # Header
    st.markdown("# 🛍️ Brand Price Tracker")
    st.markdown("*Find the best prices for your favorite brands across global online retailers*")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Brand input
        brand_name = st.text_input(
            "Enter Brand Name",
            placeholder="e.g., Apple, Sony, Nike",
            key="brand_input"
        )
        
        # Search button
        search_button = st.button(
            "🔍 Search Brand Prices",
            type="primary",
            use_container_width=True
        )
        
        st.divider()
        
        # AI Analysis toggle
        enable_ai = st.checkbox("🤖 Enable AI Analysis", value=True)
        
        st.divider()
        
        # Additional options
        st.subheader("Options")
        
        include_markdown = st.checkbox("Include Markdown/Sale Items", value=True)
        export_data = st.checkbox("Export Results to CSV", value=False)
        
        st.divider()
        
        # Info section
        st.subheader("ℹ️ About")
        st.info(
            "This app searches multiple e-commerce platforms including "
            "Amazon (US, UK, DE), eBay, and more for product prices in "
            "their respective currencies. AI-powered analysis provides "
            "insights and recommendations."
        )
    
    # Main content area
    if search_button and brand_name.strip():
        with st.spinner(f"🔄 Searching for {brand_name} across platforms..."):
            try:
                # Collect data
                collector = DataCollector()
                products = collector.collect_brand_data(brand_name)
                
                # Store in session state
                st.session_state.products_data = products
                st.session_state.brand_searched = brand_name
                st.session_state.last_search_time = datetime.now()
                
                # Process data
                processor = DataProcessor()
                df = processor.process_products(products)
                
                if not df.empty:
                    st.success(f"✓ Found {len(df)} products for '{brand_name}'")
                else:
                    st.warning(f"No products found for '{brand_name}'. Try a different search term.")
                
            except Exception as e:
                st.error(f"❌ Error during search: {str(e)}")
                st.info("Please check your internet connection and try again.")
    
    # Display results if available
    if st.session_state.products_data:
        processor = DataProcessor()
        df = processor.process_products(st.session_state.products_data)
        
        if not df.empty:
            # Summary Statistics
            st.subheader("📊 Summary Statistics")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Products", len(df))
            
            with col2:
                st.metric("Sites Searched", df['site'].nunique())
            
            with col3:
                st.metric("Regions", df['region'].nunique())
            
            with col4:
                min_price = df['current_price'].min()
                st.metric("Lowest Price", f"${min_price:.2f}" if min_price else "N/A")
            
            with col5:
                avg_price = df['current_price'].mean()
                st.metric("Average Price", f"${avg_price:.2f}" if avg_price else "N/A")
            
            st.divider()
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_sites = st.multiselect(
                    "Filter by Site",
                    options=df['site'].unique(),
                    default=df['site'].unique()
                )
            
            with col2:
                selected_regions = st.multiselect(
                    "Filter by Region",
                    options=df['region'].unique(),
                    default=df['region'].unique()
                )
            
            with col3:
                sort_by = st.selectbox(
                    "Sort by",
                    options=["Price (Low to High)", "Price (High to Low)", "Site", "Region"]
                )
            
            # Apply filters
            filtered_df = df[
                (df['site'].isin(selected_sites)) & 
                (df['region'].isin(selected_regions))
            ]
            
            # Apply sorting
            if sort_by == "Price (Low to High)":
                filtered_df = filtered_df.sort_values('current_price', ascending=True)
            elif sort_by == "Price (High to Low)":
                filtered_df = filtered_df.sort_values('current_price', ascending=False)
            elif sort_by == "Site":
                filtered_df = filtered_df.sort_values('site')
            elif sort_by == "Region":
                filtered_df = filtered_df.sort_values('region')
            
            # Display formatted table
            st.subheader("📋 Product Prices")
            display_df = processor.format_for_display(filtered_df)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Product": st.column_config.TextColumn(width="medium"),
                    "Site": st.column_config.TextColumn(width="small"),
                    "Region": st.column_config.TextColumn(width="small"),
                    "Current Price": st.column_config.TextColumn(width="small"),
                    "Original Price": st.column_config.TextColumn(width="small"),
                    "Currency Code": st.column_config.TextColumn(width="small"),
                    "Discount": st.column_config.TextColumn(width="small"),
                }
            )
            
            # Export functionality
            if export_data or st.button("📥 Download CSV"):
                csv_filename = f"brand_prices_{st.session_state.brand_searched}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                csv_path = os.path.join("data", csv_filename)
                
                # Create data folder if it doesn't exist
                os.makedirs("data", exist_ok=True)
                
                export_result = processor.export_to_csv(display_df, csv_path)
                st.success(export_result)
                
                # Provide download button
                with open(csv_path, 'r') as f:
                    st.download_button(
                        label="📊 Download Results",
                        data=f.read(),
                        file_name=csv_filename,
                        mime="text/csv"
                    )
            
            st.divider()
            
            # Display detailed information
            with st.expander("📝 View Details"):
                for idx, row in filtered_df.iterrows():
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{row['title'][:80]}...**")
                            st.markdown(f"🏪 {row['site']} | 🌍 {row['region']}")
                        
                        with col2:
                            st.metric(
                                "Price",
                                f"{processor._format_price(row['current_price'], row['currency'])}"
                            )
                        
                        if row['url'] and row['url'] != 'N/A':
                            st.markdown(f"[View on {row['site']}]({row['url']})")
            
            # AI-Powered Analysis Section
            if enable_ai:
                st.divider()
                st.subheader("🤖 AI-Powered Market Analysis")
                
                try:
                    # Initialize analyzers
                    analyzer = PriceAnalyzer()
                    predictor = PricePrediction()
                    
                    # Create tabs for different analyses
                    ai_tab1, ai_tab2, ai_tab3, ai_tab4 = st.tabs([
                        "📊 Insights",
                        "✅ Recommendations", 
                        "🔮 Predictions",
                        "📋 Full Report"
                    ])
                    
                    with ai_tab1:
                        st.markdown("#### Key Market Insights")
                        with st.spinner("🤖 Analyzing market insights..."):
                            analysis = analyzer.analyze_prices(filtered_df, st.session_state.brand_searched)
                            
                            if "insights" in analysis:
                                st.markdown(analysis["insights"])
                            else:
                                st.error(analysis.get("error", "Analysis failed"))
                    
                    with ai_tab2:
                        st.markdown("#### Purchasing Recommendations")
                        with st.spinner("🤖 Generating recommendations..."):
                            analysis = analyzer.analyze_prices(filtered_df, st.session_state.brand_searched)
                            
                            if "recommendations" in analysis:
                                st.markdown(analysis["recommendations"])
                            else:
                                st.error(analysis.get("error", "Analysis failed"))
                    
                    with ai_tab3:
                        st.markdown("#### 30-Day Price Trend Prediction")
                        with st.spinner("🤖 Predicting price trends..."):
                            prediction = predictor.predict_trend(filtered_df)
                            st.info(prediction)
                    
                    with ai_tab4:
                        st.markdown("#### Comprehensive Market Report")
                        with st.spinner("🤖 Generating comprehensive report..."):
                            report = analyzer.generate_report(filtered_df, st.session_state.brand_searched)
                            st.code(report, language="text")
                            
                            # Download button for report
                            st.download_button(
                                label="📥 Download Analysis Report",
                                data=report,
                                file_name=f"analysis_{st.session_state.brand_searched}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                
                except ValueError as e:
                    st.warning(
                        f"⚠️ AI Analysis Not Available: {str(e)}\n\n"
                        "To enable AI analysis:\n"
                        "1. Create a `.env` file in the project folder\n"
                        "2. Add: `OPENAI_API_KEY=your_api_key_here`\n"
                        "3. Restart the app"
                    )
                except Exception as e:
                    st.error(f"❌ Analysis Error: {str(e)}")
            
            # Last updated
            st.divider()
            st.caption(
                f"Last updated: {st.session_state.last_search_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
    
    else:
        # Initial state message
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                ### 👋 Welcome to Brand Price Tracker
                
                **How to use:**
                1. Enter a brand name (e.g., Apple, Sony, Nike)
                2. Click "Search Brand Prices"
                3. View results across multiple platforms and regions
                4. Filter and sort by your preferences
                5. Export results to CSV
                
                **Features:**
                - 🌍 Search across Amazon, eBay, and more
                - 💱 Prices in multiple currencies
                - 📊 Compare prices across regions
                - 💾 Export data for analysis
            """)


if __name__ == "__main__":
    main()
