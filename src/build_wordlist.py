# Builds a wordlist from InnovativeInventor/dict4schools's light blacklist

import urllib
import urllib.request
from automute import encipher

URL = "https://raw.githubusercontent.com/InnovativeInventor/dict4schools/master/blacklists/blacklist_light.txt"

print("Downloading wordlist...")
count = 0
with open("default_wordlist_en.txt", "w") as dest:
  dest.write(f"# Downloaded from {URL} and enciphered.\n")
  with urllib.request.urlopen(URL) as source:
    for line in source:
      dest.write("\\b" + encipher(line.decode('utf8').rstrip()) + "\\b\n")
      count += 1
print(f"Created wordlist with {count} words")
