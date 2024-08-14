import re
from typing import Dict, Optional, Literal

def parse_pkgbuild(file_path: str) -> (Dict[str, Optional[str]] | Literal[-1]) :
    # Define a dictionary to store the parsed fields
    fields = {
        'pkgname': None,
        'pkgver': None,
        'pkgrel': None,
        'arch': None,
        'depends': None,
        'source': None,
        'md5sums': None,
        'sha256sums': None,
    }
    
    # Regular expressions to match fields
    regexes = {
        'pkgname': re.compile(r'pkgname\s*=\s*(\S+)'),
        'pkgver': re.compile(r'pkgver\s*=\s*(\S+)'),
        'pkgrel': re.compile(r'pkgrel\s*=\s*(\S+)'),
        'arch': re.compile(r'arch\s*=\s*\((.*?)\)'),
        'depends': re.compile(r'depends\s*=\s*\((.*?)\)'),
        'source': re.compile(r'source\s*=\s*\(([\s\S]*?)\)\n'),
        'md5sums': re.compile(r'md5sums\s*=\s*\(([\s\S]*?)\)\n'),
        'sha256sums': re.compile(r'sha256sums\s*=\s*\(([\s\S]*?)\)\n'),
    }

    try:
        with open(file_path, 'r') as f:
            data = f.read()
            
        for key, regex in regexes.items():
            match = regex.search(data)
            if match:
                # Clean up and store the matched value
                fields[key] = match.group(1).replace('"', '').replace("'", '').strip()

        return fields
    
    except FileNotFoundError:
        return -1