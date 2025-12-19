#!/usr/bin/env python3
"""
Validation script to ensure all necessary files and imports are working
Run this before deploying to catch any issues early
"""
import sys
import os
from pathlib import Path

def check_file(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ MISSING {description}: {filepath}")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ FAILED {description}: {module_name} - {e}")
        return False

def main():
    print("=" * 60)
    print("Antenna Tools Deployment Validation")
    print("=" * 60)

    all_good = True

    print("\n📄 Checking required files...")
    all_good &= check_file("Home.py", "Home page")
    all_good &= check_file("streamlit_antenna_gui_test.py", "Link Budget Calculator")
    all_good &= check_file("streamlit_process_all_csv.py", "CSV Processor")
    all_good &= check_file("pages/1_📊_Link_Budget_Calculator.py", "Page: Link Budget")
    all_good &= check_file("pages/2_📈_CSV_Antenna_Processor.py", "Page: CSV Processor")
    all_good &= check_file("Dockerfile", "Dockerfile")
    all_good &= check_file(".dockerignore", "Docker ignore file")
    all_good &= check_file(".streamlit/config.toml", "Streamlit config")
    all_good &= check_file("requirements.txt", "Requirements file")
    all_good &= check_file("DEPLOY.md", "Deployment guide")

    print("\n📦 Checking Python dependencies...")
    all_good &= check_import("streamlit", "Streamlit")
    all_good &= check_import("pandas", "Pandas")
    all_good &= check_import("numpy", "NumPy")
    all_good &= check_import("scipy", "SciPy")
    all_good &= check_import("matplotlib", "Matplotlib")
    all_good &= check_import("requests", "Requests")

    print("\n🔍 Checking app imports...")
    sys.path.insert(0, os.getcwd())
    try:
        import streamlit_antenna_gui_test
        print("✅ Link Budget Calculator imports successfully")
    except Exception as e:
        print(f"❌ Link Budget Calculator import failed: {e}")
        all_good = False

    try:
        import streamlit_process_all_csv
        print("✅ CSV Processor imports successfully")
    except Exception as e:
        print(f"❌ CSV Processor import failed: {e}")
        all_good = False

    print("\n" + "=" * 60)
    if all_good:
        print("✅ All checks passed! Ready to deploy.")
        print("\nNext steps:")
        print("1. Test locally: streamlit run Home.py")
        print("2. Deploy to Azure: See DEPLOY.md")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
