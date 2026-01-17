import argparse

def removeTags(script):
  TO_REMOVE = ["[","]","/"]

  newScript = script.replace("-"," ")
  for charToRemove in TO_REMOVE:
      newScript = newScript.replace(charToRemove,"")

  while "<" in newScript:
      start = newScript.index("<")
      end = newScript.index(">")+1
      newScript = newScript[:start]+newScript[end:]
  while "  " in newScript:
      newScript = newScript.replace("  "," ")
  while "\n " in newScript:
      newScript = newScript.replace("\n ","\n")
  while " \n" in newScript:
      newScript = newScript.replace(" \n","\n")
  while newScript[0] == " ":
      newScript = newScript[1:]

  return newScript

def create_gentle_script(input_file):
    """Create a gentle-friendly script by removing tags.
    
    Args:
        input_file: Path to input script file (without .txt extension)
    
    Returns:
        str: Path to the generated gentle-friendly script
    """
    with open(f"{input_file}.txt", "r") as f:
        script = f.read()
    
    output_path = f"{input_file}_g.txt"
    with open(output_path, "w") as f:
        f.write(removeTags(script))
    
    print("Done creating the gentle-friendly script!")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create gentle-friendly script')
    parser.add_argument('--input_file', type=str, help='the script')
    args = parser.parse_args()
    create_gentle_script(args.input_file)
