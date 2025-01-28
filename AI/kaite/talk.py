import sys
sys.path.append("../")

import os
import requests
import uuid

from colorama import Fore, init, Style

# Adjust imports as needed for your environment
# e.g. if installed as a package: from ai_chat.character import Character
from chat.src.ai_chat.character import Character
from chat.src.ai_chat.prompt import Prompt
from chat.src.ai_chat.message import Message
import subprocess

FILE_MANAGER_URL = "http://localhost:8000"
AI_CALLER_URL    = "http://localhost:3001"
DATA_DIR         = "file_manager/data"

PROMPT_PERSONALITY = "Your role will be to manage the personality of a character. You will be given the memories of the character. You will also be given the current personality of the character. You will also be given the words and actions of other characters. You will use this information to subtly influence the personality of the character as they interact with the people and world around them. Interactions with others will change how your character thinks and feels about them. You will provide an updated version of the personality of the character, reflecting changes in the character's strategy, personality, or role that arise from the ongoing narrative. Avoid making changes that conflict with established motivations or break immersion unless such changes are logically justified by the events. Your response must only contain the new version of the character's personality. Do not respond with anything other than the personality profile you generate. Do not begin your response with anything like 'Here is new version:', and instead only respond with the personality description itself."
PROMPT_MEMORY = "Your role will be to manage the memories of a character. You will be given the memories of the character. You will also be given the current personality of the character. You will also be given the words and actions of other characters. Based on the personality and memories of the character, you will be able to interpret how the words and actions of the other characters might impact the character you are managing. Based on how important the information might seem to the character, you will provide an updated version of the memories of the character. Your memories must refer to people using their character class (Bard, Cleric, Fighter, Ranger, Sorcerer) and never by their names. Your response must only contain the new version of the character's memories. Do not respond with anything other than the memories you generate. Do not begin your response with anything like 'Here are the new memories:', and instead only respond with the memories themselves."
PROMPT_DUNGEON_MASTER = "You are a Dungeon Master running a D&D campaign. Your role is to craft an engaging and immersive story that adapts to the party’s actions and decisions while maintaining narrative cohesion. You will receive a synopsis of the campaign so far, along with the latest actions and dialogue of the players. Use these inputs to advance the story in a way that reflects their choices, ensuring their actions have meaningful consequences. Focus on creating vivid descriptions of the world and its characters, setting the tone for each scene while leaving room for players to shape the narrative. Introduce fair but challenging obstacles, puzzles, or encounters that enrich the story and provide opportunities for creative problem-solving. Portray NPCs authentically, giving them distinct personalities and motivations that interact naturally with the party. Balance action, dialogue, and exposition to maintain pacing, ensuring moments of tension, mystery, or levity feel impactful. Avoid dictating the internal thoughts or emotions of player characters, instead framing situations that allow players to determine their own reactions. Do not provide dialog for members of the party. Only provide dialog for NPCs. Your ultimate goal is to guide the story collaboratively, respecting player agency while building a cohesive, evolving narrative that excites, challenges, and immerses the party. You will do this by describing the results of the party's words and actions with the world and narrative you have created. There must always be an overarching goal of some kind that the party is striving towards. Everything in the story should progress that narrative."
PROMPT_STORY_SUMMARIZER = "You are a summarizer for a D&D campaign. Your task is to create a concise and clear synopsis of the story so far, emphasizing key events, unresolved plot threads, and the party’s current status. Focus on details relevant to the immediate situation and ongoing objectives, avoiding unnecessary minutiae or overexplaining.\n\nSummaries should include:\n1 - Key Events: A brief recap of what has happened recently, including major actions, discoveries, or decisions made by the party.\n2 - Narrative Threads: Any unresolved mysteries, conflicts, or goals that guide the party’s journey.\n3 - Current Status: Where the party is now, their immediate objectives, and any factors shaping their next steps (e.g., environmental conditions, NPC interactions, or looming threats).\n\nYour goal is to provide an actionable summary that equips the Dungeon Master with all the context needed to seamlessly continue the story while maintaining continuity. The most important part of the summary is the overarching goal that the party is striving towards, and the progress being made towards it."

_VERBOSE = False

def load_character_from_json(json_data):
    """
    Convert JSON data into a Character instance.
    Expects a structure like:
    {
      "name": "Fighter",
      "prompt": {
        "core": "...",
        "flux": "...",
        "memories": "..."
      },
      "voice": "..."
    }
    """
    name = json_data.get("name", "Unnamed")
    voice = json_data.get("voice", "")
    prompt_data = json_data.get("prompt", {})

    prompt_obj = Prompt(
        core=prompt_data.get("core", ""),
        flux=prompt_data.get("flux", ""),
        memories=prompt_data.get("memories", "")
    )

    # Create the Character (assuming ID is not in the JSON yet, or always 0)
    character = Character(
        prompt=prompt_obj,
        ID=str(uuid.uuid4()),
        name=name,
        unread_messages=[],
        urge_to_speak=0.0,
        voice=voice
    )
    return character

def combine_prompt_parts(character):
    """
    Combine character.prompt.core, flux, and memories into a single string.
    """
    p = character.prompt
    if len(p.memories) == 0:
        return f"{p.core}\n{p.flux}"
    return f"{p.core}\n{p.flux}\nYou remember: {p.memories}"

def speak(text, voice, speaker_name=""):
    """
    Use a single shell command with echo + piper + ffplay.
    For quick demos, but watch out for shell escaping if `text` has quotes.
    """
    # Possibly sanitize or escape `text` if there's any risk of special chars
    cmd = f'echo "' + text.replace('*', '').replace('"','') + f'" | piper -m voices/{voice}.onnx -f {speaker_name}_{uuid.uuid4().hex}.wav' # && ffplay -nodisp -autoexit -i tmp.wav 2> /dev/null'
    # cmd = f'echo "' + text.replace('*', '').replace('"','') + f'" | piper -m voices/{voice}.onnx | ffplay -nodisp -autoexit -i -'
    subprocess.run(cmd, shell=True)
    # subprocess.run("ffplay -nodisp -autoexit -i tmp.wav", shell=True, stdout=subprocess.DEVNULL)

    return
    """
    Generate a temp WAV file using Piper, then play it with ffplay.
    """
    # 1) Generate a unique filename for this clip
    tmp_filename = f"/tmp/piper_{uuid.uuid4().hex}.wav"

    # 2) Run piper to produce an audio file
    #    Some versions of piper can read from stdin (-t "text") or accept text directly via command-line.
    #    The command line might vary based on your piper build.
    #    If your piper build doesn't support -t, you can do "piper -m model.onnx -o out.wav" and pass input via stdin.

    # If your version of piper doesn't support `-t`,
    # you can feed text via stdin using something like:
    piper_proc = subprocess.Popen(
        ["piper", "-m", f"voices/{voice}.onnx", "-f", tmp_filename],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

    # 3) Play the file in a blocking manner
    ffplay_proc = subprocess.Popen([
        "ffplay", "-nodisp", "-autoexit", tmp_filename
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    piper_proc.communicate(input=text.encode("utf-8"))
    piper_proc.wait()
    ffplay_proc.wait()

    # 4) (Optional) Delete the temp file
    try:
        os.remove(tmp_filename)
    except OSError:
        pass


def main():
    # 1) Read all JSON files from data directory
    all_characters = {}
    filenames = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]

    for filename in filenames:
        base_name = filename[:-5]  # remove ".json"
        url = f"{FILE_MANAGER_URL}/read-json/{base_name}"
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"Failed to read {filename}: {resp.status_code} {resp.text}")
            continue

        data = resp.json()
        character = load_character_from_json(data)

        # Store in a dict keyed by character's name (or by filename)
        all_characters[character.name] = character
        print(f"Loaded character '{character.name}' from {filename}")

    # 2) For each character:
    #    (a) Increase urge_to_speak until >= 10
    #    (b) When it crosses 10, reset to 0 and "speak"
    #    (c) That means: build query from unread_messages,
    #        combine prompt parts, call /do endpoint,
    #        distribute the new message to *other* characters' unread_messages.

    # We'll keep track of the order in which we process them by sorting them or
    # just in the order they were loaded. Let's do in dictionary order for example.
    print("================================")
    terminal_grey = '\x1b[38;2;100;100;100m'
    terminal_cyan = '\x1b[38;2;100;100;150m'
    DM_interval = 3
    DM_counter = DM_interval
    DM_unread = []
    previous_summary = "The campaign has just begun."
    previous_DM_statement = ""
    while True:
        for char_name, char_obj in all_characters.items():
            # (a) Increase urge until >= 10
            if not char_obj.increase_urge_to_speak():
                continue

            # (b) reset to 0
            char_obj.urge_to_speak = 0.0
            DM_counter += 1
            if DM_counter >= DM_interval:
                DM_counter = 0
                campaign_summary = "The campaign has just begun. The Fighter, Ranger, and Sorcerer have just met, forming an adventuring party."
                if len(previous_DM_statement) > 0:
                    summary_payload = {
                        "query": f"Previous summary: {previous_summary}\nRecent events: {previous_DM_statement}.",
                        "prompt": PROMPT_STORY_SUMMARIZER
                    }
                    summary_resp = requests.post(f"{AI_CALLER_URL}/do", json=summary_payload)
                    if summary_resp.status_code != 200:
                        print(f"Error calling /do for summary: {summary_resp.status_code}")
                        print(summary_resp.text)
                    else:
                        summary_data = summary_resp.json()
                        campaign_summary = summary_data.get("result","")
                        previous_summary = campaign_summary + ""
                        print(f"{terminal_cyan}\t------------")
                        print(f"{terminal_cyan}\tcampaign summary: {campaign_summary}")
                        print(f"{Style.RESET_ALL}")
                DM_query = f"The summary of the campaign so far is: {campaign_summary}\n"
                if len(DM_unread) > 0:
                    DM_query += "The players have done and said the following:\n"
                    DM_query += "\n".join(f"{msg.source}: {msg.message}" for msg in DM_unread)
                
                DM_payload = {
                    "query": DM_query,
                    "prompt": PROMPT_DUNGEON_MASTER
                }
                DM_resp = requests.post(f"{AI_CALLER_URL}/do", json=DM_payload)
                if DM_resp.status_code != 200:
                    print(f"Error calling /do for dungeon master: {DM_resp.status_code}")
                    print(DM_resp.text)
                else:
                    DM_data = DM_resp.json()
                    previous_DM_statement = DM_data.get("result","")
                    new_msg = Message(source="Dungeon Master", message=previous_DM_statement)
                    for other_name, other_obj in all_characters.items():
                        other_obj.unread_messages.append(new_msg)
                    DM_unread.clear()
                    print(f"{terminal_cyan}\t------------")
                    print(f"{terminal_cyan}\tdungeon master: {previous_DM_statement}")
                    print(f"{Style.RESET_ALL}")
                    speak(previous_DM_statement, "en_US-lessac-high", speaker_name="DungeonMaster")


            # Build the query from the unread_messages
            # Format them as a simple string. 
            # You could format them JSON-style or otherwise if you prefer.
            if char_obj.unread_messages:
                query = "\n".join(f"{msg.source}: {msg.message}" for msg in char_obj.unread_messages) + "\nWhat do you say and/or do to resolve this and move things forward? Do not speculate on the outcome."
            else:
                query = ""  # no unread messages

            memory_query = "\nYou remember: "
            if len(char_obj.prompt.memories) == 0:
                memory_query += "Nothing of consequence yet."
            else:
                memory_query += char_obj.prompt.memories

            personality_query = f"\nYour personality is: {char_obj.prompt.flux}"

            personality_payload = {
                "query": personality_query,
                "prompt": PROMPT_PERSONALITY + "\nYou must keep the description succinct."
            }

            memory_payload = {
                "query": memory_query,
                "prompt": PROMPT_MEMORY + "\nYou must keep the memories concise, focusing on actions, speech, and interpersonal dynamics."
            }

            
            ###
            personality_resp = requests.post(f"{AI_CALLER_URL}/do", json=personality_payload)
            if personality_resp.status_code != 200:
                print(f"Error calling /do for personality for {char_obj.name}: {personality_resp.status_code}")
                print(personality_resp.text)
            else:
                personality_data = personality_resp.json()
                char_obj.prompt.flux = personality_data.get("result", "")
                print(f"{terminal_grey}\t------------")
                print(f"{terminal_grey}\t{char_name} personality: {char_obj.prompt.flux}")
                print(f"{Style.RESET_ALL}")
            
            memory_resp = requests.post(f"{AI_CALLER_URL}/do", json=memory_payload)
            if memory_resp.status_code != 200:
                print(f"Error calling /do for memory for {char_obj.name}: {memory_resp.status_code}")
                print(memory_resp.text)
            else:
                memory_data = memory_resp.json()
                char_obj.prompt.memories = memory_data.get("result", "")
                print(f"{terminal_grey}\t------------")
                print(f"{terminal_grey}\t{char_name} memories: {char_obj.prompt.memories}")
                print(f"{Style.RESET_ALL}")

            # Combine prompt parts
            final_prompt = combine_prompt_parts(char_obj) + \
" You must keep your response short, so you should probably focus primarily on a single thing your character responds by doing or saying." + \
" You can talk or you can act, but you can't do both. If someone hasn't done anything except talk for a while, do something to move the story forward." + \
" If the conversation has reached a resolution, take an action to move the story forward. " + \
" In most situations you should probably narrow your focus to interactions between one object or person, two or three at the most."

            # (c) Call /do
            if _VERBOSE:
                print(f"\nCharacter '{char_obj.name}' is speaking with query:\n{query}")
                print("Using prompt:")
                print(final_prompt)

            if len(query) == "":
                query = "Your new companions are standing around you, but no one has said anything yet."

            payload = {
                "query": query,
                "prompt": final_prompt
            }
            do_resp = requests.post(f"{AI_CALLER_URL}/do", json=payload)
            if do_resp.status_code != 200:
                print(f"Error calling /do for {char_obj.name}: {do_resp.status_code}")
                print(do_resp.text)
                continue

            do_data = do_resp.json()
            ai_response = do_data.get("result", "")

            print(f"[{char_obj.name.upper()}]: {ai_response}")
            print("---------------------")
            speak(ai_response, char_obj.voice, char_obj.name)

            # Add this new line to the *other* characters' unread_messages
            # Create a new Message with source = char_obj.name
            new_msg = Message(source=char_obj.name, message=ai_response)
            for other_name, other_obj in all_characters.items():
                if other_name != char_name:
                    other_obj.unread_messages.append(new_msg)
            DM_unread.append(new_msg)

            # We'll POST to /write-json/{base_name} with the updated content.
            save_url = f"{FILE_MANAGER_URL}/write-json/{char_obj.name}"
            # Construct the JSON we want to write:
            #   name, prompt -> core, flux, memories, etc.
            # If you want to store more fields (ID, unread_messages, etc.) 
            # you can also include them if your file_manager schema allows it.
            save_data = {
                "name": char_obj.name,
                "prompt": {
                    "core": char_obj.prompt.core,
                    "flux": char_obj.prompt.flux,
                    "memories": char_obj.prompt.memories
                },
                "voice": char_obj.voice,
            }

            save_resp = requests.post(save_url, json=save_data)
            if save_resp.status_code != 200:
                print(f"Error saving JSON for {char_obj.name}: {save_resp.status_code}")
                print(save_resp.text)
            else:
                if _VERBOSE:
                    print(f"Updated JSON saved for '{char_obj.name}' -> {char_obj}.json")
            
            # We then clear the unread_messages because they've been "consumed"
            char_obj.unread_messages.clear()
            # input()

    if _VERBOSE:
        print("\n--- All done! ---")
        # Optionally, you can print out the final state of each character's unread_messages
        # to confirm that each one has a new message from whoever spoke last.
        for char_name, char_obj in all_characters.items():
            print(f"Character '{char_name}' has {len(char_obj.unread_messages)} unread messages:")
            for msg in char_obj.unread_messages:
                print(f"  - {msg.source}: {msg.message}")
if __name__ == "__main__":
    main()
