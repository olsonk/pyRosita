import requests
import pyRosita
import base64
import os
import argparse
import re

# set up a session in order to call the Tritium Web API on Rosita to run the sequence
session = requests.Session()
token = os.environ["TRITIUM_AUTH_TOKEN"]
session.cookies.set("tritium_auth_token", token)

def make_sequence(seq, sequence_file):
    if sequence_file:
        file = open(sequence_file, 'r')
        for line in file.readlines():
            print(line)
            verb = re.match(r'set|change', line).group()
            print("Matched {} from line {}".format(verb, line))
            if verb == None:
                # print help text for fixing error. Must start with either 'set' or 'change'
                pass
            noun = re.search(r'(?: )([a-z_]+)', line).group(1)
            print("Matched {} from line {}".format(noun, line))
            if noun == None:
                # print help text for fixing error. Should also check if this string is
                # in the accepted 'nouns' list (needs to be created)
                pass
            amount = re.search(r'(\([0-9-]+, *[0-9-]+\))|[0-9-]+', line)
            if amount:
                print("Matched {} from line {}".format(amount.group(), line))
                if re.match("\(", amount.group()):
                    x = amount.group().split(",")[0][1:]
                    y = amount.group().split(",")[1][:-1]
                    amount = (int(x), int(y))
                else:
                    amount = int(amount.group())
                seq.add("{} {}".format(verb, noun), amount)
            else:
                seq.add("{} {}".format(verb, noun))
            #print("Received invalid sequence instruction: {}".format(line))
            #print("Instructions must follow this format: <verb> <noun> <amount (optional)>")
            #print("Valid verbs are 'set' or 'change'")
            
            
    else:
        # Edit the filename in the next line to generate new .sequence files
        # MUST end in .sequence!
        filename = 'its-working.sequence'
    
        # build a sequence in the space below, if you're not passing a text file into the program
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
        for i in range(3):
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

def main(sequence_file):
    
    if sequence_file:
        filename = sequence_file.split(".")[0] + ".sequence"
    else:
        filename = "test-no-args.sequence"
    f = open(filename, 'w')
    # Edit the following line to indicate your VirtualRobot username
    user = ""
    # Edit the following line to indicate your VirtualRobot ID
    id = ""
    # Edit the following line to include a short description of what this sequence performs
    description = "The following test runs a variety of motions for about 1 minute"

    rt = pyRosita.Robot()
    seq = pyRosita.Sequencer(f, rt, user, id, description)

    make_sequence(seq, sequence_file)

    seq.generate_animation()
    time_for_animation = round(seq.timer)

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
    
    print("Running end2end.py")
    THIS_FILEPATH = os.path.dirname(os.path.realpath(__file__))
    TEST_RUN_FILEPATH = os.path.join(THIS_FILEPATH, "end2end.py")
    os.system("python \"{}\" {} {}".format(TEST_RUN_FILEPATH, seq.file.name.split(".")[0], time_for_animation))
    
if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--sequence', 
                        help='Specify a text (.txt) file to be played on RoboThespian.')
    args = parser.parse_args()
    sequence_file = args.sequence
    main(sequence_file)