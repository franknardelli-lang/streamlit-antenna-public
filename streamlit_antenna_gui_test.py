"""
Streamlit Antenna Radiation Pattern Visualization Tool

This is a Streamlit web application for loading, analyzing, and visualizing
antenna radiation pattern data from processed CSV files.

Key Features:
- Web-based interface for uploading multiple processed CSV files.
- Alternative URL-based file loading for users behind restrictive firewalls.
- Caches processed data to avoid recalculations on UI updates.
- Parses each CSV into a pandas DataFrame and calculates key antenna metrics.
- Multi-select widget to choose one or more datasets to plot.
- UI organized into tabs for 'Plot' and 'Statistics'.
- Computes and plots polar radiation patterns using matplotlib with:
    * Customizable line width and legend visibility.
    * Polar plots with theta=0 at North and clockwise direction.
    * Multiple datasets plotted with distinct colors.
- Displays detailed statistics including Max, Min, Avg Power, Efficiency, and HPBW.
- Enables downloading the generated plot and the statistics table.

CSV File Format Requirement:
- Column 0: Angle values in degrees
- Column 3: Total field strength values in dBµV/m
- At least 4 columns total

File Naming Convention:
- Processes files ending in '_processed.csv'

Dependencies:
- streamlit, numpy, pandas, matplotlib, requests

Usage:
- Run: streamlit run streamlit_antenna_gui_test.py
- Upload processed CSV files through the web interface or load from URLs
- Select variables, enter parameters, and view/download plots and data
"""

import io
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs

# --- URL File Loading Classes and Functions ---

class UploadedFileFromURL:
    """Wrapper to make BytesIO compatible with Streamlit's UploadedFile interface"""
    
    def __init__(self, content, name):
        """
        Initialize wrapper with file content and name.
        
        Args:
            content: BytesIO object containing file data
            name: Filename string
        """
        self._content = content
        self.name = name
        # Cache the content for pickling/hashing
        self._content.seek(0)
        self._bytes = self._content.getvalue()
        self._content.seek(0)
    
    def seek(self, position):
        """Seek to position in file"""
        return self._content.seek(position)
    
    def read(self, size=-1):
        """Read file content"""
        return self._content.read(size)
    
    def getvalue(self):
        """Get entire file content"""
        return self._content.getvalue()
    
    def __reduce__(self):
        """Support for pickling (required for Streamlit caching)"""
        return (
            _reconstruct_uploaded_file,
            (self._bytes, self.name)
        )


def _reconstruct_uploaded_file(content_bytes, name):
    """Reconstruct UploadedFileFromURL from pickled state"""
    return UploadedFileFromURL(io.BytesIO(content_bytes), name)


def convert_share_url_to_direct(url):
    """
    Convert sharing URLs from Google Drive, Dropbox, and OneDrive to direct download URLs.
    
    Args:
        url: The sharing URL to convert
        
    Returns:
        str: Direct download URL
    """
    # Parse the URL to safely check the domain
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # Google Drive conversion
    # Pattern: https://drive.google.com/file/d/FILE_ID/view → https://drive.google.com/uc?export=download&id=FILE_ID
    if domain in ('drive.google.com', 'www.drive.google.com'):
        gdrive_pattern = r'https://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)'
        match = re.search(gdrive_pattern, url)
        if match:
            file_id = match.group(1)
            return f'https://drive.google.com/uc?export=download&id={file_id}'
    
    # Dropbox conversion
    # Ensure dl=1 parameter
    if domain in ('www.dropbox.com', 'dropbox.com'):
        if 'dl=0' in url:
            return url.replace('dl=0', 'dl=1', 1)
        elif 'dl=1' not in url:
            separator = '&' if '?' in url else '?'
            return f'{url}{separator}dl=1'
    
    # OneDrive conversion
    # Pattern: Convert share link to download link
    if domain in ('onedrive.live.com', '1drv.ms'):
        # OneDrive share links can be converted by replacing 'view' with 'download'
        return url.replace('view.aspx', 'download.aspx')
    
    # Return original URL if no conversion needed
    return url


def download_file_from_url(url, timeout=30):
    """
    Download a file from a URL and return it as a file-like object.
    Converts common sharing URLs to direct download URLs.
    
    Args:
        url: The URL to download from
        timeout: Request timeout in seconds
        
    Returns:
        tuple: (BytesIO object, original filename or None, error message or None)
    """
    try:
        # Validate URL scheme (only allow http and https)
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return None, None, f"Invalid URL scheme: {parsed.scheme}. Only HTTP and HTTPS are allowed."
        
        # Basic validation to prevent SSRF attacks on private networks
        # Block localhost and private IP ranges
        hostname = parsed.hostname
        if hostname:
            hostname_lower = hostname.lower()
            # Block localhost
            if hostname_lower in ('localhost', '127.0.0.1', '::1'):
                return None, None, "Access to localhost is not allowed for security reasons."
            # Block private IP ranges (basic check)
            if hostname_lower.startswith(('10.', '172.16.', '172.17.', '172.18.', '172.19.', 
                                          '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
                                          '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
                                          '172.30.', '172.31.', '192.168.')):
                return None, None, "Access to private IP addresses is not allowed for security reasons."
        
        # Convert sharing URLs to direct download URLs
        direct_url = convert_share_url_to_direct(url)
        
        # Set headers to avoid bot blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Download the file
        response = requests.get(direct_url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Extract filename from Content-Disposition header or URL
        filename = None
        if 'Content-Disposition' in response.headers:
            content_disp = response.headers['Content-Disposition']
            # Match filename with optional quotes: filename="file.csv" or filename=file.csv
            filename_match = re.search(r'filename[^;=\n]*=([\'"]?)([^;\n]*?)\1', content_disp)
            if filename_match:
                filename = filename_match.group(2).strip()
        
        if not filename:
            # Try to extract from URL path
            parsed_url = urlparse(direct_url)
            path = parsed_url.path
            if path:
                filename = path.split('/')[-1]
            
        if not filename or not filename.endswith('.csv'):
            filename = 'downloaded_file.csv'
        
        # Create BytesIO object from content
        file_content = io.BytesIO(response.content)
        
        return file_content, filename, None
        
    except requests.exceptions.Timeout:
        return None, None, f"Timeout: Server took longer than {timeout} seconds to respond"
    except requests.exceptions.ConnectionError:
        return None, None, "Connection Error: Could not connect to the server"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None, None, "Error 404: File not found"
        elif e.response.status_code == 403:
            return None, None, "Error 403: Access forbidden - file may not be publicly accessible"
        else:
            return None, None, f"HTTP Error {e.response.status_code}: {str(e)}"
    except Exception as e:
        return None, None, f"Unexpected error: {str(e)}"


# --- Data Processing Functions ---

def calculate_hpbw(angles_deg, P_dBm):
    """Calculate the Half-Power Beamwidth (HPBW)."""
    max_power_idx = np.argmax(P_dBm)
    max_power_val = P_dBm[max_power_idx]
    half_power_val = max_power_val - 3

    # Find where the power crosses the half-power level
    intersections = np.where(np.diff(np.sign(P_dBm - half_power_val)))[0]

    if len(intersections) < 2:
        return None  # Not enough data to determine beamwidth

    # Find the two intersection points closest to the main lobe
    main_lobe_angle = angles_deg[max_power_idx]
    
    # Sort intersections by angular distance to the main lobe's peak angle
    sorted_intersections = sorted(intersections, key=lambda i: min(abs(angles_deg[i] - main_lobe_angle), 360 - abs(angles_deg[i] - main_lobe_angle)))

    if len(sorted_intersections) < 2:
        return None

    angle1 = angles_deg[sorted_intersections[0]]
    angle2 = angles_deg[sorted_intersections[1]]

    hpbw = abs(angle1 - angle2)
    return hpbw if hpbw < 180 else 360 - hpbw


def process_dataset(df, iso_power_dBm):
    """
    Calculates all metrics for a given dataset.
    
    Returns:
        dict: A dictionary containing the original df, calculated power values, and all stats.
    """
    angles_deg = df.iloc[:, 0].values
    field_dBuV_m = df.iloc[:, 3].values

    # --- Calculations ---
    E_V_per_m = 10**((field_dBuV_m - 120) / 20)
    P_watts = (E_V_per_m**2 * 3**2) / 30
    P_watts[P_watts < 1e-15] = 1e-15
    P_dBm = 10 * np.log10(P_watts * 1000)

    P_linear = 10**(P_dBm / 10) / 1000
    avg_power_linear = np.mean(P_linear)
    P_iso_linear = 10**(iso_power_dBm / 10) / 1000

    efficiency = (avg_power_linear / P_iso_linear) * 100 if P_iso_linear > 0 else 0
    max_dBm = np.max(P_dBm)
    min_dBm = np.min(P_dBm)
    avg_dBm = 10 * np.log10(avg_power_linear * 1000)
    range_dB = max_dBm - min_dBm
    eff_dB = 10 * np.log10(efficiency / 100) if efficiency > 0 else -np.inf
    peak_angle = angles_deg[np.argmax(P_dBm)]
    hpbw = calculate_hpbw(angles_deg, P_dBm)

    return {
        "df": df,
        "angles_deg": angles_deg,
        "P_dBm": P_dBm,
        "stats": {
            'Max (dBm)': max_dBm,
            'Min (dBm)': min_dBm,
            'Avg (dBm)': avg_dBm,
            'Range (dB)': range_dB,
            'Peak Angle (°)': peak_angle,
            'HPBW (°)': hpbw,
            'Efficiency (%)': efficiency,
            'Efficiency (dB)': eff_dB,
        }
    }


@st.cache_data
def load_and_process_data(_uploaded_files, iso_power_dBm):
    """
    Load uploaded CSV files and process them into a dictionary of datasets.
    
    Note: The underscore prefix in _uploaded_files tells Streamlit not to hash this parameter,
    which is necessary because our UploadedFileFromURL objects cannot be hashed by Streamlit's caching system.
    """
    data_dict = {}
    skipped_files = []

    for uploaded_file in _uploaded_files:
        filename = uploaded_file.name
        if filename.endswith('_processed.csv'):
            try:
                # Reset buffer for reading
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file)
                if df.shape[1] >= 4:
                    base_name = filename.replace('_processed.csv', '')
                    var_name = base_name + '_totalField'
                    data_dict[var_name] = process_dataset(df, iso_power_dBm)
                else:
                    skipped_files.append({'file': filename, 'reason': f'Only {df.shape[1]} column(s) found (need ≥4)', 'type': 'warning'})
            except pd.errors.EmptyDataError:
                skipped_files.append({'file': filename, 'reason': 'File is empty', 'type': 'error'})
            except Exception as e:
                skipped_files.append({'file': filename, 'reason': f'Error: {str(e)}', 'type': 'error'})
        else:
            skipped_files.append({'file': filename, 'reason': 'Does not end with "_processed.csv"', 'type': 'warning'})

    return data_dict, skipped_files


# --- Plotting and UI Functions ---

def create_polar_plot(data_dict, selected_vars, plot_title, figsize, line_width, show_legend):
    """
    Create a polar plot of antenna radiation patterns from pre-processed data.
    """
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=figsize, dpi=100)
    fig.subplots_adjust(right=0.75)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    colors = plt.cm.jet(np.linspace(0, 1, len(selected_vars)))
    legend_entries = []
    all_P_dBm = []

    for i, var_name in enumerate(selected_vars):
        dataset = data_dict[var_name]
        angles_deg = dataset["angles_deg"]
        P_dBm = dataset["P_dBm"]

        theta = np.deg2rad(angles_deg)
        theta = np.append(theta, theta[0])
        P_dBm_plot = np.append(P_dBm, P_dBm[0])

        ax.plot(theta, P_dBm_plot, label=var_name, linewidth=line_width, color=colors[i])

        if show_legend:
            stats = dataset["stats"]
            legend_entries.append(
                f"{var_name}\nmax→{stats['Max (dBm)']:.1f} dBm, min→{stats['Min (dBm)']:.1f} dBm"
                f"\navg→{stats['Avg (dBm)']:.1f} dBm\neff→{stats['Efficiency (%)']:.1f}% ({stats['Efficiency (dB)']:.1f} dB)"
            )
        
        all_P_dBm.extend(P_dBm)

    if all_P_dBm:
        ax.set_rlim([np.floor(np.min(all_P_dBm)) - 5, np.ceil(np.max(all_P_dBm)) + 5])
    else:
        ax.set_rlim([-10, 10])

    ax.set_title(plot_title, pad=20)

    if show_legend and legend_entries:
        lgd = ax.legend(legend_entries, loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=8)
        plt.setp(lgd.get_texts(), linespacing=1.2)

    return fig


def fig_to_bytes(fig, dpi=300, format='png'):
    """Convert matplotlib figure to bytes for download."""
    buf = io.BytesIO()
    fig.savefig(buf, format=format, dpi=dpi, bbox_inches='tight')
    buf.seek(0)
    return buf.getvalue()

def df_to_csv(df):
    """Convert DataFrame to CSV bytes for download."""
    return df.to_csv(index=False).encode('utf-8')


def main():
    st.set_page_config(page_title="Antenna Radiation Pattern Visualizer", page_icon="📡", layout="wide")

    st.title("📡 Antenna Radiation Pattern Visualizer")
    st.markdown("Upload processed CSV files to visualize antenna radiation patterns and analyze performance metrics.")

    # --- Sidebar ---
    with st.sidebar:
        st.header("📂 Data Upload")
        uploaded_files = st.file_uploader("Upload processed CSV files", type=['csv'], accept_multiple_files=True)
        
        # URL-based file loading
        with st.expander("🔗 Or Load from URLs"):
            st.markdown("""
            **Paste URLs to CSV files** (one per line)
            
            Supported services:
            - Google Drive share links
            - Dropbox public links  
            - OneDrive share links
            - Direct HTTP/HTTPS URLs to CSV files
            
            **Example:**
            ```
            https://drive.google.com/file/d/FILE_ID/view
            https://www.dropbox.com/s/FILE_PATH?dl=0
            https://example.com/data.csv
            ```
            """)
            
            url_input = st.text_area(
                "URLs (one per line)",
                height=150,
                placeholder="https://drive.google.com/file/d/YOUR_FILE_ID/view\nhttps://www.dropbox.com/s/YOUR_FILE?dl=0"
            )
            
            load_urls_button = st.button("📥 Load Files", type="primary")
        
        # Process URL downloads
        url_files = []
        if load_urls_button and url_input:
            urls = [url.strip() for url in url_input.split('\n') if url.strip()]
            
            if urls:
                with st.spinner(f"Downloading {len(urls)} file(s)..."):
                    success_count = 0
                    error_messages = []
                    
                    for url in urls:
                        # Basic URL validation
                        if not url.startswith(('http://', 'https://')):
                            error_messages.append(f"⚠️ Invalid URL format: {url[:50]}...")
                            continue
                        
                        content, filename, error = download_file_from_url(url)
                        
                        if error:
                            error_messages.append(f"❌ {url[:50]}...: {error}")
                        elif content and filename:
                            url_files.append(UploadedFileFromURL(content, filename))
                            success_count += 1
                    
                    # Display results
                    if success_count > 0:
                        st.success(f"✅ Successfully loaded {success_count} file(s)")
                        with st.expander("📄 Loaded files", expanded=False):
                            for f in url_files:
                                st.write(f"• {f.name}")
                    
                    if error_messages:
                        with st.expander(f"⚠️ {len(error_messages)} error(s)", expanded=True):
                            for msg in error_messages:
                                st.error(msg)

        st.markdown("---")
        st.header("⚙️ Global Parameters")
        iso_power = st.number_input("Isotropic Power (dBm)", value=0.0, step=0.1, format="%.1f", help="Reference isotropic power for efficiency calculation.")
        
        st.markdown("---")
        st.header("🎨 Plot Customization")
        plot_title = st.text_input("Plot Title", value="Antenna Radiation Pattern")
        line_width = st.slider("Line Width", min_value=0.5, max_value=5.0, value=1.5, step=0.5)
        show_legend = st.toggle("Show Detailed Legend", value=True)

        st.markdown("---")
        st.header("📏 Figure Size")
        col1, col2 = st.columns(2)
        fig_width = col1.slider("Width (inches)", 8, 20, 14, 1)
        fig_height = col2.slider("Height (inches)", 6, 16, 10, 1)

    # --- Main Content Area ---
    # Combine uploaded files and URL files
    all_files = list(uploaded_files) if uploaded_files else []
    all_files.extend(url_files)
    
    if not all_files:
        st.info("👈 Please upload processed CSV files using the sidebar or load from URLs to get started.")
        st.markdown("""
        ### How to Use
        1. **Upload Files**: Use the sidebar to upload one or more `_processed.csv` files.
        2. **Or Load from URLs**: Expand the URL loader and paste links to publicly accessible CSV files.
        3. **Set Parameters**: Adjust isotropic power and customize the plot.
        4. **Select Datasets**: Choose which files to visualize from the dropdown.
        5. **Analyze**: View the interactive plot and detailed statistics in their respective tabs.
        6. **Download**: Save the plot image or statistics table for your reports.
        """)
        return

    data_dict, skipped_files = load_and_process_data(tuple(all_files), iso_power)

    if skipped_files:
        with st.expander(f"⚠️ Skipped {len(skipped_files)} file(s)", expanded=False):
            for item in skipped_files:
                st.warning(f"**{item['file']}**: {item['reason']}")

    if not data_dict:
        st.error("No valid data could be processed. Please check your files and try again.")
        return

    st.success(f"✅ Loaded and processed {len(data_dict)} dataset(s).")

    st.header("📊 Select Datasets to Plot")
    selected_vars = st.multiselect("Choose one or more datasets", options=list(data_dict.keys()), default=list(data_dict.keys()))

    if not selected_vars:
        st.info("👆 Please select at least one dataset to plot.")
        return

    # --- Tabs for Plot and Stats ---
    tab1, tab2 = st.tabs(["📈 Plot", "📋 Statistics Summary"])

    with tab1:
        st.header("Radiation Pattern Plot")
        with st.spinner("Generating plot..."):
            try:
                fig = create_polar_plot(data_dict, selected_vars, plot_title, (fig_width, fig_height), line_width, show_legend)
                
                plot_as_bytes = fig_to_bytes(fig, dpi=fig.dpi)
                st.image(plot_as_bytes, use_container_width=False)

                # Download Buttons
                col_dl1, col_dl2 = st.columns(2)
                png_bytes = fig_to_bytes(fig, dpi=300, format='png')
                col_dl1.download_button("💾 Download as PNG (High-Res)", png_bytes, f"{plot_title.replace(' ', '_')}.png", "image/png")
                
                jpg_bytes = fig_to_bytes(fig, dpi=300, format='jpg')
                col_dl2.download_button("💾 Download as JPG", jpg_bytes, f"{plot_title.replace(' ', '_')}.jpg", "image/jpeg")

                plt.close(fig)

            except Exception as e:
                st.error(f"Error generating plot: {e}")

    with tab2:
        st.header("Statistics Summary")
        
        stats_list = []
        for var_name in selected_vars:
            stats = data_dict[var_name]["stats"]
            stats['Dataset'] = var_name
            stats_list.append(stats)
        
        stats_df = pd.DataFrame(stats_list)
        
        # Reorder columns
        cols = ['Dataset', 'Max (dBm)', 'Min (dBm)', 'Avg (dBm)', 'Range (dB)', 'Peak Angle (°)', 'HPBW (°)', 'Efficiency (%)', 'Efficiency (dB)']
        stats_df = stats_df[cols]

        st.dataframe(stats_df,
            column_config={
                'Max (dBm)': st.column_config.NumberColumn(format='%.2f'),
                'Min (dBm)': st.column_config.NumberColumn(format='%.2f'),
                'Avg (dBm)': st.column_config.NumberColumn(format='%.2f'),
                'Range (dB)': st.column_config.NumberColumn(format='%.2f'),
                'Peak Angle (°)': st.column_config.NumberColumn(format='%d°'),
                'HPBW (°)': st.column_config.NumberColumn(format='%d°'),
                'Efficiency (%)': st.column_config.NumberColumn(format='%.2f%%'),
                'Efficiency (dB)': st.column_config.NumberColumn(format='%.2f'),
            },
            hide_index=True,
            use_container_width=True
        )

        csv_bytes = df_to_csv(stats_df)
        st.download_button(
            label="💾 Download as CSV",
            data=csv_bytes,
            file_name="antenna_statistics.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
