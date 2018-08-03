import requests
import pyRosita
from pathlib import Path
import base64

# set up a session in order to call the Tritium Web API on Rosita to run the sequence
session = requests.Session()
session.cookies.set("tritium_auth_token", "")


# Edit the filename in the next line to generate new .sequence files
# MUST end in .sequence!
filename = 'its-working.sequence'

f = open(filename, 'w')
# Edit the following line to indicate your VirtualRobot username
user = ""
# Edit the following line to indicate your VirtualRobot ID
id = ""
# Edit the following line to include a short description of what this sequence performs
description = "The following test runs a variety of motions for about 1 minute"

rt = pyRosita.Robot()
seq = pyRosita.Sequencer(f, rt, user, description, id)

"""
To add movements to the animation, use seq.add("<verb> <noun>", <int or tuple>)
Acceptable verbs are "set" or "change"
Acceptable nouns are snake_case robot commands:
    default
    wait
    look_point_forward/left/right
    head_move
    head_nod/turn/roll
    torso_move
    torso_sideways/turn/bend_forward
    right/left_arm_aim/move
    right/left_arm_up/out/twist/elbow/wrist/fore_arm
    both/right/left_trigger/grip/drop/buttonA/buttonB
Arguments may either be tuples (for x,y actions like "aim" or "move"), or ints
    "set" ints should be between 0 and 100
    "change" ints should be between -100 and 100
"""

seq.add("set default")
seq.add("set both_grip")
seq.add("set look_point_forward")
seq.add("set both_trigger")
seq.add("set left_arm_aim", (100,50))
seq.add("set left_trigger")
seq.add("change torso_turn", -60)
seq.add("set left_trigger")
seq.add("change torso_turn", -30)
seq.add("set left_trigger")
seq.add("change torso_turn", 50)
seq.add("set left_trigger")
seq.add("change torso_turn", 30)
seq.add("set left_trigger")
seq.add("set right_arm_aim", (50, 70))
seq.add("set right_trigger")
seq.add("set right_arm_aim", (50,-30))
seq.add("set right_trigger")
seq.add("change torso_turn", -40)
seq.add("set right_trigger")
seq.add('set left_arm_aim', (50, 50))
seq.add('set left_trigger')
seq.add('set right_arm_aim', (50, 50))
seq.add('set right_trigger')
seq.add("set both_drop")
seq.add("set default")

seq.generate_animation()

f.close()
f = open(filename, 'rb')

# Files uploaded to RoboThespian must be base64-encoded strings
# Encode the file, then decode to ascii to send over
file_data = f.read()
file_decoded = base64.b64encode(file_data).decode('ascii')

upload_url = "https://rt-0101.robothespian.co.uk/tritium/asset_manager/assets"

data = {'file_data_base64': file_decoded,
        'asset_type_name': 'sequence',
        'directory_route': 'user/',
        'asset_file_name': filename
        }

response = session.post(upload_url, json=data)

print("Response object")
print(response)
print(response.content)
print("Response Items")
for item in response:
    print(item)
f.close()