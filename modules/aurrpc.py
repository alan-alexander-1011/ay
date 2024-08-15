import requests
import subprocess
import colorama
from git import Repo
import os
import sys
from . import progbar, parser
from .fetching import *

#format text and reset it.
textformat = lambda color, text: color + text + colorama.Fore.RESET


#downloading package, and return the pkg path.
def download_pkgbuild(package_name: str) -> (str | int):

  name_packages = []
  pkgs = suggest_package(package_name)

  #if there is multiple pkgs, asks to choose one or multiple pkgs
  if len(pkgs) > 1:
    print(textformat(colorama.Fore.LIGHTCYAN_EX, "there are multiple packages to install, please choose one, or multiple (e.g: 1 2 3)"))
    #print names
    for i, pkg in enumerate(pkgs, start=1):
      print(f"{i}. {pkg}")
    
    #strip so it doesnt bug out on for e.g: '  1  '
    opt = input("--> ").strip()
    if opt == "":
      return textformat(colorama.Fore.LIGHTRED_EX, "invalid option.")

    #check spaces (cause this is space separated)
    if opt.find(" ") == -1:

      #check if its a digit
      if opt.isdigit():

        #check if its in the range
        if int(opt) > 0 and int(opt) <= len(pkgs):
          #put it in pkgs
          num = int(opt)
          name_packages.append(pkgs[num-1])

        #if its not in range
        else:
          return textformat(colorama.Fore.LIGHTRED_EX, "invalid option.")
      
      #if it isnt a digit
      else:
        return textformat(colorama.Fore.LIGHTRED_EX, "option is not a digit.")
      
    #if there is space (heres the perpose of the strip above to make sure not bugged out)
    else:
      opts = opt.split(" ") #just split space.

      #loop thru options
      for opt in opts:
        #check if its a digit, if so, add it to the list of packages.
        if opt.isdigit():
          if int(opt) > 0 and int(opt) <= len(pkgs):
            num = int(opt)
            name_packages.append(pkgs[num-1])
          else:
            return textformat(colorama.Fore.LIGHTRED_EX, "invalid option.")
        else:
          return textformat(colorama.Fore.LIGHTRED_EX, "option is not a digit.")
        
  #if there is only one
  elif len(pkgs) == 1:
    name_packages.append(pkgs[0])
  
  #if nothing found
  else:
    return textformat(colorama.Fore.LIGHTRED_EX, "no package found.")

  #loop through packages.
  for package_name in name_packages:
    #get pkg info.
    pkginfo = fetch_package_info(package_name)
    
    if pkginfo['results'] == []:
      return textformat(colorama.Fore.LIGHTRED_EX, f"No package named {package_name} found.")

    #take the url and download the package. 
    urlpath: str = pkginfo['results'][0]['URLPath']
    pkg_url: str = "https://aur.archlinux.org" + urlpath
    # https://aur.archlinux.org + /cgit/aur.git/snapshot/xxx.tar.gz

    response = requests.get(pkg_url, stream=True)
    
    if response.status_code == 200:
      #if server respond
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


    

