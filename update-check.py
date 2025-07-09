#!/usr/bin/env python3
import requests
import re
import subprocess
import sys
from datetime import datetime

LAUNCHPAD_URL = "https://launchpad.net/~libfprint-tod1-group/+archive/ubuntu/ppa/+packages"
PACKAGE_NAME = "libfprint-2-tod1-goodix"

def get_latest_version():
    """Scrape the latest version from Launchpad"""
    response = requests.get(LAUNCHPAD_URL)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return None
    
    # Look for the package and version pattern
    pattern = rf'{PACKAGE_NAME}\s+(\d+\.\d+\.\d+\+\d+-\d+ubuntu\d+)'
    matches = re.findall(pattern, response.text)
    
    if matches:
        # Return the first (latest) match
        return matches[0]
    return None

def get_current_version():
    """Get current version from PKGBUILD"""
    try:
        with open('PKGBUILD', 'r') as f:
            content = f.read()
            # Extract pkgver and _debver
            pkgver_match = re.search(r'pkgver=(.+)', content)
            debver_match = re.search(r'_debver="\${pkgver}-(.+)"', content)
            if pkgver_match and debver_match:
                return f"{pkgver_match.group(1)}-{debver_match.group(1)}"
    except FileNotFoundError:
        print("PKGBUILD not found")
    return None

def update_pkgbuild(new_version):
    """Update PKGBUILD with new version"""
    # Split version into pkgver and ubuntu suffix
    parts = new_version.split('-')
    pkgver = parts[0]
    ubuntu_suffix = parts[1]
    
    with open('PKGBUILD', 'r') as f:
        content = f.read()
    
    # Update pkgver
    content = re.sub(r'pkgver=.+', f'pkgver={pkgver}', content)
    
    # Update pkgrel to 1 for new version
    content = re.sub(r'pkgrel=\d+', 'pkgrel=1', content)
    
    # Calculate new checksum
    deb_url = f"https://launchpad.net/~libfprint-tod1-group/+archive/ubuntu/ppa/+files/{PACKAGE_NAME}_{new_version}_amd64.deb"
    
    try:
        # Download and calculate sha256sum
        subprocess.run(['wget', '-q', '-O', '/tmp/temp.deb', deb_url], check=True)
        result = subprocess.run(['sha256sum', '/tmp/temp.deb'], capture_output=True, text=True)
        checksum = result.stdout.split()[0]
        content = re.sub(r"sha256sums=\('[^']+'\)", f"sha256sums=('{checksum}')", content)
        subprocess.run(['rm', '/tmp/temp.deb'])
    except subprocess.CalledProcessError:
        print("Failed to download package for checksum")
        return False
    
    with open('PKGBUILD', 'w') as f:
        f.write(content)
    
    return True

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
        if update_pkgbuild(latest):
            print("PKGBUILD updated successfully")
            # Create a commit message
            print(f"Commit message: Update to {latest}")
        else:
            print("Failed to update PKGBUILD")
            sys.exit(1)
    else:
        print("Already up to date")

if __name__ == "__main__":
    main()
