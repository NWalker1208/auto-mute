def encipher(s: str) -> str:
  """Enciphers a given string by applying a simple caesar cipher.
  This lets users choose to avoid having profanity in human-readable form."""
  return ''.join(_shift_letter(c, 1) for c in s)

def decipher(s: str) -> str:
  """The inverse of encipher."""
  return ''.join(_shift_letter(c, -1) for c in s)

# This array can be modified for other languages.
_ALPHABET = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def _shift_letter(c: str, offset: int) -> str:
  """Rotates a character through the alphabet, if it is a letter."""
  c_lower = c.lower()
  if c_lower not in _ALPHABET:
    return c
  
  o_lower = _ALPHABET[(_ALPHABET.index(c_lower) + offset) % len(_ALPHABET)]
  return o_lower if c.islower() else o_lower.upper()
