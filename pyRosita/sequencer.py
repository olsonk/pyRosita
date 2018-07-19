from random import randint
from datetime import datetime
        
class Sequencer:
    """Has attr for RoboThespian metadata. Writes sequences to a file recognized by RT.
    
    The Sequencer class is what the user primarily interacts with. Users create an
    instance and add movements using the .add() method. These are appended to a 
    keyframes dictionary, which gives timing and device instructions in a format
    recognized by RoboThespian. When the sequence is completed, the user calls
    generate_animation() to write all of the instructions to the file, which can
    then be uploaded and played on Rosita.
    
    Attributes
    ----------
    file : File object
        A File instance that is written to by generate_animation()
    robot : Robot object
        The robot being commanded by the sequencer. See rt_hardware for details
    user : string
        VirtualRobot username, for organizing .sequence files & viewing in VirtualRobot
    id : int
        VirtualRobot username id,  for organizing on VirtualRobot
    description : string
        A brief description of what the animation does or is used for
    sequence_id : int
        A 5-digit identifier for the sequence, used by VirtualRobot GUI
    created : string
        A string-formatted "datetime" timestamp, used by VirtualRobot GUI
    modified : string
        A string-formatted "datetime" timestamp, used by VirtualRobot GUI
    timer : int
        Timer used for the KEY of keyframes dict. Begins at 0.00
    keyframes : dict
        Keeps track of animation. KEY is timer, VALUE is string of instructions
    actions : dict
        A mapping of accepted strings from .add() method to actual robot commands
    
    """
    def __init__(self, file, robot, user, id, description):
        self.file = file
        self.robot = robot
        self.user = user
        self.id = id
        self.description = description
        self.sequence_id = randint(0, 99999)
        self.created = datetime.now().strftime("%Y-%m-%dT%I:%M.%S")
        self.modified = datetime.now().strftime("%Y-%m-%dT%I:%M.%S")
        self.timer = 0.00
        self.keyframes = {}
        self.actions = {
            'wait': self.wait,
            'default': self.robot.default,
            'head move': self.robot.head.move,
            'head nod': self.robot.head.set_nod,
            'head turn': self.robot.head.set_turn,
            'head roll': self.robot.head.set_roll,
            "change head nod": self.robot.head.change_nod,
            "change head turn": self.robot.head.change_turn,
            "change head roll": self.robot.head.change_roll,
            'torso bend forward': self.robot.torso.set_bendForward,
            'torso sideways': self.robot.torso.set_sideways,
            'torso turn': self.robot.torso.set_turn,
            'change torso bend forward': self.robot.torso.change_bendForward,
            'change torso sideways': self.robot.torso.change_sideways,
            'change torso turn': self.robot.torso.change_turn,
            "look point forward": self.robot.look_point_forward,
            "look point left": self.robot.look_point_left,
            "look point right": self.robot.look_point_right,
			"left aim": self.robot.left_aim,
            "right aim": self.robot.right_aim,
            "right arm move": self.robot.rightArm.move,
            "left arm move": self.robot.leftArm.move,
            "left up": self.robot.leftArm.set_up,
            "right up": self.robot.rightArm.set_up,
            "left out": self.robot.leftArm.set_out,
            "right out": self.robot.rightArm.set_out,
            "left twist": self.robot.leftArm.set_twist,
            "right twist": self.robot.rightArm.set_twist,
            "left forearm": self.robot.leftArm.set_foreArm,
            "right forearm": self.robot.rightArm.set_foreArm,
            "left elbow": self.robot.leftArm.set_elbow,
            "right elbow": self.robot.rightArm.set_elbow,
            "left wrist": self.robot.leftArm.set_wrist,
            "right wrist": self.robot.rightArm.set_wrist,
            "change left arm up": self.robot.leftArm.change_up,
            "change right arm up": self.robot.rightArm.change_up,
            "change left arm out": self.robot.leftArm.change_out,
            "change right arm out": self.robot.rightArm.change_out,
            "change left arm twist": self.robot.leftArm.change_twist,
            "change right arm twist": self.robot.rightArm.change_twist,
            "change left forearm": self.robot.leftArm.change_foreArm,
            "change right forearm": self.robot.rightArm.change_foreArm,
            "change left elbow": self.robot.leftArm.change_elbow,
            "change right elbow": self.robot.rightArm.change_elbow,
            "change left wrist": self.robot.leftArm.change_wrist,
            "change right wrist": self.robot.rightArm.change_wrist,
            "left trigger": self.robot.leftHand.trigger,
            "right trigger": self.robot.rightHand.trigger,
            "both trigger": self.robot.triggerBoth,
            "left grip": self.robot.leftHand.grip,
            "right grip": self.robot.rightHand.grip,
            "both grip": self.robot.gripBoth,
            "both drop": self.robot.dropBoth,
            "left drop": self.robot.leftHand.drop,
            "right drop": self.robot.rightHand.drop,
            "left buttonA": self.robot.leftHand.buttonA,
            "right buttonA": self.robot.rightHand.buttonA,
            "left buttonB": self.robot.leftHand.buttonB,
            "right buttonB": self.robot.rightHand.buttonB,
            }
    
    def write(self, content):
        """Writes content to file, auto-appending newline to insert line breaks
        
        This helper method simply adds the newline character to content so that
        the file is neatly formatted and organized.
        
        """
        self.file.write(content + '\n')
    
    def wait(self, time):
        """Return a list of two int representing how long to pause the animation
        
        Parameters
        ----------
        time : int
            The amount of time, in seconds, to pause the animation
        
        Returns
        -------
        list
            0: int
            1: int
        
        """
        return [time, time]
    
    def add(self, action, *args, **kwargs):
        """Adds new Key/Value pairs to keyframes attr
        
        This is the primary method of the Sequencer. It takes in a string and
        keyword arguments, identifies the robot commands to issue, passes along
        relevant arguments, and stores the response. Then, for each element in the
        response, it generates a new key/value pair in the keyframes dict with a
        timer value and string of necessary .sequence commands.
        
        Parameters
        ----------
        action : string
            The user-defined action to add to the animation. Should be in the form of
            ("<verb> <noun>", kwargs). Acceptable verbs are "set" or "change". Nouns
            must be in the form of "left_arm_up", "head_nod", "both_hands_grip", etc.
        kwargs : kw=(int)
            Keyword arguments must be either x=__, y=__, time=__, or amt=__ . Values
            must be int.
        
        """
        # create the key for this dict entry. Keys should always be time signatures for the keyframe animation
        key = "time={0:.2f}".format(self.timer)
        
        command = action.split(" ")
        verb = command[0]
        noun = command[1]
        
        if verb == "set":
            if noun == "default":
                response = self.robot.default()
            elif noun == "wait" or noun == "pause":
                response = self.wait(args[0])
            elif "head_" in noun:
                part = noun.split("head_")[1]
                if len(args) == 1 and type(args[0]) == int:
                    response = self.robot.head.set(part, args[0])
                elif "amt" in kwargs:
                    response = self.robot.head.set(part, kwargs["amt"])
                else:
                    print("'{}' requires an 'amt' value that is an int between 0 and 100.".format(action))
                    print("Try again in this format: seq.add('{}', <int>)".format(action))
            elif "torso_" in noun:
                part = noun.split("torso_")[1]
                if len(args) == 1 and type(args[0]) == int:
                    response = self.robot.torso.set(part, args[0])
                elif "amt" in kwargs:
                    response = self.robot.torso.set(part, kwargs["amt"])
                    
                else:
                    print("'{}' requires an 'amt' value that is an int between 0 and 100.".format(action))
                    print("Try again in this format: seq.add('{}', <int>)".format(action))
            elif "left_arm_" in noun:
                part = noun.split("left_arm_")[1]
                if part == "aim":
                    x = args[0][0]
                    y = args[0][1]
                    print("AIM called with x={} y={}".format(x, y))
                    response = self.robot.left_aim(x, y)
                elif len(args) == 1 and type(args[0]) == int:
                    response = self.robot.leftArm.set(part, args[0])
                elif "amt" in kwargs:
                    response = self.robot.leftArm.set(part, kwargs["amt"])
                else:
                    print("'{}' requires an 'amt' value that is an int between 0 and 100.".format(action))
                    print("Try again in this format: seq.add('{}', <int>)".format(action))
            elif "right_arm_" in noun:
                part = noun.split("right_arm_")[1]
                if part == "aim":
                    x = args[0][0]
                    y = args[0][1]
                    response = self.robot.right_aim(x, y)
                elif len(args) == 1 and type(args[0]) == int:
                    response = self.robot.rightArm.set(part, args[0])
                elif "amt" in kwargs:
                    response = self.robot.rightArm.set(part, kwargs["amt"])
                else:
                    print("'{}' requires an 'amt' value that is an int between 0 and 100.".format(action))
                    print("Try again in this format: seq.add('{}', <int>)".format(action))
            elif noun == "left_trigger":
                response = self.robot.leftHand.trigger()
            elif noun == "right_trigger":
                response = self.robot.rightHand.trigger()
            elif noun == "both_trigger":
                response = self.robot.triggerBoth()
            elif noun == "left_grip":
                response = self.robot.leftHand.grip()
            elif noun == "right_grip":
                response = self.robot.rightHand.grip()
            elif noun == "both_grip":
                response = self.robot.gripBoth()
            elif noun == "left_drop":
                response = self.robot.leftHand.drop()
            elif noun == "right_drop":
                response = self.robot.rightHand.drop()
            elif noun == "both_drop":
                response = self.robot.dropBoth()
            elif noun == "look_point_forward":
                response = self.robot.look_point_forward()
            elif noun == "look_point_left":
                response = self.robot.look_point_left()
            elif noun == "look_point_right":
                response = self.robot.look_point_right()
        elif verb == "change":
            if "head_" in noun:
                part = noun.split("head_")[1]
                if len(args) == 1 and type(args[0]) == int:
                    response = self.robot.head.change(part, args[0])
                elif "amt" in kwargs:
                    response = self.robot.head.change(part, kwargs["amt"])
                else:
                    print("'{}' requires an 'amt' value that is an int between -100 and 100.".format(action))
                    print("Try again in this format: seq.add('{}', <int>)".format(action))
            elif "torso_" in noun:
                part = noun.split("torso_")[1]
                if len(args) == 1 and type(args[0]) == int:
                    response = self.robot.torso.change(part, args[0])
                elif "amt" in kwargs:
                    response = self.robot.torso.change(part, kwargs["amt"])
                    
                else:
                    print("'{}' requires an 'amt' value that is an int between -100 and 100.".format(action))
                    print("Try again in this format: seq.add('{}', <int>)".format(action))
            elif "left_arm_" in noun:
                part = noun.split("left_arm_")[1]
                if len(args) == 1 and type(args[0]) == int:
                    response = self.robot.leftArm.change(part, args[0])
                elif "amt" in kwargs:
                    response = self.robot.leftArm.change(part, kwargs["amt"])
                else:
                    print("'{}' requires an 'amt' value that is an int between -100 and 100.".format(action))
                    print("Try again in this format: seq.add('{}', <int>)".format(action))
            elif "right_arm_" in noun:
                part = noun.split("right_arm_")[1]
                if len(args) == 1 and type(args[0]) == int:
                    response = self.robot.rightArm.change(part, args[0])
                elif "amt" in kwargs:
                    response = self.robot.rightArm.change(part, kwargs["amt"])
                else:
                    print("'{}' requires an 'amt' value that is an int between -100 and 100.".format(action))
                    print("Try again in this format: seq.add('{}', <int>)".format(action))
        response_string = response[0]
        response_timing = response[1]
            
        # if a method returns a list of strings, handle them all here to control timing without holding up the 
        # rest of the animation. This will auto-add pauses for things like button presses. If it's an int
        # instead of a string, then wait was called; adjust timer for future events. If it's just a string, 
        # add to the keyframes!
        if type(response_string) is list:
            for item in response_string:
                key = "time={0:.2f}".format(self.timer)
                self.keyframes[key] = item
                self.timer += response_timing
        elif type(response_string) is int:
            self.keyframes[key] = ""
            self.timer += response_timing
        else:
            # check to see if there's already a key for the entry. If so, append the next action to the existing 
            # key. If not, create a new dict key and value
            try:
                self.keyframes[key] += "\n"+response_string
            except KeyError:
                self.keyframes[key] = response_string
            self.timer += response_timing
        
    def generate_animation(self):
        """Outputs text to the file given on instantiation. Call after done using .add()
        
        This method actually writes to the .sequence file. It first writes metadata
        for the VirtualRobot/RoboThespian visual interfaces to keep organized. It then
        iterates over the keyframes attribute to write headings for each keyframe in
        the format of "time=0.00" and then write robot commands that can be read by
        RoboThespian ("L Arm Out=1800")
        
        """
        self.write("[Sequence Header]")
        self.write("name={}".format(self.file.name.split(".")[0]))
        self.write("description={}".format(self.description))
        self.write("number={}".format(self.sequence_id))
        self.write('length={}'.format(round(self.timer)))
        self.write('[Meta]')
        self.write('robot_model=RoboThespian4')
        self.write('virtualrobot_id={}'.format(self.id))
        self.write('virtualrobot_user={}'.format(self.user))
        self.write('virtualrobot_created={}'.format(self.created))
        self.write('virtualrobot_modified={}'.format(self.modified))
        self.write('')
        self.write('[Sequence Events]')
        for frame, value in self.keyframes.items():
            self.write(frame)
            self.write(value)
            
