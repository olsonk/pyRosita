class Head:
    """A head that can TURN, NOD, and ROLL"""
    def __init__(self):
        self.turn = 1800
        self.nod = 1800
        self.roll = 1800
    
    def get_values(self):
        return {"Head Turn": self.turn, "Head Nod": self.nod, "Head Roll": self.roll}
    
    def reset(self):
        self.turn = 1800
        self.nod = 1800
        self.roll = 1800
        return self.get_values()
    
    def move(self, x, y):
        string = ""
        time = 0.40
		# map x/100 to total range of possible values. Add min value to mapX to get new value
        mapX = round(x / 100 * 900)
        mapY = round(y / 100 * 600)
        if 1350.0+mapX != self.turn:
            diff = self.turn - (1350+mapY)
            if abs(diff) > 200 and abs(diff) < 400:
                time = 0.50
            elif abs(diff) > 400:
                time = 0.75
            self.turn = 1350 + mapX
            string += "Head Turn={}\n".format(self.turn)
        if 1500.0+mapY != self.nod:
            diff = self.nod - (1500+mapY)
            if abs(diff) > 200 and abs(diff) < 400:
                time = 0.50
            elif abs(diff) > 400:
                time = 0.75
            self.nod = 1500 + mapY
            string += "Head Nod={}\n".format(self.nod)
        return [string, time]

class Torso:
    """A torso that can BEND FORWARD, bend SIDEWAYS, or twist/TURN"""
    def __init__(self):
        self.bendForward = 1800
        self.sideways = 1800
        self.turn = 1800
        
    def get_values(self):
        return {"Torso Bend Forward": self.bendForward, "Torso Sideways": self.sideways, "Torso Turn": self.turn}
    
    def reset(self):
        self.bendForward = 1800
        self.sideways = 1800
        self.turn = 1800
        return self.get_values()
    
    def move(self, x=0, y=0):
        string = ""
        time = 0.40
        mapX = round(x / 100 * 400)
        mapY = round(y / 100 * 300)
        if 1600.0+mapX != self.turn:
            diff = self.turn - (1600+mapX)
            if abs(diff) > 100 and abs(diff) <= 200:
                time = 0.75
            elif abs(diff) > 200 and abs(diff) < 300:
                time = 1.5
            elif abs(diff) >= 300:
                time = 2
            self.turn = 1600 + mapX
            string += "Torso Turn={}\n".format(self.turn)
        if 1950.0-mapY != self.bendForward:
            diff = self.bendForward - (1950-mapY)
            if abs(diff) > 200 and abs(diff) < 400:
                time = 0.50
            elif abs(diff) > 400:
                time = 0.75
            self.bendForward = 1950 - mapY
            string += "Torso Bend Forward={}\n".format(self.bendForward)
        return [string, time]

class Arm:
    """An arm with a SIDE (left/right). Can go UP, OUT, TWIST at the shoulder, rotate/twist the FORE ARM, bend at the ELBOW, and bend at the WRIST"""
    def __init__(self, side):
        self.side = side
        self.up = 950
        self.out = 950
        self.twist = 1800
        self.foreArm = 1800
        self.elbow = 1350
        self.wrist = 1800
        
    def get_values(self):
        return {"{} Arm Up".format(self.side): self.up,
                "{} Arm Out".format(self.side): self.out,
                "{} Arm Twist".format(self.side): self.twist,
                "{} Fore Arm Rotate".format(self.side): self.foreArm,
                "{} Arm Elbow".format(self.side): self.elbow,
                "{} Arm Wrist".format(self.side): self.wrist
                }
    
    def reset(self):
        self.up = 950
        self.out = 950
        self.twist = 1800
        self.foreArm = 1800
        self.elbow = 1350
        self.wrist = 1800
        return self.get_values()
    
    def move(self, x=0, y=0):
        string = ""
        time = 0.40
        mapX = round(x / 100 * 530)
        mapY = round(y / 100 * 1000)
        elbow = round(1.05 ** y * 4)
        if 900+mapY != self.up:
            diff = self.up - (900+mapY)
            if abs(diff) > 200 and abs(diff) < 300:
                time = 0.50
            elif abs(diff) > 300 and abs(diff) < 500:
                time = 0.75
            else:
                time = 1.25
            self.up = 900+mapY
            self.elbow = 1350+elbow
            string += "{} Arm Elbow={}\n".format(self.side, self.elbow)
            string += "{} Arm Up={}\n".format(self.side, self.up)
        if 920+mapX != self.out:
            diff = self.out - (920+mapX)
            if abs(diff) > 200 and abs(diff) < 400:
                time = 0.50
            elif abs(diff) > 400:
                time = 0.75
            self.out = 920+mapX
            string += "{} Arm Out={}\n".format(self.side, self.out)
        return [string, time]
	
    def bend_elbow(self, amt):
	    string = ""

class Hand:
    """A hand with a SIDE (left/right). Can open/close its INDEX, MIDDLE, RING, or BABY fingers"""
    def __init__(self, side):
        self.side = side
        self.index = 0
        self.middle = 0
        self.ring = 0
        self.baby = 0
        
    def get_values(self):
        return {"{} Finger index".format(self.side): self.index,
                "{} Finger middle".format(self.side): self.middle,
                "{} Finger Ring".format(self.side): self.ring,
                "{} Finger Baby".format(self.side): self.baby
                }
    
    def reset(self):
        self.index = 0
        self.middle = 0
        self.ring = 0
        self.baby = 0
        return self.get_values()
    
    def trigger(self):
        if not self.index:
            return [["{} Finger index={}".format(self.side, 1), "{} Finger index={}\n".format(self.side, 0)], 0.40]
        else:
            return [["{} Finger index={}".format(self.side, 0), "{} Finger index={}\n".format(self.side, 1)], 0.40]
    
    def grip(self):
        if not self.middle:
            self.middle = 1
        return ["{} Finger middle={}".format(self.side, self.middle), 0.40]
    
    def drop(self):
        if self.middle:
            self.middle = 0
        return ["{} Finger middle={}".format(self.side, self.middle), 0.40]
    
    def buttonA(self):
        if self.ring:
            self.ring = 0
        else:
            self.ring = 1
        return [["{} Finger ring={}".format(self.side, self.ring), '', "{} Finger ring={}".format(self.side, self.ring - self.ring)], 0.40]
    
    def buttonB(self):
        if self.baby:
            self.baby = 0
        else:
            self.baby = 1
        return [["{} Finger baby={}".format(self.side, self.baby), '', "{} Finger baby={}".format(self.side, self.baby - self.baby)], 0.40]
        
class Robot:
    """A body with a HEAD, TORSO, LEFTARM, RIGHTARM, LEFTHAND, and RIGHTHAND"""
    def __init__(self):
        self.head = Head()
        self.torso = Torso()
        self.leftArm = Arm("L")
        self.rightArm = Arm("R")
        self.leftHand = Hand("L")
        self.rightHand = Hand("R")
    
    def default(self):
        string = ""
        head = self.head.reset()
        for key, value in head.items():
            string += "{}={}\n".format(key, value)
            
        torso = self.torso.reset()
        for key, value in torso.items():
            string += "{}={}\n".format(key, value)
        
        leftArm = self.leftArm.reset()
        for key, value in leftArm.items():
            string += "{}={}\n".format(key, value)
        
        rightArm = self.rightArm.reset()
        for key, value in rightArm.items():
            string += "{}={}\n".format(key, value)
            
        leftHand = self.leftHand.reset()
        for key, value in leftHand.items():
            string += "{}={}\n".format(key, value)
        
        rightHand = self.rightHand.reset()
        for key, value in rightHand.items():
            string += "{}={}\n".format(key, value)
            
        return [string, 0.40]
        
    def look_point_forward(self):
        string = ""
        left = self.leftArm.move(0, 50)
        right = self.rightArm.move(0, 50)
        head = self.head.move(50, 20)
        torso = self.torso.move(50, 50)
        string += left[0] + "\n"
        string += right[0] + "\n"
        string += head[0] + "\n"
        string += torso[0] + '\n'
        
        times = [left[1], right[1], head[1], torso[1]]
        time = max(times)
        
        return [string, time]
    
    def look_point_left(self):
        string = ""
        left = self.leftArm.move(0, 50)
        right = self.rightArm.move(0, 50)
        head = self.head.move(50, 20)
        torso = self.torso.move(100, 50)
        string += left[0] + "\n"
        string += right[0] + "\n"
        string += head[0] + "\n"
        string += torso[0] + '\n'
        times = [left[1], right[1], head[1], torso[1]]
        time = max(times)
        
        return [string, time]
    
    def look_point_right(self):
        string = ""
        left = self.leftArm.move(0, 50)
        right = self.rightArm.move(0, 50)
        head = self.head.move(50, 20)
        torso = self.torso.move(0, 50)
        string += left[0] + "\n"
        string += right[0] + "\n"
        string += head[0] + "\n"
        string += torso[0] + '\n'
        times = [left[1], right[1], head[1], torso[1]]
        time = max(times)
        
        return [string, time]
		
    def left_aim(self, x=0, y=0):
        string = ""
        look_x = round(0.0004*(x-50)**3+50)
        left = self.leftArm.move(x, y)
        right = self.rightArm.move(0, 99)
        head = self.head.move(look_x, y)
        torso = self.torso.move(x, y)
        string += left[0] + '\n'
        string += right[0] + "\n"
        string += head[0] + "\n"
        string += torso[0] + '\n'
        times = [left[1], right[1], head[1], torso[1]]
        time = max(times)
        return [string, time]

    def right_aim(self, x=0, y=0):
        string = ""
        look_x = round(0.0004*(x-50)**3+50)
        right = self.rightArm.move(x, y)
        left = self.leftArm.move(0, 99)
        head = self.head.move(look_x, y)
        torso = self.torso.move(x, y)
        string += left[0] + '\n'
        string += right[0] + "\n"
        string += head[0] + "\n"
        string += torso[0] + '\n'
        times = [left[1], right[1], head[1], torso[1]]
        time = max(times)
        return [string, time]
		
    def triggerBoth(self):
        left = self.leftHand.trigger()
        right = self.rightHand.trigger()
        left_fire = left[0]
        right_fire = right[0]
        fire = left_fire[0] + '\n' + right_fire[0] + '\n'
        release = left_fire[1] + '\n' + right_fire[1] + '\n'
        string = [fire, release]
        
        return [string, 0.40]
    
    def gripBoth(self):
        string = ""
        string += self.leftHand.grip()[0] + "\n"
        string += self.rightHand.grip()[0] + "\n"
        
        return [string, 0.40]
        
    def dropBoth(self):
        string = ""
        string += self.leftHand.drop()[0] + "\n"
        string += self.rightHand.drop()[0] + "\n"
        
        return [string, 0.40]

class Sequencer:
    """A sequencer that writes to a FILE. Has a ROBOT and TIMER to keep track of actions. Uses KEYFRAMES to generate animations. Recognizes ACTIONS to call robot methods"""
    def __init__(self, file):
        self.file = file
        self.robot = Robot()
        self.timer = 0.00
        self.keyframes = {}
        self.actions = {
            'wait': self.wait,
            'default': self.robot.default,
            'head move': self.robot.head.move,
            "look point forward": self.robot.look_point_forward,
            "look point left": self.robot.look_point_left,
            "look point right": self.robot.look_point_right,
			"left aim": self.robot.left_aim,
            "right aim": self.robot.right_aim,
            "right arm move": self.robot.rightArm.move,
            "left arm move": self.robot.leftArm.move,
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
        
        # Check to see which keyword arguments were given with the .add method. Checks common keywords (x, y); if none given, just call the method with no arguments
        if "x" in kwargs and "y" in kwargs:
            response = self.actions[action](kwargs["x"], kwargs["y"])
            response_string = response[0]
            response_timing = response[1]
        elif "time" in kwargs:
            response = self.actions[action](kwargs["time"])
            response_string = response[0]
            response_timing = response[1]
        else:
            response = self.actions[action]()
            response_string = response[0]
            response_timing = response[1]
            
        # if a method returns a list of strings, handle them all here to control timing without holding up the rest of the animation. This will auto-add pauses for things
        # like button presses. If it's an int instead of a string, then wait was called; adjust timer for future events. If it's just a string, add to the keyframes!
        if type(response_string) is list:
            for item in response_string:
                key = "time={0:.2f}".format(self.timer)
                self.keyframes[key] = item
                self.timer += response_timing
        elif type(response_string) is int:
            self.keyframes[key] = ""
            self.timer += response_timing
        else:
            # check to see if there's already a key for the entry. If so, append the next action to the existing key. If not, create a new dict key and value
            try:
                self.keyframes[key] += "\n"+response_string
            except KeyError:
                self.keyframes[key] = response_string
            self.timer += response_timing
        
    def generate_animation(self):
        self.write("[Sequence Header]")
        self.write("name=text-from-python")
        self.write("description=compose_movement")
        self.write("number=2207")
        self.write('length={}'.format(round(self.timer)))
        self.write('[Meta]')
        self.write('robot_model=RoboThespian4')
        self.write('virtualrobot_id=22777')
        self.write('virtualrobot_user=Eldad')
        self.write('virtualrobot_created=2018-07-06T10:49:00.830569+00:00')
        self.write('virtualrobot_modified=2018-07-06T10:49:00.830569+00:00')
        self.write('')
        self.write('[Sequence Events]')
        for frame, value in self.keyframes.items():
            self.write(frame)
            self.write(value)
            
