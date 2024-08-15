from modules import *

textformat = lambda color, text: color + text + colorama.Fore.RESET

if platform.system() == 'Windows':
  print("Arch Linux and Arch-based distros only.")
  exit (-1)

command:str = sys.argv[1]
args:list[str] = sys.argv[2:]
os.makedirs(os.path.join(os.path.dirname(__file__), "pkgbuilds"),exist_ok=True)

def help():
  print('install / sync : used to install things from AUR and pacman.')
  print('update / upgrade : used to update all of your packages and your core files.')
  print('remove / uninstall : used to remove packages.')
  print('search / query : used to search pkgs on AUR.')
  print('help : show this help tab.')
  
if command in ['install', 'sync']:
  ret = install_pkg(args)
  print(ret)

elif command in ['update', 'upgrade']:
  try:
    print(update_aur_pacman())
  except KeyboardInterrupt:
    print(textformat(colorama.Fore.LIGHTRED_EX, "\rUpdate cancelled by user."))

elif command in ['remove', 'uninstall']:
  if args == []:
    print(textformat(colorama.Fore.LIGHTRED_EX, "No packages in arguments. (main.py remove 'all of packages seperated by spaces.')"))
  else:
    subprocess.run(['sudo', 'pacman', '-R'] + args)

elif command in ['search', 'query']:
  try:
    if len(args[0]) < 3:
      print(textformat(colorama.Fore.LIGHTRED_EX, "the name is too short. make sure the name length is 3 and above"))
      exit(0)
  except IndexError:
    print(textformat(colorama.Fore.LIGHTRED_EX, "No package name provided."))
  else:
    a = fetch_db(args[0])
    b = fetch_official_repo(args[0])
    if a["resultcount"] == 0:
      print(textformat(colorama.Fore.LIGHTRED_EX, f"No package named {args[0]} found."))
    else:
      i = 1
      for v in b:
        print(f"{i}. {textformat(colorama.Fore.CYAN,v[0])}/{textformat(colorama.Fore.LIGHTGREEN_EX, v[1])} - {textformat(colorama.Fore.GREEN, v[2])}\nDesc: {textformat(colorama.Fore.LIGHTYELLOW_EX,v[3])}\n")
        i += 1
      for i , pkg in enumerate(a["results"], start=i):
        print(f"{i}. {textformat(colorama.Fore.LIGHTBLUE_EX, "AUR")}/{textformat(colorama.Fore.LIGHTGREEN_EX, pkg["Name"])} - {textformat(colorama.Fore.GREEN, pkg["Version"])}\nDesc: {textformat(colorama.Fore.LIGHTYELLOW_EX, str(pkg["Description"]))}\n")

elif command == 'help':
  help()

else:
  print("Invalid commands. The commands are:")
  help()

shutil.rmtree(os.path.join(os.path.dirname(__file__), "pkgbuilds"))