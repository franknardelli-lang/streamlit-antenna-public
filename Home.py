"""
Antenna Tools - Home Launcher
Navigate between different antenna calculation tools
"""
import streamlit as st
from theme_toggle import apply_theme_toggle

st.set_page_config(
    page_title="Antenna Tools Suite",
    page_icon="📡",
    layout="wide"
)

# Apply theme toggle
apply_theme_toggle()

st.title("📡 Antenna Tools Suite")
st.markdown("---")

st.markdown("""
Welcome to the Antenna Tools Suite! Choose a tool to get started:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Antenna Radiation Pattern Visualizer")
    st.markdown("""
    Visualize and analyze antenna radiation patterns:
    - Upload processed CSV files (_processed.csv)
    - Load from URLs (Google Drive, Dropbox, ZIP archives)
    - Generate polar radiation pattern plots
    - Calculate efficiency, HPBW, and other metrics
    - Download high-resolution plots and statistics

    **Use the sidebar to navigate** ⬅️
    """)

with col2:
    st.markdown("### 📈 CSV Antenna Sweep Processor")
    st.markdown("""
    Process raw antenna measurement data:
    - Upload multiple CSV sweep files
    - Load from URLs (Google Drive, Dropbox, etc.)
    - Combine two sweeps using Pythagorean sum
    - Convert between dBµV/m and V/m
    - Generate shareable download links

    **Use the sidebar to navigate** ⬅️
    """)

st.info("💡 **Tip:** Use the sidebar (⬅️) to navigate between tools!")

st.markdown("---")
st.markdown("""
### 📁 Navigation
Use the sidebar to switch between tools. Each tool runs as a separate page.

### ℹ️ About
This suite provides tools for antenna and RF link calculations, as well as
processing and analysis of antenna measurement data.
""")
