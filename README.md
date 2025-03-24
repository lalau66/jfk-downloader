Special-purpose downloader to download the files exposed at https://www.archives.gov/research/jfk/release-2025 
"""
JFK Archives 2025 Release PDF Downloader
=======================================

This script downloads all PDF documents from the JFK Archives 2025 release
by extracting all links from the index page and downloading them.

Features:
- Extracts all PDF links from the index page
- Downloads all PDF documents while preserving filenames
- Creates date-based folder structure
- Shows download progress

Usage:
    python jfk_pdf_downloader.py

Requirements:
- Python 3.6+ (Python 3.11.3 or higher recommended) 
- jfk-requirements.txt sets out full list of dependencies (to be installed in your env or venv) 

Author: lalau66@GitHub
License: MIT
Date: March 24, 2025

