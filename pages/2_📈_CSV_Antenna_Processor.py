"""CSV Antenna Sweep Processor - Page wrapper for multi-page app"""
# This file imports and runs the CSV processor app
import sys
import os

# Add parent directory to path to import the main app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import theme toggle and apply it
from theme_toggle import apply_theme_toggle
apply_theme_toggle()

# Import and run the streamlit_process_all_csv module
import streamlit_process_all_csv

# Execute the main function
if __name__ == "__main__":
    streamlit_process_all_csv.main()
else:
    # When imported as a page, also run main
    streamlit_process_all_csv.main()
