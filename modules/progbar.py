import colorama
import sys

def print_progbar(size1, size2):
  done = int(25 * size1 / size2)
  sys.stdout.write(f'\rDownloading: {colorama.Fore.LIGHTYELLOW_EX}[{"#" * done}{"-" * (25 - done)}]{colorama.Fore.RESET} {done * 2}%')
  sys.stdout.flush()