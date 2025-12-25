# 🔒 OpenAI Integration & Security Guide

## Setup Instructions

### Step 1: Install OpenAI Package

```bash
pip install openai
```

Or if you want to update all dependencies:

```bash
pip install -r requirements.txt
```

### Step 2: Create .env File

1. **In your project folder**, create a file named `.env` (note: the dot is important)

2. **Add your OpenAI API key:**
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Optional settings:**
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_TIMEOUT=30
   ```

### Step 3: Run the App

```bash
streamlit run app.py
```

The AI analysis features will now be available!

---

## 🔐 Security Best Practices

### ❌ NEVER DO THIS:

```python
# ❌ WRONG - Hardcoded API key
client = OpenAI(api_key="sk-proj-xxxxx")

# ❌ WRONG - Committed to GitHub
# In your code
OPENAI_API_KEY = "sk-proj-xxxxx"
```

### ✅ ALWAYS DO THIS:

```python
# ✅ CORRECT - Load from environment
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
```

---

## 📋 .env File Handling

### Create the .env File

**Location:** `c:\Users\alija\Downloads\London International - AI\Module C\App for self\.env`

**Contents:**
```bash
OPENAI_API_KEY=your_actual_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TIMEOUT=30
```

### Make Sure It's Ignored

The `.gitignore` file **already includes** `.env`, so it won't be committed to GitHub.

### Example .env Template

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
# Then edit .env with your API key
```

---

## 🔑 Getting Your OpenAI API Key

1. Go to https://platform.openai.com/account/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (you'll only see it once!)
5. Paste it in your `.env` file

### Setting Up Billing

1. Visit https://platform.openai.com/account/billing/overview
2. Add a payment method
3. Set usage limits to prevent unexpected charges

---

## 💳 Cost Information

### API Usage Rates

**GPT-3.5-turbo** (recommended for this app):
- Input: $0.0005 per 1K tokens
- Output: $0.0015 per 1K tokens

**Typical Analysis Cost:**
- One brand analysis: ~$0.01-0.05

**Cost Control:**
- Set usage limits in OpenAI dashboard
- Monitor your usage regularly
- Use the cheaper gpt-3.5-turbo model

---

## 🚨 If Your Key Gets Compromised

1. **Immediately revoke it:**
   - Go to https://platform.openai.com/account/api-keys
   - Find the key and delete it
   
2. **Create a new key**

3. **Update your .env file**

---

## 🔍 Troubleshooting

### "OPENAI_API_KEY not found" Error

**Solution:**
1. Ensure `.env` file exists in your project root
2. Make sure it contains: `OPENAI_API_KEY=sk-proj-...`
3. Restart the Streamlit app

### "Bad API Key" Error

**Solution:**
1. Check you copied the full key correctly
2. The key should start with `sk-proj-`
3. Make sure there are no extra spaces

### Rate Limit Error

**Solution:**
1. Wait a few moments before retrying
2. OpenAI has rate limits for free accounts
3. Upgrade your account or reduce analysis frequency

### API Timeout

**Solution:**
1. Increase timeout in `.env`:
   ```
   OPENAI_TIMEOUT=60
   ```
2. Check your internet connection

---

## 📚 AI Features Available

### 1. Market Insights 📊
- Price patterns across regions
- Competition analysis
- Market opportunities

### 2. Recommendations ✅
- Best places to buy
- Timing considerations
- Value analysis

### 3. Price Predictions 🔮
- 30-day trend forecast
- Confidence levels
- Seasonal factors

### 4. Comprehensive Report 📋
- Full market analysis
- Downloadable summary
- All metrics included

---

## 🛡️ Data Privacy

### What Gets Sent to OpenAI

✅ Product titles, prices, and regions (anonymized)
✅ Market statistics only (no personal data)

### What Doesn't Get Sent

❌ Your browsing history
❌ Personal information
❌ Raw HTML or page data

---

## 🔄 Environment Variables Reference

```bash
# Required
OPENAI_API_KEY=sk-proj-...

# Optional (defaults provided)
OPENAI_MODEL=gpt-3.5-turbo        # Model to use
OPENAI_TIMEOUT=30                 # Timeout in seconds
```

---

## ✅ Checklist

Before running with AI features:

- [ ] OpenAI account created
- [ ] API key generated
- [ ] `.env` file created in project root
- [ ] API key added to `.env`
- [ ] `.env` file is in `.gitignore` (it is by default)
- [ ] Billing enabled on OpenAI account
- [ ] All dependencies installed (`pip install -r requirements.txt`)

---

## 🚀 Deploy to Streamlit Cloud with API Key

### Important: Secrets Management

**On Streamlit Cloud, use Secrets:**

1. Go to your app settings on Streamlit Cloud
2. Click "Secrets"
3. Add:
   ```
   OPENAI_API_KEY = "sk-proj-..."
   ```

**Never put .env in GitHub!** The `.gitignore` prevents this automatically.

---

## 📞 Support

- **OpenAI Documentation:** https://platform.openai.com/docs
- **API Status:** https://status.openai.com
- **Community:** https://community.openai.com

---

**Created:** December 25, 2025  
**Status:** ✅ Ready for Production  
**Security Level:** Enterprise-Grade
