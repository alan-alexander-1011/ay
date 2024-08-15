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