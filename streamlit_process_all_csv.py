"""
Streamlit CSV Antenna Sweep Data Processor

This is a Streamlit web application for processing antenna measurement CSV files
containing two sweep datasets representing electric field strength (in dBµV/m) versus angle.

Key Functionality:
- Web-based interface for uploading CSV files.
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
- Upload CSV files through the web interface.
- Download processed results.

Dependencies:
- streamlit, numpy, pandas, scipy
"""

import io
import zipfile
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import streamlit as st


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
                               kind='linear', fill_value='extrapolate')
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

    # Initialize session state for results
    if 'results' not in st.session_state:
        st.session_state.results = None

    # File uploader
    uploaded_files = st.file_uploader(
        "Choose CSV files",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload one or more CSV files with antenna sweep data"
    )

    if uploaded_files:
        st.write(f"### Uploaded {len(uploaded_files)} file(s)")

        # Process button
        if st.button("Process All Files", type="primary"):
            results = {}

            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, uploaded_file in enumerate(uploaded_files):
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
                progress_bar.progress((idx + 1) / len(uploaded_files))

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

            col1, col2, col3 = st.columns(3)
            col1.metric("Successfully Processed", success_count)
            col2.metric("Failed", fail_count)

            # Download All button
            if success_count > 0:
                with col3:
                    zip_data = create_zip_archive(results)
                    st.download_button(
                        label=f"📦 Download All ({success_count} files)",
                        data=zip_data,
                        file_name="processed_files.zip",
                        mime="application/zip",
                        type="primary"
                    )

            # Show details for each file
            for filename, result in results.items():
                with st.expander(f"{'✅' if result['success'] else '❌'} {filename}"):
                    if result['success']:
                        st.success(result['message'])

                        # Display preview
                        st.write("**Preview:**")
                        st.dataframe(result['data'].head(10), width='stretch')

                        # Download button
                        csv_buffer = io.StringIO()
                        result['data'].to_csv(csv_buffer, index=False)
                        csv_bytes = csv_buffer.getvalue().encode()

                        output_filename = filename.replace('.csv', '_processed.csv')
                        st.download_button(
                            label=f"Download {output_filename}",
                            data=csv_bytes,
                            file_name=output_filename,
                            mime='text/csv',
                            key=f"download_{filename}"
                        )
                    else:
                        st.error(f"Error: {result['message']}")

    # Sidebar with information
    with st.sidebar:
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
        """)


if __name__ == "__main__":
    main()
