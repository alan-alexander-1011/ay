from modules import *

command:str = sys.argv[1]
args:list[str] = sys.argv[2:]

def help():
  print('install / sync : used to install things from AUR and pacman.')
  print('update / upgrade : used to update all of your packages and your core files.')
  print('remove / uninstall : used to remove packages.')
  print('help : show this help tab.')

if command not in ['install', 'sync', 'update', 'upgrade', 'remove', 'uninstall', 'help']:
  print("Invalid commands. The commands are:")
  help()
  exit(-1)

if command in ['install', 'sync']:
  ret = install_pkg(args)
  print(ret)
elif command in ['update', 'upgrade']:
  subprocess.run(['sudo', 'pacman', '-Syu'] + args)
elif command in ['remove', 'uninstall']:
  subprocess.run(['sudo', 'pacman', '-R'] + args)