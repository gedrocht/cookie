def decode(message_file):
  try:
    numbered_lines = dict()
    for line in message_file:
      line_split = line.strip().split(" ")
      if len(line_split) < 2:
        raise Exception
      number = int(line_split[0])
      line_content = " ".join(line_split[1:])
      numbered_lines[number] = line_content
    
    id = 1
    last_id = len(numbered_lines)
    offset = 2
    reached_last_id = False
    decoded_message = ""

    while id <= last_id:
      decoded_message += numbered_lines[id] + " "
      id += offset
      if id == last_id:
        reached_last_id = True
      offset += 1
    
    if not reached_last_id:
      raise Exception

    return decoded_message.strip()
  except Exception as exception:
    print("ERROR: Input file is incorrectly formatted.")

print(decode(open("input.txt","r")))