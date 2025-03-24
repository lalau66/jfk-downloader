#!/usr/bin/env python3
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
    - Python 3.6+
    - requests
    - beautifulsoup4

Author: Custom script for JFK Archives document collection
License: MIT
Date: March 24, 2025
"""

import os
import re
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import argparse

class JFKPDFDownloader:
    def __init__(self, base_url=None, download_folder="jfk_2025_release", max_workers=5):
        self.base_url = base_url or "https://www.archives.gov/research/jfk/release-2025"
        self.download_folder = download_folder
        self.max_workers = max_workers
        self.total_downloaded = 0
        self.total_failed = 0
        self.downloaded_files = set()
        
        # Headers to simulate a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        # Create download directory if it doesn't exist
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
    
    def download_pdf(self, pdf_url):
        """Download a PDF file from the given URL"""
        try:
            # Extract filename from URL
            filename = os.path.basename(pdf_url)
            
            # Create subfolder structure based on URL path
            parsed_url = urlparse(pdf_url)
            path_parts = parsed_url.path.split('/')
            
            # Extract the date part from the URL (e.g., '0318')
            date_folder = None
            for part in path_parts:
                if re.match(r'^\d{4}$', part):
                    date_folder = part
                    break
            
            if date_folder:
                subfolder = os.path.join(self.download_folder, date_folder)
                if not os.path.exists(subfolder):
                    os.makedirs(subfolder)
            else:
                subfolder = self.download_folder
            
            # Full path to save the file
            file_path = os.path.join(subfolder, filename)
            
            # Skip if file already exists
            if os.path.exists(file_path):
                print(f"Skipping (already exists): {filename}")
                return True
            
            # Skip if already downloaded in this session
            if pdf_url in self.downloaded_files:
                return True
                
            # Download the file
            response = requests.get(pdf_url, headers=self.headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"Downloaded: {filename}")
                self.total_downloaded += 1
                self.downloaded_files.add(pdf_url)
                return True
            else:
                print(f"Failed to download {filename}: HTTP {response.status_code}")
                self.total_failed += 1
                return False
                
        except Exception as e:
            print(f"Error downloading {pdf_url}: {str(e)}")
            self.total_failed += 1
            return False

    def extract_all_pdf_links(self, page_url):
        """Extract all PDF links from the index page"""
        pdf_links = []
        
        try:
            print(f"Fetching page: {page_url}")
            response = requests.get(page_url, headers=self.headers, timeout=30)
            if response.status_code != 200:
                print(f"Failed to fetch page {page_url}: HTTP {response.status_code}")
                return pdf_links
            
            print(f"Page size: {len(response.text)} bytes")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for all PDF links on the page
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                
                # Make sure it's a PDF link
                if '.pdf' in href:
                    # Convert relative URL to absolute
                    if not href.startswith('http'):
                        pdf_url = urljoin(page_url, href)
                    else:
                        pdf_url = href
                    
                    # Ensure URL points to archives.gov domain
                    if 'archives.gov' in pdf_url:
                        pdf_links.append(pdf_url)
            
            print(f"Found {len(pdf_links)} PDF links")
            
            # If no links found, try checking for iframes
            if not pdf_links:
                print("No PDF links found directly. Checking for iframes...")
                
                for iframe in soup.find_all('iframe', src=True):
                    iframe_src = iframe.get('src')
                    if not iframe_src.startswith('http'):
                        iframe_url = urljoin(page_url, iframe_src)
                    else:
                        iframe_url = iframe_src
                    
                    print(f"Checking iframe: {iframe_url}")
                    
                    try:
                        iframe_response = requests.get(iframe_url, headers=self.headers, timeout=30)
                        if iframe_response.status_code == 200:
                            iframe_soup = BeautifulSoup(iframe_response.text, 'html.parser')
                            
                            for iframe_link in iframe_soup.find_all('a', href=True):
                                iframe_href = iframe_link.get('href')
                                
                                if '.pdf' in iframe_href:
                                    if not iframe_href.startswith('http'):
                                        pdf_url = urljoin(iframe_url, iframe_href)
                                    else:
                                        pdf_url = iframe_href
                                    
                                    if 'archives.gov' in pdf_url:
                                        pdf_links.append(pdf_url)
                            
                            print(f"Found {len(pdf_links)} PDF links in iframe")
                            
                    except Exception as e:
                        print(f"Error checking iframe: {str(e)}")
            
            return pdf_links
            
        except Exception as e:
            print(f"Error extracting PDF links: {str(e)}")
            return pdf_links

    def run(self):
        """Main method to download all PDF files"""
        print(f"Starting JFK Archives 2025 Release PDF Downloader")
        print(f"Base URL: {self.base_url}")
        print(f"Files will be saved to: {os.path.abspath(self.download_folder)}")
        
        # Get all PDF links from the index page
        pdf_links = self.extract_all_pdf_links(self.base_url)
        
        if not pdf_links:
            print("No PDF links found. The page structure might have changed.")
            return
        
        # Download all PDFs using thread pool
        print(f"Starting download of {len(pdf_links)} PDF files...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.download_pdf, pdf_links)
        
        print(f"\nDownload complete!")
        print(f"Total PDF files downloaded: {self.total_downloaded}")
        print(f"Total failed downloads: {self.total_failed}")

def main():
    parser = argparse.ArgumentParser(description='Download PDF files from JFK Archives 2025 Release')
    parser.add_argument('--folder', type=str, default='jfk_2025_release', 
                        help='Folder to save downloaded files (default: jfk_2025_release)')
    parser.add_argument('--workers', type=int, default=5, 
                        help='Number of parallel downloads (default: 5)')
    args = parser.parse_args()
    
    downloader = JFKPDFDownloader(download_folder=args.folder, max_workers=args.workers)
    downloader.run()

if __name__ == "__main__":
    main()