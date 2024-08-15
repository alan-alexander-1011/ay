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

import colorama
from .aurrpc import *

def list_installed_aur_packages() -> list[tuple]:
  try:
    result = subprocess.run(
        ['pacman', '-Qm'],
        capture_output=True, text=True
    )
    output = result.stdout
    packages = [(line.split()[0], line.split()[1]) for line in output.split('\n') if line]
    return packages
  except subprocess.CalledProcessError:
    return []
    
def list_update_packages() -> list:
  try:
    subprocess.run(['sudo', 'pacman', '-Sy'], capture_output=True, text=True)
    result = subprocess.run(
        ['pacman', '-Quq'],
        capture_output=True, text=True
    )
    output = result.stdout
    packages = output.split('\n')
    return packages
  except subprocess.CalledProcessError:
    return []
    
def update_aur_pacman():
  print(textformat(colorama.Fore.LIGHTCYAN_EX,"updating official repo.."))
  listopkgs = list_update_packages()

  printformat = [listopkgs[i:i + 3] for i in range(0, len(listopkgs), 3)]

  print(textformat(colorama.Fore.LIGHTYELLOW_EX,"official repo updates:"))

  if listopkgs != ['']:
    for row in printformat:
      print(textformat(colorama.Fore.LIGHTGREEN_EX,"  " + ' '.join(row)))
  else:
    print(textformat(colorama.Fore.LIGHTGREEN_EX, "  No official repo updates available."))

  print()
  print(textformat(colorama.Fore.LIGHTYELLOW_EX, "AUR updates:"))

  aurpkgs = list_installed_aur_packages()
  aur_updates = []

  for package in aurpkgs:
    name = package[0]
    version = package[1]
    fetched = fetch_package_info(name)
    if fetched["resultcount"] > 0:
      fversion= fetched["results"][0]["Version"]

      if version != fversion:
        aur_updates.append(name)

  #show AUR updates
  if len(aur_updates) > 0:
    for i, v in enumerate(aur_updates, 1):
      print(textformat(colorama.Fore.LIGHTGREEN_EX,f"{i}, {v}"))

    print("choose AUR packages that can break your computer , or leave blank (for e.g: 1 , 1 2 3)")
    opt = input("-->").strip()

    #check if user leave blank
    if opt != "":
      #nearly the same as the choosing packages in aurrpc.py
      if opt.find(" ") == -1:
        if opt.isdigit():
          if int(opt) > 0 and int(opt) <= len(aur_updates):
            aur_updates.pop(int(opt)-1)
          else:
            return textformat(colorama.Fore.LIGHTRED_EX, "Invalid selection.")
        else:
          return textformat(colorama.Fore.LIGHTRED_EX, "Option is not a digit.")
      else:
        opts = opt.split(" ")
        i = 1
        for opt in opts:
          if opt.isdigit():
            if int(opt) > 0 and int(opt) <= len(aur_updates):
              aur_updates.pop(int(opt)-i)
            else:
              return textformat(colorama.Fore.LIGHTRED_EX, "Invalid selection.")
          else:
            return textformat(colorama.Fore.LIGHTRED_EX, "Option is not a digit.")
          i += 1
  
    
  else:
    print(textformat(colorama.Fore.LIGHTGREEN_EX, "  No AUR packages to update."))
  
  if listopkgs != ['']:
    #update
    print(textformat(colorama.Fore.LIGHTCYAN_EX, "Updating from official repo"))
    try:
      subprocess.run(['sudo', 'pacman', '-Su', '--noconfirm'], check=True)
      print(textformat(colorama.Fore.GREEN, "Successfully updated official repo."))
    except subprocess.CalledProcessError:
      print(textformat(colorama.Fore.LIGHTRED_EX, "Failed to update official repo."))
  
  if len(aur_updates)>0:
    print(textformat(colorama.Fore.LIGHTCYAN_EX, "Updating from AUR"))
    return install_pkg(aur_updates)
  
  return textformat(colorama.Fore.LIGHTCYAN_EX,"Command ran successfully")

def install_pkg(packages: list) -> (str | int):
  if packages == []:
    return textformat(colorama.Fore.LIGHTRED_EX, "No packages in arguments. (main.py install 'all of packages seperated by spaces.')")

  for package_name in packages:
    pkgname = download_pkgbuild(package_name)
    print(f"========Installing {package_name}========")

    #condition for retcode
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
    
    data = fetch_package_info(package_name)["results"][0]

    print(f"===========PACKAGE INFO===========")
    print(f"Pkgname: {package_name}")
    print(f"Version: {data["Version"]}")
    print(f"Dependencies: {' '.join(data["Depends"])}")
    if data.get("OptDepends", False):
      print(f"Optional dependencies: {' '.join(data["OptDepends"])}")
    print(f"===================================")
    
    # Extracting the tarball
    print(textformat(colorama.Fore.CYAN, "Extracting package build..."))
    extraction_dir = os.path.dirname(pkgname)
    print(f"path extracted targz: {extraction_dir}")
    subprocess.run(['tar', '-xzf', pkgname, '-C', extraction_dir], check=True)

    current_dir = os.getcwd()
    os.chdir(os.path.join(extraction_dir,package_name))

    #parsing PKGBUILD data
    checkflag = input(textformat(colorama.Fore.LIGHTYELLOW_EX, ":: Want to take a peek/edit at PKGBUILD? (y/n):")).lower() == "y"

    if checkflag:
      editor = os.getenv("EDITOR", "nano")
      subprocess.run([editor, os.path.join(extraction_dir,package_name,"PKGBUILD")], check=False)
    
    # Building the package
    print(textformat(colorama.Fore.CYAN, "Building package with makepkg..."))
    try:
      result = subprocess.run(['makepkg', '-si'], check=True)
      os.chdir(current_dir)
      if result.returncode == 0:
          if packages != []:
            packages.remove(package_name)
          else:
            return textformat(colorama.Fore.GREEN, "Package built and installed successfully.")
      else:
          return textformat(colorama.Fore.LIGHTRED_EX, f"makepkg failed with return code: {result.returncode}")
    except KeyboardInterrupt:
      return textformat(colorama.Fore.LIGHTRED_EX, "Process interrupted by user.")
    except subprocess.CalledProcessError:
      return textformat(colorama.Fore.LIGHTRED_EX, "Error running makepkg.")