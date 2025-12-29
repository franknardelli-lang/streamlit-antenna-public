"""
Streamlit CSV Antenna Sweep Data Processor

This is a Streamlit web application for processing antenna measurement CSV files
containing two sweep datasets representing electric field strength (in dBµV/m) versus angle.

Key Functionality:
- Web-based interface for uploading CSV files or loading from URLs.
- Processes multiple CSV files at once.
- Reads each CSV file assuming at least two columns: angle and field strength.
- Detects the "sweep break" where the angle data resets (angle decreases).
- Splits data into two sweeps based on this break.
- Cleans repeated rows at the start of the second sweep (up to 5 duplicates).
- Averages duplicate angle entries in the second sweep to align data.
- Interpolates the second sweep's field values onto the first sweep's angle points.
- Converts field strengths from dBµV/m to linear V/m scale.
- Combines the two sweeps using a Pythagorean sum of the field strengths.
- Converts the combined field strength back to dBµV/m.
- Allows download of processed data.

Usage:
- Run: streamlit run streamlit_process_all_csv.py
- Upload CSV files through the web interface or load from URLs.
- Download processed results.

Dependencies:
- streamlit, numpy, pandas, scipy, requests
"""

import io
import re
import zipfile
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import streamlit as st
import requests
from urllib.parse import urlparse


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


def download_and_extract_zip(zip_url, timeout=30):
    """
    Download a ZIP file from a URL and extract all CSV files.
    
    Args:
        zip_url: URL to the ZIP file
        timeout: Request timeout in seconds
        
    Returns:
        tuple: (list of UploadedFileFromURL objects, error message or None)
    """
    try:
        # Download the ZIP file
        content, filename, error = download_file_from_url(zip_url, timeout)
        
        if error:
            return [], error
        
        if not content:
            return [], "Failed to download ZIP file"
        
        # Extract CSV files from ZIP
        extracted_files = []
        
        try:
            with zipfile.ZipFile(content, 'r') as zip_ref:
                # Get list of all files in the ZIP
                file_list = zip_ref.namelist()
                
                # Filter for CSV files (excluding __MACOSX/)
                csv_files = [f for f in file_list if f.endswith('.csv') and not f.startswith('__MACOSX/')]
                
                if not csv_files:
                    return [], "No CSV files found in ZIP"
                
                # Extract each CSV file
                for csv_filename in csv_files:
                    try:
                        file_data = zip_ref.read(csv_filename)
                        file_obj = io.BytesIO(file_data)
                        
                        # Get just the filename without path
                        name_only = csv_filename.split('/')[-1]
                        
                        # Create UploadedFileFromURL wrapper
                        uploaded_file = UploadedFileFromURL(file_obj, name_only)
                        extracted_files.append(uploaded_file)
                    except Exception as e:
                        # Skip files that can't be extracted
                        continue
                
                if not extracted_files:
                    return [], "No valid CSV files could be extracted from ZIP"
                
                return extracted_files, None
                
        except zipfile.BadZipFile:
            return [], "Invalid ZIP file format"
        except Exception as e:
            return [], f"Error extracting ZIP: {str(e)}"
    
    except Exception as e:
        return [], f"Unexpected error: {str(e)}"


def process_csv_data(df, filename):
    """
    Process a single CSV dataframe containing antenna sweep data.

    Args:
        df: pandas DataFrame with at least 2 columns (angle, field strength)
        filename: name of the file being processed

    Returns:
        tuple: (processed_df, success, message)
    """
    try:
        if df.shape[1] < 2:
            return None, False, 'Fewer than 2 columns'

        angles = df.iloc[:, 0].values
        f1_dBuV_m = df.iloc[:, 1].values

        # Find sweep break where angle decreases
        d = np.diff(angles)
        brk_indices = np.where(d < 0)[0]
        if len(brk_indices) == 0:
            return None, False, 'No clear sweep break found'
        brk = brk_indices[0]

        ang1 = angles[:brk+1]
        f1 = f1_dBuV_m[:brk+1]
        ang2 = angles[brk+1:]
        f2_dBuV_m = f1_dBuV_m[brk+1:]

        # Clean repeated leading rows in sweep 2 (up to 5)
        keep = np.ones(len(ang2), dtype=bool)
        for k in range(1, min(5, len(ang2))):
            if ang2[k] == ang2[k-1] and f2_dBuV_m[k] == f2_dBuV_m[k-1]:
                keep[k] = False
        ang2 = ang2[keep]
        f2_dBuV_m = f2_dBuV_m[keep]

        # Align sweeps by averaging duplicates in sweep 2
        df2 = pd.DataFrame({'angle': ang2, 'field': f2_dBuV_m})
        df2_mean = df2.groupby('angle').mean().reset_index()

        # Interpolate sweep 2 onto sweep 1 angles
        interp_func = interp1d(df2_mean['angle'], df2_mean['field'],
                               kind='linear', fill_value='extrapolate')  # type: ignore[arg-type]
        f2_on_1 = interp_func(ang1)

        # Convert dBµV/m to V/m
        f1_V_per_m = 10 ** ((f1 - 120) / 20)
        f2_V_per_m = 10 ** ((f2_on_1 - 120) / 20)

        # Pythagorean sum
        total_V_per_m = np.sqrt(f1_V_per_m**2 + f2_V_per_m**2)

        # Convert back to dBµV/m
        total_dBuV_m = 20 * np.log10(total_V_per_m) + 120

        # Create output dataframe
        out_df = pd.DataFrame({
            'Angle': ang1,
            'Field1': f1,
            'Field2': f2_on_1,
            'TotalField': total_dBuV_m
        })

        return out_df, True, 'Success'

    except Exception as e:
        return None, False, str(e)


def create_zip_archive(results):
    """
    Create a ZIP file containing all successfully processed CSV files.

    Args:
        results: Dictionary of processing results

    Returns:
        bytes: ZIP file contents
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, result in results.items():
            if result['success'] and result['data'] is not None:
                # Convert DataFrame to CSV string
                csv_buffer = io.StringIO()
                result['data'].to_csv(csv_buffer, index=False)
                csv_string = csv_buffer.getvalue()

                # Add to ZIP with processed filename
                output_filename = filename.replace('.csv', '_processed.csv')
                zip_file.writestr(output_filename, csv_string)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def upload_to_litterbox(data_bytes, filename):
    """
    Upload file bytes to litterbox.catbox.moe and return a shareable link.
    Files are kept for 72 hours.

    Args:
        data_bytes: File content as bytes
        filename: Name for the file

    Returns:
        tuple: (url string or None, error message or None)
    """
    try:
        # Litterbox API endpoint
        url = 'https://litterbox.catbox.moe/resources/internals/api.php'

        # Prepare the multipart form data
        files = {
            'fileToUpload': (filename, data_bytes, 'application/octet-stream')
        }

        data = {
            'reqtype': 'fileupload',
            'time': '72h'  # Available options: 1h, 12h, 24h, 72h
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.post(url, files=files, data=data, headers=headers, timeout=60)
        response.raise_for_status()

        # Litterbox returns the download URL as plain text
        download_url = response.text.strip()

        # Validate the response
        if download_url and download_url.startswith('https://'):
            return download_url, None
        else:
            return None, f"Invalid response from litterbox: {response.text[:200]}"

    except requests.exceptions.Timeout:
        return None, "Upload timeout: Server took too long to respond (>60 seconds)"
    except requests.exceptions.ConnectionError:
        return None, "Connection error: Could not connect to litterbox.catbox.moe service"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 413:
            return None, "File too large: litterbox has a 1GB limit"
        elif e.response.status_code == 429:
            return None, "Rate limit exceeded: Please wait a few minutes before trying again"
        else:
            return None, f"HTTP error {e.response.status_code}: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def main():
    st.set_page_config(
        page_title="CSV Antenna Sweep Processor",
        page_icon="📡",
        layout="wide"
    )

    st.title("📡 CSV Antenna Sweep Data Processor")
    st.markdown("""
    Upload CSV files containing antenna measurement data with two sweep datasets.
    The app will process the data and provide downloadable results.
    """)

    # Initialize session state for results and files
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'url_files' not in st.session_state:
        st.session_state.url_files = []
    if 'zip_files' not in st.session_state:
        st.session_state.zip_files = []

    # Sidebar with file loading options
    with st.sidebar:
        st.header("📁 File Loading")
        
        # URL-based file loading
        with st.expander("🔗 Load from URLs"):
            st.markdown("""
            **Paste URLs to raw/unprocessed CSV files** (one per line)
            
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
            
            load_urls_button = st.button("📥 Load Files from URLs", type="primary")
        
        # ZIP URL loading
        with st.expander("📦 Load CSV files from ZIP"):
            st.markdown("""
            **Paste URL to a ZIP file containing raw/unprocessed CSV files**
            
            The app will:
            - Download the ZIP file
            - Extract all CSV files
            - Make them available for processing
            
            **Example:**
            ```
            https://example.com/data.zip
            https://drive.google.com/file/d/FILE_ID/view
            ```
            """)
            
            zip_url_input = st.text_input(
                "ZIP File URL",
                placeholder="https://example.com/antenna_data.zip"
            )

            load_zip_button = st.button("📥 Load ZIP File", type="primary")

        # File uploader
        uploaded_files = st.file_uploader(
            "Choose CSV files",
            type=['csv'],
            accept_multiple_files=True,
            help="Upload one or more CSV files with antenna sweep data"
        )

    # Process URL downloads
    if load_urls_button and url_input:
        urls = [url.strip() for url in url_input.split('\n') if url.strip()]

        if urls:
            with st.spinner(f"Downloading {len(urls)} file(s)..."):
                success_count = 0
                error_messages = []
                url_files_temp = []

                for url in urls:
                    # Basic URL validation
                    if not url.startswith(('http://', 'https://')):
                        error_messages.append(f"⚠️ Invalid URL format: {url[:50]}...")
                        continue

                    content, filename, error = download_file_from_url(url)

                    if error:
                        error_messages.append(f"❌ {url[:50]}...: {error}")
                    elif content and filename:
                        url_files_temp.append(UploadedFileFromURL(content, filename))
                        success_count += 1

                # Store in session state
                if success_count > 0:
                    st.session_state.url_files = url_files_temp
                    st.success(f"✅ Successfully loaded {success_count} file(s)")
                    with st.expander("📄 Loaded files", expanded=False):
                        for f in st.session_state.url_files:
                            st.write(f"• {f.name}")

                if error_messages:
                    with st.expander(f"⚠️ {len(error_messages)} error(s)", expanded=True):
                        for msg in error_messages:
                            st.error(msg)

    # Process ZIP downloads
    if load_zip_button and zip_url_input:
        with st.spinner("Downloading and extracting ZIP file..."):
            extracted_files, error = download_and_extract_zip(zip_url_input)

            if error:
                st.error(f"❌ Failed to load ZIP: {error}")
            elif extracted_files:
                # Store in session state
                st.session_state.zip_files = extracted_files
                st.success(f"✅ Successfully extracted {len(extracted_files)} CSV file(s) from ZIP")
                with st.expander("📄 Extracted files", expanded=False):
                    for f in st.session_state.zip_files:
                        st.write(f"• {f.name}")

    # Get files from session state
    url_files = st.session_state.url_files
    zip_files = st.session_state.zip_files

    # Combine uploaded files, URL files, and ZIP files
    all_files = list(uploaded_files) if uploaded_files else []
    all_files.extend(url_files)
    all_files.extend(zip_files)

    if all_files:
        st.write(f"### Loaded {len(all_files)} file(s) total")

        # Process button
        if st.button("Process All Files", type="primary"):
            results = {}

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, uploaded_file in enumerate(all_files):
                status_text.text(f"Processing {uploaded_file.name}...")

                # Read the CSV
                df = pd.read_csv(uploaded_file)

                # Process the data
                processed_df, success, message = process_csv_data(df, uploaded_file.name)

                results[uploaded_file.name] = {
                    'success': success,
                    'message': message,
                    'data': processed_df
                }

                # Update progress
                progress_bar.progress((idx + 1) / len(all_files))

            status_text.text("Processing complete!")

            # Store results in session state
            st.session_state.results = results

        # Display results if they exist
        if st.session_state.results:
            results = st.session_state.results

            # Display results
            st.write("### Processing Results")

            success_count = sum(1 for r in results.values() if r['success'])
            fail_count = len(results) - success_count

            col1, col2 = st.columns(2)
            col1.metric("Successfully Processed", success_count)
            col2.metric("Failed", fail_count)

            # Download All and Share All buttons
            if success_count > 0:
                zip_data = create_zip_archive(results)

                col_btn1, col_btn2 = st.columns(2)

                with col_btn1:
                    st.download_button(
                        label=f"📦 Download All ({success_count} files)",
                        data=zip_data,
                        file_name="processed_files.zip",
                        mime="application/zip",
                        type="primary"
                    )

                with col_btn2:
                    if st.button(
                        f"🔗 Generate Shareable Link for All ({success_count} files)",
                        key="share_all",
                        help="Upload ZIP file to litterbox.catbox.moe and get a shareable download link"
                    ):
                        with st.spinner("Uploading ZIP file to litterbox.catbox.moe..."):
                            share_url, error = upload_to_litterbox(zip_data, "processed_files.zip")

                        if share_url:
                            st.success("✅ ZIP upload successful!")
                            st.text_input(
                                "Shareable Link for ZIP (copy this URL):",
                                value=share_url,
                                key="url_all",
                                help="Copy this URL to share the ZIP file"
                            )
                            st.warning("⚠️ This link expires after 72 hours")
                            st.info("💡 Open this URL in your browser to download the ZIP file with all processed files")
                        else:
                            st.error(f"❌ ZIP upload failed: {error}")

            # Show details for each file
            for filename, result in results.items():
                with st.expander(f"{'✅' if result['success'] else '❌'} {filename}"):
                    if result['success']:
                        st.success(result['message'])

                        # Display preview
                        st.write("**Preview:**")
                        st.dataframe(result['data'].head(10), width='stretch')

                        # Download button and shareable link button
                        csv_buffer = io.StringIO()
                        result['data'].to_csv(csv_buffer, index=False)
                        csv_bytes = csv_buffer.getvalue().encode()

                        output_filename = filename.replace('.csv', '_processed.csv')
                        
                        # Create two columns for buttons
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label=f"📥 Download {output_filename}",
                                data=csv_bytes,
                                file_name=output_filename,
                                mime='text/csv',
                                key=f"download_{filename}"
                            )
                        
                        with col2:
                            if st.button(
                                "🔗 Generate Shareable Link",
                                key=f"share_{filename}",
                                help="Upload to litterbox.catbox.moe and get a shareable download link"
                            ):
                                with st.spinner("Uploading to litterbox.catbox.moe..."):
                                    share_url, error = upload_to_litterbox(csv_bytes, output_filename)

                                if share_url:
                                    st.success("✅ Upload successful!")
                                    st.text_input(
                                        "Shareable Link (copy this URL):",
                                        value=share_url,
                                        key=f"url_{filename}",
                                        help="Copy this URL to share the file"
                                    )
                                    st.warning("⚠️ This link expires after 72 hours")
                                    st.info("💡 Open this URL in your browser to download the file")
                                else:
                                    st.error(f"❌ Upload failed: {error}")
                    else:
                        st.error(f"Error: {result['message']}")

    # Sidebar with information
    with st.sidebar:
        st.markdown("---")
        st.header("ℹ️ About")
        st.markdown("""
        This tool processes antenna measurement CSV files by:

        1. Detecting sweep breaks
        2. Splitting data into two sweeps
        3. Cleaning duplicate rows
        4. Aligning data points
        5. Combining sweeps using Pythagorean sum
        6. Converting between dBµV/m and V/m

        **Input Format:**
        - CSV files with at least 2 columns
        - Column 1: Angle measurements
        - Column 2: Field strength (dBµV/m)

        **Output Format:**
        - Angle
        - Field1 (first sweep)
        - Field2 (second sweep, interpolated)
        - TotalField (combined)
        """)

        st.header("📊 Requirements")
        st.code("""
pandas
numpy
scipy
streamlit
requests
        """)


if __name__ == "__main__":
    main()
