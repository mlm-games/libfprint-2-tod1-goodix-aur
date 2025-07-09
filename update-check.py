#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import sys

LAUNCHPAD_URL = "https://launchpad.net/~libfprint-tod1-group/+archive/ubuntu/ppa/+packages"
PACKAGE_NAME = "libfprint-2-tod1-goodix"

def get_latest_version():
    """Scrape the latest version from Launchpad"""
    response = requests.get(LAUNCHPAD_URL)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for the package in the table
    for row in soup.find_all('tr'):
        if PACKAGE_NAME in str(row):
            # Extract version from the row
            version_match = re.search(rf'{PACKAGE_NAME}\s+(\d+\.\d+\.\d+\+\d+-\d+ubuntu\d+)', str(row))
            if version_match:
                return version_match.group(1)
    
    return None

def get_current_version():
    """Get current version from local PKGBUILD or AUR"""
    try:
        # Try to get from AUR first
        aur_response = requests.get(f"https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h={PACKAGE_NAME}")
        if aur_response.status_code == 200:
            pkgver_match = re.search(r'pkgver=(.+)', aur_response.text)
            if pkgver_match:
                return f"{pkgver_match.group(1)}-0ubuntu1"
    except:
        pass
    
    # Fallback to local PKGBUILD
    try:
        with open('PKGBUILD', 'r') as f:
            content = f.read()
            pkgver_match = re.search(r'pkgver=(.+)', content)
            if pkgver_match:
                return f"{pkgver_match.group(1)}-0ubuntu1"
    except FileNotFoundError:
        pass
    
    return None

def main():
    latest = get_latest_version()
    current = get_current_version()
    
    if not latest:
        print("Could not fetch latest version")
        sys.exit(1)
    
    print(f"Current version: {current}")
    print(f"Latest version: {latest}")
    
    if current != latest:
        print("New version available!")
    else:
        print("Already up to date")

if __name__ == "__main__":
    main()
