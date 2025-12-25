# 🛍️ Brand Price Tracker

A powerful web scraping application that tracks and compares prices for any brand across multiple global e-commerce platforms.

## Features

✨ **Multi-Platform Scraping**
- Amazon (US, UK, Germany)
- eBay
- MercadoLibre
- And more...

💱 **Multi-Currency Support**
- Automatic currency detection
- Prices displayed with proper currency codes
- Support for USD, EUR, GBP, CNY, ARS, JPY, INR, and more

📊 **Data Analysis & Comparison**
- Real-time price tracking
- Identify price markdowns vs original prices
- Calculate discount percentages
- Compare prices across regions

🎨 **User-Friendly Interface**
- Built with Streamlit for interactive experience
- Filter and sort results easily
- Download results to CSV
- Responsive design

## Project Structure

```
Brand-Price-Tracker/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── config/
│   └── settings.py        # Configuration and site settings
├── src/
│   └── scraper.py         # Web scraping logic
├── utils/
│   └── processor.py       # Data processing and formatting
├── data/                  # Output data folder
└── README.md              # Documentation
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Brand-Price-Tracker.git
   cd Brand-Price-Tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Local Development

Run the Streamlit app locally:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the App

1. Enter a brand name in the sidebar (e.g., "Apple", "Sony", "Nike")
2. Click "Search Brand Prices"
3. View results across multiple platforms
4. Filter by site or region
5. Sort by price or other criteria
6. Download results to CSV

## Deployment on Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit Community Cloud account (free at streamlit.io)

### Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/Brand-Price-Tracker.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [Streamlit Cloud](https://share.streamlit.io/)
   - Click "New app"
   - Select your repository
   - Select branch: `main`
   - Set main file path: `app.py`
   - Click "Deploy"

Your app will be live at `https://share.streamlit.io/yourusername/brand-price-tracker`

## API/Data Sources

### Supported Platforms
- **Amazon**: US, UK, Germany, and other regions
- **eBay**: US marketplace
- **MercadoLibre**: Latin America
- **Alibaba**: International marketplace

### Data Points Collected
- Product title
- Current price
- Original price
- Site and region
- Currency code
- Product URL
- Timestamp

## Configuration

Edit `config/settings.py` to:
- Add or remove websites
- Adjust scraping timeouts
- Change maximum products per site
- Modify user agent list
- Set cache duration

## Development

### Adding New Scrapers

To add a new site scraper:

1. Add site configuration in `config/settings.py`:
   ```python
   'new_site': {
       'url': 'https://example.com/search',
       'search_param': 'q',
       'enabled': True,
       'region': 'Country',
       'currency': 'CURR'
   }
   ```

2. Add scraper method in `src/scraper.py`:
   ```python
   def scrape_new_site(self, brand_name: str) -> List[Dict]:
       # Implementation
       pass
   ```

3. Add method call in `scrape_multiple_sites()` method

### Handling Blocked Requests

If you encounter blocking:
- Add delays between requests
- Rotate user agents
- Use residential proxies
- Consider using Selenium for JavaScript-heavy sites

## Challenges & Solutions

### Challenge 1: Website Changes
**Solution**: Regularly update CSS selectors and HTML parsing logic

### Challenge 2: Rate Limiting
**Solution**: Implement request delays and proxy rotation

### Challenge 3: Dynamic Content
**Solution**: Use Selenium for JavaScript-rendered content

### Challenge 4: Currency Conversion
**Solution**: Use currency conversion API for real-time rates

## Future Enhancements

- [ ] Real-time currency conversion
- [ ] Price history tracking
- [ ] Email alerts for price drops
- [ ] Machine learning for price predictions
- [ ] Mobile app version
- [ ] Integration with more e-commerce platforms
- [ ] Selenium support for JavaScript-heavy sites
- [ ] Proxy rotation for better reliability
- [ ] Database integration for historical data

## Dependencies

- **streamlit**: Web app framework
- **requests**: HTTP library
- **beautifulsoup4**: HTML parsing
- **pandas**: Data processing
- **selenium**: Browser automation (optional)
- **python-dotenv**: Environment variables

See `requirements.txt` for full list and versions.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Issues & Troubleshooting

### Connection Timeout
- Check internet connection
- Increase TIMEOUT in `config/settings.py`
- Try a different website

### No Results Found
- Verify brand name spelling
- Try searching for specific product models
- Check if website is accessible

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify virtual environment is activated

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes. When web scraping:
- Respect website terms of service
- Check `robots.txt` before scraping
- Don't overload servers with requests
- Consider using official APIs when available
- Follow data protection regulations (GDPR, CCPA, etc.)

## Contact & Support

- GitHub Issues: [Report bugs or suggest features](https://github.com/yourusername/Brand-Price-Tracker/issues)
- Email: your.email@example.com

## Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Data from various e-commerce platforms
- Community feedback and contributions

---

**Happy Price Tracking! 🎉**

For updates and latest features, follow this repository.
