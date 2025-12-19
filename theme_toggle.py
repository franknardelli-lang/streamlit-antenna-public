"""
Theme toggle component for dark/light mode switching
"""
import streamlit as st

def apply_theme_toggle():
    """
    Add a theme toggle to the sidebar and apply the selected theme.
    Uses session state to persist the theme choice across page navigation.
    """
    # Initialize theme in session state if not present
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'

    if 'dark_mode_enabled' not in st.session_state:
        st.session_state.dark_mode_enabled = False

    # Create toggle in sidebar
    with st.sidebar:
        st.markdown("---")
        dark_mode = st.toggle(
            "🌙 Dark Mode",
            value=st.session_state.dark_mode_enabled,
            help="Toggle between dark and light themes",
            key="dark_mode_toggle"
        )

        # Update theme based on toggle
        if dark_mode != st.session_state.dark_mode_enabled:
            st.session_state.dark_mode_enabled = dark_mode
            st.session_state.theme = 'dark' if dark_mode else 'light'
            st.rerun()

    # Apply custom CSS based on theme
    if st.session_state.theme == 'dark':
        # Dark theme CSS
        st.markdown("""
        <style>
        /* Dark theme - Force all text to be light colored */
        .stApp {
            background-color: #0e1117 !important;
            color: #fafafa !important;
        }

        /* Main content text - be very specific */
        .stMarkdown,
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown span,
        .stText,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stMarkdownContainer"] span,
        h1, h2, h3, h4, h5, h6,
        p, span, div, li, label {
            color: #fafafa !important;
        }

        /* Headers */
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3 {
            color: #ffffff !important;
        }

        /* Sidebar text */
        section[data-testid="stSidebar"] {
            background-color: #262730 !important;
            color: #fafafa !important;
        }

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div {
            color: #fafafa !important;
        }

        /* Info boxes and alerts */
        .stAlert,
        div[data-baseweb="notification"] {
            background-color: #1e3a5f !important;
            color: #fafafa !important;
        }

        .stAlert p,
        .stAlert span,
        div[data-baseweb="notification"] p,
        div[data-baseweb="notification"] span {
            color: #fafafa !important;
        }

        /* Code blocks */
        code {
            background-color: #262730 !important;
            color: #fafafa !important;
        }

        /* Widget labels */
        label {
            color: #fafafa !important;
        }

        /* Buttons */
        button {
            color: #262730 !important;
        }

        /* Success/Error/Warning messages */
        .stSuccess, .stError, .stWarning, .stInfo {
            color: #fafafa !important;
        }

        /* Dataframes */
        .stDataFrame {
            color: #262730 !important;
        }

        /* File uploader dropzone - keep text black for readability */
        section[data-testid="stFileUploadDropzone"],
        section[data-testid="stFileUploadDropzone"] label,
        section[data-testid="stFileUploadDropzone"] p,
        section[data-testid="stFileUploadDropzone"] span,
        section[data-testid="stFileUploadDropzone"] small,
        section[data-testid="stFileUploadDropzone"] div,
        div[data-testid="stFileUploader"] label,
        div[data-testid="stFileUploader"] p,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] small,
        div[data-testid="stFileUploader"] div {
            color: #262730 !important;
        }

        /* File uploader dropzone background and border - light background for contrast */
        section[data-testid="stFileUploadDropzone"] {
            background-color: #e8e8e8 !important;
            border: 2px dashed #525252 !important;
        }

        /* File uploader button - make sure browse button is visible */
        div[data-testid="stFileUploader"] button,
        div[data-testid="stFileUploader"] button span,
        section[data-testid="stFileUploadDropzone"] button,
        section[data-testid="stFileUploadDropzone"] button span {
            background-color: #FF4B4B !important;
            color: #ffffff !important;
            border: none !important;
        }

        /* Expander borders */
        div[data-testid="stExpander"] {
            border: 1px solid #525252 !important;
        }

        /* Text area */
        textarea {
            background-color: #262730 !important;
            color: #fafafa !important;
        }

        /* Text input */
        input {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light theme CSS
        st.markdown("""
        <style>
        /* Light theme - Force all text to be dark colored */
        .stApp {
            background-color: #ffffff !important;
            color: #262730 !important;
        }

        /* Main content text */
        .stMarkdown,
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown span,
        .stText,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stMarkdownContainer"] span,
        h1, h2, h3, h4, h5, h6,
        p, span, div, li, label {
            color: #262730 !important;
        }

        /* Headers */
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3 {
            color: #262730 !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #f0f2f6 !important;
            color: #262730 !important;
        }

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div {
            color: #262730 !important;
        }

        /* Code blocks */
        code {
            background-color: #f0f2f6 !important;
            color: #262730 !important;
        }

        /* Widget labels */
        label {
            color: #262730 !important;
        }

        /* File uploader dropzone - comprehensive text styling */
        section[data-testid="stFileUploadDropzone"],
        section[data-testid="stFileUploadDropzone"] label,
        section[data-testid="stFileUploadDropzone"] p,
        section[data-testid="stFileUploadDropzone"] span,
        section[data-testid="stFileUploadDropzone"] small,
        section[data-testid="stFileUploadDropzone"] div,
        div[data-testid="stFileUploader"] label,
        div[data-testid="stFileUploader"] p,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] small,
        div[data-testid="stFileUploader"] div {
            color: #262730 !important;
        }

        /* File uploader dropzone background and border */
        section[data-testid="stFileUploadDropzone"] {
            background-color: #ffffff !important;
            border: 2px dashed #d0d0d0 !important;
        }

        /* File uploader button */
        div[data-testid="stFileUploader"] button,
        div[data-testid="stFileUploader"] button span,
        section[data-testid="stFileUploadDropzone"] button,
        section[data-testid="stFileUploadDropzone"] button span {
            background-color: #FF4B4B !important;
            color: #ffffff !important;
            border: none !important;
        }

        /* Expander borders */
        div[data-testid="stExpander"] {
            border: 1px solid #d0d0d0 !important;
        }

        /* Text area and input */
        textarea,
        input {
            background-color: #ffffff !important;
            color: #262730 !important;
        }
        </style>
        """, unsafe_allow_html=True)
