"""
MIT/GU-NNoA-LF License

Copyright (c) 2023-now alan-alexander-1011

(Copyright was added by the owner too :) not too much force but pls give creds 
when showing this to the public or distribute it)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

After the MIT License, the name of the owner("alan-alexander-1011") *Shall Not* be used to
make money or in advertisement or to make any deals that is related to this software because
the software is *100%* free.

The program IS NOT for sale, but for normal and commercial uses.

The Distributor of this software is not needed to show the code of the program to the public. 
But the Distributor of this software may needed to give an simple explanation of what the 
Distributor added/modified to the program.
And the distributor may give the owner credits.
"""

import subprocess
import requests, re

#self-explanatory, fetching pkg info.

rpcprefix = "https://aur.archlinux.org/rpc/v5"
getlink = lambda path : rpcprefix+path

def fetch_package_info(package_name: str):
  response = requests.get(getlink(f'/info/{package_name}'))
  return response.json()

def fetch_db(name: str):
  response = requests.get(getlink(f'/search/{name}'))
  return response.json()

def suggest_package(package_name: str):
  response = requests.get(getlink(f'/suggest/{package_name}'))
  return response.json()

#return pkgs in repo in pacman. returns as (reponame, pkgname, version, desc)
def fetch_official_repo(name: str) -> list[tuple[str, str, str, str]]:
  res = []
  try:
    # Fetch the package information
    repos = subprocess.run(['pacman', '-Si'], capture_output=True, text=True).stdout.strip().split("\n\n")
    
    for pkg in repos:
      try:
        # Extract package name
        pkgname = re.compile(r"^Name\s*:\s*(.*)", re.MULTILINE).search(pkg)
        pkgname = pkgname.group(1).strip() if pkgname else "Unknown"

        # Extract package description
        pkgdesc = re.compile(r"^Description\s*:\s*(.*)", re.MULTILINE).search(pkg)
        pkgdesc = pkgdesc.group(1).strip() if pkgdesc else "No description"

        if pkgname.startswith(name) or (name in pkgdesc):
          # Extract repository name
          repoline = re.compile(r"^Repository\s*:\s*(.*)", re.MULTILINE).search(pkg)
          repoline = repoline.group(1).strip() if repoline else "Unknown"
          
          # Extract package version
          pkgver = re.compile(r"^Version\s*:\s*(.*)", re.MULTILINE).search(pkg)
          pkgver = pkgver.group(1).strip() if pkgver else "Unknown"
          
          
          res.append((repoline, pkgname, pkgver, pkgdesc))
        
      except AttributeError:
        print(f"Warning: Failed to parse package info from:\n{pkg}")
      
  except subprocess.CalledProcessError as e:
    print(f"Error running pacman command: {e}")
    
  return res