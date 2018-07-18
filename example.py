import requests
import pyRosita

"""
# set up a session in order to call the Tritium Web API on Rosita to run the sequence
session = requests.Session()
session.cookies.set("tritium_auth_token", "")
"""

# Edit the filename in the next line to generate new .sequence files
# MUST end in .sequence!
f = open('change-test.sequence', 'w')
# Edit the following line to indicate your VirtualRobot username
user = ""
# Edit the following line to indicate your VirtualRobot ID
id = ""
# Edit the following line to include a short description of what this sequence performs
description = ""

rt = pyRosita.Robot()
seq = pyRosita.Sequencer(f, rt, user, description, id)

"""
For movements, use numbers between -90 (fully down/right) and 90 (fully up/left)
Actions:
    default (resets robot to default pose)
    wait, time=?
    head move, x=?, y=?
    head nod/turn/roll, amt=?,
    change head nod/turn/roll, amt=? (between -100 and 100)
    torso bend forward/sideways/turn, amt=?
    left/right arm move, x=?, y=?
    left/right up/out/twist/forearm/elbow/wrist, amt=?
	look point forward/left/right
	left/right aim, x=?, y=?
    left/right trigger/grip/buttonA/buttonB
    both trigger/grip/drop
"""
seq.add("default")
seq.add("both grip")
seq.add("look point forward")
seq.add("left aim", x=1500, y=-50)
seq.add("left trigger")
seq.add("change head turn", amt=100)
seq.add("change head turn", amt=-80)
seq.add("both drop")
seq.add("default")

seq.generate_animation()

f.close()

'''
file_to_upload = open("kevintest.sequence")

args = {
    "asset_type_name": "sequence",
    "directory_route": "user/Eldad/",
    "asset_file_name": "kevintest.sequence",
    "file_path": "kevintest.sequence",
}

r = json.dumps(args)
json_r = json.loads(r)
print("JSON dumped args")
print(r)
response = session.post("http://rt-0101.robothespian.co.uk/assets/upload", data=args, files={"kevintest":file_to_upload})

print("Response object")
print(response)
print(response.content)
print("Response Items")
for item in response:
    print(item)
'''