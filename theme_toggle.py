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

        /* Buttons - primary buttons */
        button[data-testid="stBaseButton-primary"] {
            background-color: #FF4B4B !important;
            color: #ffffff !important;
        }

        /* Buttons - secondary buttons (the white ones) */
        button[data-testid="stBaseButton-secondary"],
        button[kind="secondary"] {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #525252 !important;
        }

        /* All other buttons */
        button {
            color: #fafafa !important;
        }

        /* Success/Error/Warning messages */
        .stSuccess, .stError, .stWarning, .stInfo {
            color: #fafafa !important;
        }

        /* Dataframes - light text on dark background */
        .stDataFrame,
        .stDataFrame div,
        .stDataFrame span,
        .stDataFrame td,
        .stDataFrame th,
        div[data-testid="stDataFrame"] div,
        div[data-testid="stDataFrame"] span,
        div[data-testid="stDataFrame"] td,
        div[data-testid="stDataFrame"] th {
            color: #fafafa !important;
            background-color: #262730 !important;
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

        /* Uploaded file list items - make them readable */
        div[data-testid="stFileUploaderFile"],
        div[data-testid="stFileUploaderFile"] div,
        div[data-testid="stFileUploaderFileName"],
        .stFileUploaderFile,
        .stFileUploaderFileName {
            background-color: #3d3d46 !important;
            color: #fafafa !important;
        }

        div[data-testid="stFileUploaderFile"] small {
            color: #b0b0b0 !important;
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

        /* Text input - be more specific */
        input[type="text"],
        input[type="url"],
        input[type="email"],
        input[type="number"],
        input {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #525252 !important;
        }

        /* Text input in stTextInput component */
        div[data-testid="stTextInput"] input,
        div[data-baseweb="input"] input {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #525252 !important;
        }

        /* Text input inside markdown containers (for st.text_input) */
        div[data-testid="stMarkdownContainer"] input,
        div[data-testid="stMarkdownContainer"] input[type="text"] {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #525252 !important;
        }

        /* Force all input elements with white background to dark - super specific */
        .stApp input[type="text"],
        .stApp input[type="url"],
        .stApp input[type="email"],
        .stApp input[type="number"],
        .stApp div input,
        input[style*="background-color: rgb(255, 255, 255)"],
        input[style*="background-color: white"] {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #525252 !important;
        }

        /* Number input step buttons (+ and -) */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"] {
            background-color: #3d3d46 !important;
            color: #fafafa !important;
            border: 1px solid #525252 !important;
        }

        button[data-testid="stNumberInputStepUp"]:hover,
        button[data-testid="stNumberInputStepDown"]:hover {
            background-color: #4d4d56 !important;
        }

        button[data-testid="stNumberInputStepUp"] svg,
        button[data-testid="stNumberInputStepDown"] svg {
            color: #fafafa !important;
        }

        /* Multiselect widget - comprehensive styling */
        div[data-baseweb="select"] {
            background-color: #262730 !important;
        }

        div[data-baseweb="select"] input {
            color: #fafafa !important;
        }

        /* Multiselect dropdown menu - all variations */
        ul[role="listbox"],
        div[data-baseweb="popover"] ul,
        div[data-baseweb="menu"] ul {
            background-color: #262730 !important;
        }

        ul[role="listbox"] li,
        div[data-baseweb="popover"] li,
        div[data-baseweb="menu"] li {
            color: #fafafa !important;
            background-color: #262730 !important;
        }

        ul[role="listbox"] li:hover,
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="menu"] li:hover {
            background-color: #3d3d46 !important;
            color: #ffffff !important;
        }

        /* Option text inside dropdown */
        ul[role="listbox"] li span,
        ul[role="listbox"] li div,
        div[data-baseweb="popover"] li span,
        div[data-baseweb="popover"] li div,
        div[data-baseweb="menu"] li span,
        div[data-baseweb="menu"] li div {
            color: #fafafa !important;
        }

        /* Multiselect selected items/tags */
        div[data-baseweb="tag"] {
            background-color: #FF4B4B !important;
            color: #ffffff !important;
        }

        div[data-baseweb="tag"] span {
            color: #ffffff !important;
        }

        /* Select/dropdown text - all spans */
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {
            color: #fafafa !important;
        }

        /* Popover container background */
        div[data-baseweb="popover"] {
            background-color: #262730 !important;
        }

        /* Menu items - comprehensive */
        [role="option"] {
            color: #fafafa !important;
            background-color: #262730 !important;
        }

        [role="option"]:hover {
            background-color: #3d3d46 !important;
        }

        [role="option"] span,
        [role="option"] div {
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
