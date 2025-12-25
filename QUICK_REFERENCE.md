# 🚀 QUICK REFERENCE CARD

## ⚡ Essential Commands

### Run the App
```bash
streamlit run app.py
```
📍 Access at: `http://localhost:8501`

### Run Tests
```bash
python test_components.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Activate Virtual Environment
```bash
# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

---

## 📁 Key Files Reference

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application |
| `src/scraper.py` | Web scraping logic |
| `utils/processor.py` | Data processing |
| `config/settings.py` | Configuration settings |
| `requirements.txt` | Dependencies list |
| `README.md` | Full documentation |

---

## 🌐 Supported Sites

- ✅ Amazon (US, UK, Germany)
- ✅ eBay
- ✅ MercadoLibre  
- ✅ Alibaba

### Add New Site
1. Edit `config/settings.py` - add site config
2. Edit `src/scraper.py` - add scraper method
3. Call method in `scrape_multiple_sites()`

---

## 💰 Currencies

USD, EUR, GBP, CNY, ARS, JPY, INR

---

## 📤 Deploy to Cloud

### GitHub Steps
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

### Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select repository and `app.py`
4. Click "Deploy"

---

## ⚙️ Configuration

File: `config/settings.py`

Key Settings:
- `WEBSITES` - Sites to scrape
- `TIMEOUT` - Request timeout
- `MAX_PRODUCTS_PER_SITE` - Products per site
- `CACHE_DURATION` - Cache expiry

---

## 🐛 Troubleshooting

### App won't run
→ Check venv is activated: `(venv)` should appear
→ Verify dependencies: `pip install -r requirements.txt`

### No results
→ Check internet connection
→ Try different brand name
→ Website structure may have changed

### Import errors
→ Ensure virtual environment is active
→ Run: `pip install -r requirements.txt`

---

## 📚 Documentation Files

- `README.md` - Full guide
- `QUICKSTART.md` - Fast setup
- `CHECKLIST.md` - Complete checklist
- `SETUP_COMPLETE.md` - Setup summary
- `PROJECT_SUMMARY.txt` - This summary

---

## 🎯 Usage Flow

```
User Input Brand Name
         ↓
   Run Scraper
         ↓
   Process Data
         ↓
   Display Results
         ↓
Export to CSV (optional)
```

---

## 📊 Data Processing

Features:
- Price formatting with currency
- Discount calculation
- Duplicate removal
- Filtering & sorting
- CSV export

---

## 🔒 Scraping Ethics

✓ Respect `robots.txt`
✓ Don't spam requests (delays included)
✓ Check Terms of Service
✓ Follow GDPR/CCPA
✓ Be responsible with servers

---

## 📞 Quick Help

**Virtual Environment Issues?**
```bash
python -m venv venv
```

**Reinstall Dependencies?**
```bash
pip install -r requirements.txt --force-reinstall
```

**Check What's Installed?**
```bash
pip list
```

**Clear Cache?**
```bash
rm -rf __pycache__ .streamlit/cache
```

---

## 🌟 Project Structure

```
App for self/
├── app.py              ← Run this!
├── requirements.txt
├── config/
│   └── settings.py
├── src/
│   └── scraper.py
├── utils/
│   └── processor.py
└── data/
```

---

## 🎓 Learning Path

1. ✅ Basic setup (done)
2. ⬜ Run app locally
3. ⬜ Add more sites
4. ⬜ Deploy to cloud
5. ⬜ Add database
6. ⬜ Create API
7. ⬜ Build mobile app

---

## 💡 Pro Tips

- Use `.gitignore` before pushing to GitHub
- Keep `venv/` out of version control
- Test with `test_components.py`
- Monitor requests - use delays
- Update scrapers when sites change HTML

---

**Created:** December 25, 2025
**Status:** ✅ Complete & Ready
**Version:** 1.0
