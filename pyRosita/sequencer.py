from random import randint
from datetime import datetime
        
class Sequencer:
    """A sequencer that writes to a FILE. Has a ROBOT and TIMER to keep track of actions. Uses KEYFRAMES 
       to generate animations. Recognizes ACTIONS to call robot methods"""
    def __init__(self, file, robot, user, id, description):
        self.file = file
        self.robot = robot
        self.user = user
        self.id = id
        self.description = description
        self.sequence_id = randint(0, 99999)
        self.created = datetime.now().strftime("%Y-%m-%dT%I:%M.%S")
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
        self.file.write(content + '\n')
    
    def wait(self, time):
        return [time, time]
    
    def add(self, action, **kwargs):
        # create the key for this dict entry. Keys should always be time signatures for the keyframe animation
        key = "time={0:.2f}".format(self.timer)
        
        # Check to see which keyword arguments were given with the .add method. Checks common keywords (x, y); 
        # if none given, just call the method with no arguments
        if "x" in kwargs and "y" in kwargs:
            response = self.actions[action](kwargs["x"], kwargs["y"])
        elif "time" in kwargs:
            response = self.actions[action](kwargs["time"])
        elif "amt" in kwargs:
            response = self.actions[action](kwargs["amt"])
        else:
            response = self.actions[action]()
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
        self.write('virtualrobot_modified={}'.format(self.created))
        self.write('')
        self.write('[Sequence Events]')
        for frame, value in self.keyframes.items():
            self.write(frame)
            self.write(value)
            
