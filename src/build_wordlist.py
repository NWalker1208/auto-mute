# Builds a wordlist from InnovativeInventor/dict4schools's light blacklist

import urllib
import urllib.request
from automute import encipher

#URL = "https://raw.githubusercontent.com/InnovativeInventor/dict4schools/master/blacklists/blacklist_light.txt"
URL = "https://raw.githubusercontent.com/coffee-and-fun/google-profanity-words/main/data/en.txt"

print("Downloading wordlist...")
count = 0
with open("default_wordlist_en.txt", "w") as dest:
  dest.write(f"# Downloaded from {URL} and enciphered.\n")
  with urllib.request.urlopen(URL) as source:
    for line in source:
      word: str = line.decode('utf8').rstrip()
      if word.isalpha():
        dest.write("\\b" + encipher(word) + "\\b\n")
        count += 1
print(f"Created wordlist with {count} words")
