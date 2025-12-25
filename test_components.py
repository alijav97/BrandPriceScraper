"""
Test script to verify all components are working
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🧪 Brand Price Tracker - Component Test")
print("=" * 60)

# Test 1: Import all modules
print("\n✓ Test 1: Importing modules...")
try:
    from config.settings import WEBSITES, TIMEOUT
    print("  ✓ Config imported successfully")
except Exception as e:
    print(f"  ✗ Config import failed: {e}")

try:
    from src.scraper import PriceScraper, DataCollector
    print("  ✓ Scraper imported successfully")
except Exception as e:
    print(f"  ✗ Scraper import failed: {e}")

try:
    from utils.processor import DataProcessor
    print("  ✓ Processor imported successfully")
except Exception as e:
    print(f"  ✗ Processor import failed: {e}")

# Test 2: Check settings
print("\n✓ Test 2: Checking configuration...")
try:
    from config.settings import WEBSITES, MAX_PRODUCTS_PER_SITE
    print(f"  ✓ Websites configured: {list(WEBSITES.keys())}")
    print(f"  ✓ Max products per site: {MAX_PRODUCTS_PER_SITE}")
except Exception as e:
    print(f"  ✗ Settings check failed: {e}")

# Test 3: Verify data processor
print("\n✓ Test 3: Testing data processor...")
try:
    processor = DataProcessor()
    test_price = processor._format_price(99.99, 'USD')
    print(f"  ✓ Price formatting works: {test_price}")
    
    discount = processor._calculate_discount(100, 75)
    print(f"  ✓ Discount calculation works: {discount}")
except Exception as e:
    print(f"  ✗ Processor test failed: {e}")

# Test 4: Check directory structure
print("\n✓ Test 4: Checking directory structure...")
required_dirs = ['src', 'config', 'utils', 'data']
for dir_name in required_dirs:
    dir_path = os.path.join(os.path.dirname(__file__), dir_name)
    if os.path.exists(dir_path):
        print(f"  ✓ {dir_name}/ exists")
    else:
        print(f"  ✗ {dir_name}/ missing")

# Test 5: Check required files
print("\n✓ Test 5: Checking required files...")
required_files = [
    'app.py',
    'requirements.txt',
    'README.md',
    'QUICKSTART.md',
    '.gitignore',
    'config/settings.py',
    'src/scraper.py',
    'utils/processor.py'
]

for file_name in required_files:
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(file_path):
        print(f"  ✓ {file_name} exists")
    else:
        print(f"  ✗ {file_name} missing")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
print("\nNext steps:")
print("1. Run: streamlit run app.py")
print("2. Enter a brand name (e.g., 'Apple', 'Sony')")
print("3. View results across platforms")
print("\nFor GitHub deployment:")
print("1. git init")
print("2. git add .")
print("3. git commit -m 'Initial commit'")
print("4. git branch -M main")
print("5. git remote add origin <your-repo-url>")
print("6. git push -u origin main")
print("\nThen deploy on Streamlit Cloud!")
