"""
POS Monitor Version Information
Central location for version management
"""

# Version information
MAJOR = 1
MINOR = 0
PATCH = 0
BUILD = 0

# Version string
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
VERSION_FULL = f"{MAJOR}.{MINOR}.{PATCH}.{BUILD}"

# Product information
PRODUCT_NAME = "POS Monitor"
COMPANY_NAME = "UniSight"
COPYRIGHT = "© 2025 UniSight. All rights reserved."
DESCRIPTION = "POS Application Monitor Service"

# File version info for PyInstaller
VERSION_INFO = {
    "filevers": (MAJOR, MINOR, PATCH, BUILD),
    "prodvers": (MAJOR, MINOR, PATCH, BUILD),
    "CompanyName": COMPANY_NAME,
    "FileDescription": DESCRIPTION,
    "FileVersion": VERSION_FULL,
    "InternalName": "POSMonitor",
    "LegalCopyright": COPYRIGHT,
    "OriginalFilename": "POSMonitorService.exe",
    "ProductName": PRODUCT_NAME,
    "ProductVersion": VERSION_FULL,
}

def get_version():
    """Get the current version string"""
    return VERSION

def get_full_version():
    """Get the full version string with build number"""
    return VERSION_FULL

def update_version_files():
    """Update version information in various files"""
    import re
    from pathlib import Path
    
    # Update version-info.txt
    version_info_path = Path("version-info.txt")
    if version_info_path.exists():
        content = version_info_path.read_text()
        
        # Update filevers
        content = re.sub(
            r'filevers=\(\d+, \d+, \d+, \d+\)',
            f'filevers=({MAJOR}, {MINOR}, {PATCH}, {BUILD})',
            content
        )
        
        # Update prodvers
        content = re.sub(
            r'prodvers=\(\d+, \d+, \d+, \d+\)',
            f'prodvers=({MAJOR}, {MINOR}, {PATCH}, {BUILD})',
            content
        )
        
        # Update FileVersion
        content = re.sub(
            r"StringStruct\(u'FileVersion', u'[\d.]+'\)",
            f"StringStruct(u'FileVersion', u'{VERSION_FULL}')",
            content
        )
        
        # Update ProductVersion
        content = re.sub(
            r"StringStruct\(u'ProductVersion', u'[\d.]+'\)",
            f"StringStruct(u'ProductVersion', u'{VERSION_FULL}')",
            content
        )
        
        version_info_path.write_text(content)
        print(f"Updated version-info.txt to {VERSION_FULL}")
    
    # Update build.bat
    build_bat_path = Path("build.bat")
    if build_bat_path.exists():
        content = build_bat_path.read_text()
        content = re.sub(
            r'set VERSION=[\d.]+',
            f'set VERSION={VERSION}',
            content
        )
        build_bat_path.write_text(content)
        print(f"Updated build.bat to {VERSION}")

if __name__ == "__main__":
    print(f"POS Monitor Version: {get_full_version()}")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        update_version_files()
        print("Version files updated!")