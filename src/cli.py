def confirm(prompt: str, default: bool | None = None) -> bool:
  """Prompts the user to confirm some action."""
  options = "[y/n]" if default is None else ("[Y/n]" if default else "[y/N]")
  answer = None
  while answer not in ["yes", "y", "no", "n"] and (answer != "" or default is None):
    answer = input(f"{prompt} {options} ").lower()
  if answer == "":
    return default
  else:
    return answer in ["yes", "y"]
