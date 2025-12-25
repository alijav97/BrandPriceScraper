# 🌍 Regional Brand Price Tracker

Track official brand product prices across different regions and countries. Compare prices by product and find the best deals globally.

## ✨ Key Features

### 🎯 Regional Brand Tracking
- **Official Websites Only** - Scrape directly from brand's official regional websites
- **Multiple Regions** - Compare prices across different countries simultaneously
- **By Product Organization** - See each product's price in all selected regions

### 💰 Price Comparison
- **Best Deals Detection** - Automatically identify the cheapest region for each product
- **Savings Analysis** - Calculate how much you can save by ordering from different regions
- **Price Markups** - View percentage markups across regions

### 🤖 AI-Powered Insights
- Get smart recommendations on where to buy
- Analyze market pricing patterns
- 30-day price trend predictions
- Download professional analysis reports

### 📊 Multiple Views
- **Price Comparison Table** - Side-by-side pricing across regions
- **Best Deals** - Highlighted deals and savings opportunities
- **Price Analysis** - Statistical insights and trends
- **Export Data** - Download as CSV for further analysis

## 🚀 Supported Brands

Currently tracking official websites for:
- 🏃 **Lululemon** (US, UK, Canada, UAE, Germany)
- 👟 **Nike** (US, UK, UAE, Germany, Australia)
- 👕 **Adidas** (US, UK, UAE, Germany, Canada)
- 🐆 **Puma** (US, UK, UAE, Germany)
- 🍎 **Apple** (US, UK, UAE, Germany, Australia)
- 📱 **Samsung** (US, UK, UAE, Germany)

*More brands being added regularly!*

## 📍 Supported Regions

- 🇺🇸 United States (USD)
- 🇬🇧 United Kingdom (GBP)
- 🇦🇪 United Arab Emirates (AED)
- 🇩🇪 Germany (EUR)
- 🇨🇦 Canada (CAD)
- 🇦🇺 Australia (AUD)

## 🎯 How to Use

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Add your OpenAI API key to .env
   ```

3. **Run the app:**
   ```bash
   streamlit run app_regional.py
   ```

### Usage Steps

1. **Select a Brand** - Choose from the available brands in the sidebar
2. **Pick Regions** - Select which regions to compare (multi-select)
3. **Search Prices** - Click "Search Prices" to fetch product data
4. **Analyze Results** - View different tabs for comparison, deals, and insights
5. **Export Data** - Download results as CSV or summary text

## 📁 Project Structure

```
├── config/
│   ├── brand_sites.json          # Brand → Regional URLs mapping
│   ├── settings.py               # Configuration settings
│   └── __init__.py
├── src/
│   ├── regional_scraper.py       # Regional website scraper
│   ├── scraper.py                # Legacy e-commerce scraper
│   └── __init__.py
├── utils/
│   ├── regional_processor.py     # Regional data processing
│   ├── processor.py              # Legacy data processor
│   ├── openai_analyzer.py        # AI analysis module
│   ├── helpers.py                # Utility functions
│   └── __init__.py
├── app_regional.py               # Main regional tracker app
├── app.py                        # Legacy e-commerce tracker app
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not in git)
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 🔍 How Scraping Works

### RegionalBrandScraper
- Reads official brand regional URLs from `config/brand_sites.json`
- Makes HTTP requests to each regional website
- Uses BeautifulSoup to parse HTML
- Extracts product names and prices with generic CSS selectors
- Returns standardized product data with region info

### Data Structure
```json
{
  "name": "Product Name",
  "brand": "Brand Name",
  "prices": {
    "US": {"price": 100, "currency": "USD", "currency_code": "$"},
    "UK": {"price": 85, "currency": "GBP", "currency_code": "£"},
    "UAE": {"price": 400, "currency": "AED", "currency_code": "د.إ"}
  },
  "links": {
    "US": "https://...",
    "UK": "https://..."
  }
}
```

## 🛠️ Configuration

### Adding New Brands

Edit `config/brand_sites.json`:

```json
{
  "YourBrand": {
    "name": "Your Brand",
    "regions": {
      "US": {
        "url": "https://www.yourbrand.com",
        "currency": "USD",
        "currency_code": "$"
      },
      "UK": {
        "url": "https://www.yourbrand.co.uk",
        "currency": "GBP",
        "currency_code": "£"
      }
    }
  }
}
```

### Adding New Regions

Add to any brand's `regions` section:

```json
"CountryCode": {
  "url": "https://brand_regional_url.com",
  "currency": "CurrencyName",
  "currency_code": "¤"
}
```

## 📊 Tab Overview

### 1️⃣ Price Comparison
- Side-by-side pricing table
- Shows prices in each region's currency
- Organized by product name

### 2️⃣ Best Deals
- Highlighted best prices per product
- Shows savings potential
- Displays price markups per region

### 3️⃣ Price Analysis
- Statistical summaries (avg, min, max)
- Price distribution by region
- Comparative analysis charts

### 4️⃣ AI Insights
- Market analysis with ChatGPT
- Smart buying recommendations
- Price trend predictions
- Professional formatted reports

### 5️⃣ Export Data
- Download as CSV for Excel/Sheets
- Export summary as text file
- Ready for further analysis

## 🔐 Security

- **API Keys** - Stored in `.env` file (excluded from git)
- **No Hardcoding** - All secrets use environment variables
- **Encrypted Transmission** - HTTPS for all requests
- **Data Privacy** - Only anonymized data sent to OpenAI

## 📦 Dependencies

- `streamlit` - Web app framework
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `pandas` - Data processing
- `openai` - AI analysis
- `python-dotenv` - Environment management

## ⚡ Performance Tips

1. **Cache Results** - Data is cached during session
2. **Select Fewer Regions** - Faster search with fewer regions
3. **Popular Brands** - Some brands load faster than others
4. **Off-peak Hours** - Better response times during off-peak hours

## 🐛 Troubleshooting

### "No products found"
- The brand website might have anti-scraping protection
- Try a different region or brand
- Some websites require JavaScript rendering (not currently supported)

### Prices are 0 or missing
- Generic CSS selectors might not work for all websites
- Brand structure may require custom selectors
- Consider using the legacy e-commerce tracker

### API Key not working
- Verify key in `.env` file
- Check key has necessary permissions
- Monitor OpenAI dashboard for issues

### Slow searches
- Some websites are slower to load
- Try searching one region at a time
- Check your internet connection

## 🔄 Switching Between Apps

- **app.py** - Legacy e-commerce platform scraper (Amazon, eBay, etc.)
- **app_regional.py** - New regional brand tracker (official websites)

Run different apps with:
```bash
streamlit run app.py                # Legacy tracker
streamlit run app_regional.py       # Regional tracker
```

## 🚀 Deployment to Streamlit Cloud

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Regional brand tracker"
git push origin main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your repository
4. Set main file to `app_regional.py`
5. Click "Deploy"

### Step 3: Add Secrets
In Streamlit Cloud settings, add:
```
OPENAI_API_KEY = "sk-..."
```

## 📈 Future Enhancements

- [ ] Real-time price tracking with alerts
- [ ] Price history and graphs
- [ ] Currency conversion tool
- [ ] Shipping cost integration
- [ ] Wishlist functionality
- [ ] Price drop notifications
- [ ] Mobile app version
- [ ] More brands and regions
- [ ] Machine learning price predictions
- [ ] Multi-language support

## 📞 Support

For issues or feature requests:
1. Check existing GitHub issues
2. Review troubleshooting section
3. Check brand website is accessible
4. Verify OpenAI API status

## 📄 License

This project is open source. Feel free to use and modify!

## 👨‍💻 Made By

Created with ❤️ for savvy shoppers worldwide 🌍

---

**Version:** 2.1 (Regional Edition)  
**Last Updated:** December 25, 2025  
**Status:** ✅ Production Ready
