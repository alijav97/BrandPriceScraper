"""
Verify AI integration is working correctly
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("🤖 AI INTEGRATION VERIFICATION")
print("=" * 70)

# Test 1: Check .env file
print("\n✓ Test 1: Checking .env file...")
if os.path.exists(".env"):
    print("  ✅ .env file exists")
    with open(".env", "r") as f:
        content = f.read()
        if "OPENAI_API_KEY" in content:
            print("  ✅ OPENAI_API_KEY found in .env")
        else:
            print("  ❌ OPENAI_API_KEY not found in .env")
else:
    print("  ❌ .env file not found")

# Test 2: Check .env in gitignore
print("\n✓ Test 2: Checking .gitignore...")
if os.path.exists(".gitignore"):
    with open(".gitignore", "r") as f:
        content = f.read()
        if ".env" in content:
            print("  ✅ .env is in .gitignore (protected)")
        else:
            print("  ⚠️  .env might not be in .gitignore")
else:
    print("  ⚠️  .gitignore file not found")

# Test 3: Check OpenAI module
print("\n✓ Test 3: Checking OpenAI module...")
try:
    from openai import OpenAI
    print("  ✅ OpenAI module imported successfully")
except ImportError as e:
    print(f"  ❌ Failed to import OpenAI: {e}")

# Test 4: Check AI analyzer module
print("\n✓ Test 4: Checking AI analyzer module...")
try:
    from utils.openai_analyzer import PriceAnalyzer, PricePrediction
    print("  ✅ PriceAnalyzer imported successfully")
    print("  ✅ PricePrediction imported successfully")
except ImportError as e:
    print(f"  ❌ Failed to import analyzer: {e}")

# Test 5: Check environment variables
print("\n✓ Test 5: Checking environment variables...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        if api_key.startswith("sk-proj-"):
            print("  ✅ OPENAI_API_KEY is set (valid format)")
        else:
            print("  ⚠️  OPENAI_API_KEY format may be incorrect")
    else:
        print("  ❌ OPENAI_API_KEY not loaded from environment")
except Exception as e:
    print(f"  ❌ Error loading environment: {e}")

# Test 6: Check app.py has AI features
print("\n✓ Test 6: Checking app.py for AI features...")
try:
    with open("app.py", "r") as f:
        app_content = f.read()
        checks = {
            "PriceAnalyzer": "PriceAnalyzer" in app_content,
            "AI Analysis section": "🤖 AI-Powered" in app_content,
            "enable_ai checkbox": "enable_ai" in app_content,
            "AI tabs": "ai_tab1" in app_content,
        }
        
        for check, result in checks.items():
            if result:
                print(f"  ✅ {check}")
            else:
                print(f"  ❌ {check}")
except Exception as e:
    print(f"  ❌ Error checking app.py: {e}")

# Test 7: Check requirements
print("\n✓ Test 7: Checking requirements.txt...")
try:
    with open("requirements.txt", "r") as f:
        req_content = f.read()
        if "openai" in req_content:
            print("  ✅ openai package in requirements.txt")
        else:
            print("  ❌ openai package not in requirements.txt")
except Exception as e:
    print(f"  ❌ Error checking requirements: {e}")

# Test 8: Documentation
print("\n✓ Test 8: Checking documentation...")
docs = {
    "OPENAI_SETUP.md": "OpenAI setup guide",
    "AI_ENHANCEMENT_COMPLETE.md": "AI enhancement summary",
    ".env.example": "Environment template",
}

for doc, description in docs.items():
    if os.path.exists(doc):
        print(f"  ✅ {doc} - {description}")
    else:
        print(f"  ❌ {doc} - {description} (missing)")

print("\n" + "=" * 70)
print("✨ AI INTEGRATION VERIFICATION COMPLETE!")
print("=" * 70)

print("\n📋 SUMMARY:")
print("─" * 70)
print("\n✅ If all checks passed, you're ready to run:")
print("\n   streamlit run app.py\n")

print("🤖 AI Features Available:")
print("  • Market Insights (📊)")
print("  • Smart Recommendations (✅)")
print("  • Price Predictions (🔮)")
print("  • Comprehensive Reports (📋)\n")

print("🔒 Security:")
print("  • API key in .env (protected)")
print("  • .env in .gitignore (won't commit)")
print("  • Environment variables used (secure)\n")

print("💡 Next Steps:")
print("  1. Run: streamlit run app.py")
print("  2. Enter a brand name")
print("  3. Click 'Search Brand Prices'")
print("  4. View AI analysis tabs\n")

print("=" * 70)
