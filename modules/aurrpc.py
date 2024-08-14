import requests
import subprocess
import colorama
import os
import sys
from . import progbar, parser

textformat = lambda color, text: color + text + colorama.Fore.RESET

def fetch_package_info(package_name: str):
  response = requests.get(f'https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={package_name}')
  return response.json()

def download_pkgbuild(package_name: str) -> (str | int):
  pkginfo = fetch_package_info(package_name)
  if pkginfo['resultcount'] == 0:
    return 1
  
  urlpath: str = pkginfo['results'][0]['URLPath']
  pkg_url: str = "https://aur.archlinux.org" + urlpath
  # https://aur.archlinux.org + /cgit/aur.git/snapshot/xxx.tar.gz

  response = requests.get(pkg_url, stream=True)
  
  if response.status_code == 200:
    pkgname = urlpath.split("/")[-1]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pkgbuilds", pkgname)
    os.makedirs(os.path.dirname(path), exist_ok=True)  # Create the directory if it does not exist
    size = int(response.headers.get('Content-Length', 0))
    with open(path, 'wb') as f:
      print(textformat(colorama.Fore.CYAN, "Downloading package build..."))
      for chunk in response.iter_content(chunk_size=2**14):
        if chunk:
          f.write(chunk)
          if size > 0:
            progbar.print_progbar(f.tell(), size)
      print(textformat(colorama.Fore.LIGHTGREEN_EX, "pkgbuild downloaded."))
    return path
  else:
    return response.status_code

def install_pkg(packages: list) -> (str | int):
  for package_name in packages:
    pkgname = download_pkgbuild(package_name)
    if pkgname == 1:
      print(textformat(colorama.Fore.LIGHTYELLOW_EX, "Package is not in AUR. Installing through pacman..."))
      a = subprocess.run(['sudo', 'pacman', '-Sy', package_name], shell=True)
      if a.returncode == 0:
        return textformat(colorama.Fore.GREEN, "Installed via pacman.")
      return textformat(colorama.Fore.LIGHTRED_EX, "Package does not exist both in AUR and pacman.")
    elif pkgname == 500:
      return textformat(colorama.Fore.LIGHTRED_EX, "AUR server is having problems.")
    elif isinstance(pkgname, int):
      return textformat(colorama.Fore.LIGHTRED_EX, f"Unexpected error. Returned: {pkgname}")
    
    # Extracting the tarball
    print(textformat(colorama.Fore.CYAN, "Extracting package build..."))
    extraction_dir = os.path.dirname(pkgname)
    print(f"path extracted targz: {extraction_dir}")
    subprocess.run(['tar', '-xzf', pkgname, '-C', extraction_dir], check=True)

    current_dir = os.getcwd()
    os.chdir(os.path.join(extraction_dir,package_name))
    data = parser.parse_pkgbuild(os.path.join(extraction_dir,package_name,"PKGBUILD"))
    print(f"===========PACKAGE INFO===========")
    print(f"Pkgname: {data.get("pkgname", "no name???")}")
    ks = data.get("pkgrel", "unknown number")
    print(f"Version: {data.get("pkgver", "unknown version")} ({ks[:-1]+"1-st" if ks[-1] == "1" else ks[:-1]+"2-nd" if ks[-1] == "2" else ks[:-1]+"3-rd" if ks[-1] == "3" else ks+"-th"} release)")
    print(f"Architecture: {data.get("arch")}")
    print(f"Dependencies: {data.get('depends', 'unknown or not written in PKGBUILD.')}")
    print(f"Source: {data.get('source')}")
    print(f"md5sums: {data.get('md5sums',"no md5 checksum")}")
    print(f"sha256sums: {data.get('sha256sums',"no sha256 checksum")}")
    print(f"===================================")
    
    # Building the package
    print(textformat(colorama.Fore.CYAN, "Building package with makepkg..."))
    try:
      result = subprocess.run(['makepkg', '-si'], check=True)
      os.chdir(current_dir)
      if result.returncode == 0:
          return textformat(colorama.Fore.GREEN, "Package built and installed successfully.")
      else:
          return textformat(colorama.Fore.LIGHTRED_EX, f"makepkg failed with return code: {result.returncode}")
    except KeyboardInterrupt:
      return textformat(colorama.Fore.LIGHTRED_EX, "Process interrupted by user.")
    except subprocess.CalledProcessError:
      return textformat(colorama.Fore.LIGHTRED_EX, "Error running makepkg.")
    

