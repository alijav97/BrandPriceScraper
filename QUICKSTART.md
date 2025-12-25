# Quick Start Guide

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Usage

1. **Enter Brand Name**: Type any brand name (e.g., "Apple", "Sony", "Nike")
2. **Click Search**: The app will scrape multiple platforms
3. **View Results**: See products with prices, regions, and currencies
4. **Filter & Sort**: Use the options to filter by site/region or sort by price
5. **Download**: Export results to CSV for further analysis

## Deployment to Streamlit Cloud

### Step 1: Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit: Brand Price Tracker"
```

### Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create new repository: `Brand-Price-Tracker`
3. Copy the push commands and run:

```bash
git branch -M main
git remote add origin https://github.com/yourusername/Brand-Price-Tracker.git
git push -u origin main
```

### Step 3: Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://share.streamlit.io)
2. Click "New app"
3. Select repository: `yourusername/Brand-Price-Tracker`
4. Set main file: `app.py`
5. Click "Deploy"

Your app will be live!

## File Structure

```
Brand-Price-Tracker/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Dependencies
├── QUICKSTART.md            # This file
├── README.md                # Full documentation
├── .gitignore               # Git ignore rules
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration
├── src/
│   ├── __init__.py
│   └── scraper.py           # Scraping logic
├── utils/
│   ├── __init__.py
│   ├── processor.py         # Data processing
│   └── helpers.py           # Utilities
└── data/                    # Output folder
```

## Troubleshooting

### Module Import Errors
Make sure you're in the virtual environment and have installed requirements:
```bash
pip install -r requirements.txt
```

### Connection Errors
- Check internet connection
- Try a different brand name
- Wait a few seconds and retry

### Streamlit Not Found
```bash
pip install streamlit
streamlit run app.py
```

## Next Steps

- Add more websites to scrape
- Implement price history tracking
- Add email alerts for price drops
- Deploy database for historical data
- Add currency conversion API

For full documentation, see README.md
