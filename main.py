from modules import *

command:str = sys.argv[1]
args:list[str] = sys.argv[2:]
os.makedirs(os.path.join(os.path.dirname(__file__), "pkgbuilds"),exist_ok=True)

def help():
  print('install / sync : used to install things from AUR and pacman.')
  print('update / upgrade : used to update all of your packages and your core files.')
  print('remove / uninstall : used to remove packages.')
  print('help : show this help tab.')
  
if command in ['install', 'sync']:
  ret = install_pkg(args)
  print(ret)
elif command in ['update', 'upgrade']:
  subprocess.run(['sudo', 'pacman', '-Syu'] + args)
elif command in ['remove', 'uninstall']:
  subprocess.run(['sudo', 'pacman', '-R'] + args)
elif command == 'help':
  help()
else:
  print("Invalid commands. The commands are:")
  help()
  exit(-1)