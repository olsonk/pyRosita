def check_timing(diff):
    """Check the timing of the requested movement. Accepts *diff* between current position and requested position"""
    time = 0.0
    if abs(diff) > 100 and abs(diff) < 200:
        time = 0.50
    elif abs(diff) > 200 and abs(diff) < 300:
        time = 1.5
    elif abs(diff) >= 300:
        time = 2
    return time

class Head:
    """Has nod, turn, and roll attr. Can set_ or change_ any of these attr, given an amt
    
    The Head class has three movements: nod (up and down), turn (left and right), and 
    roll (tilt left/right). Each of these values has a min and max value. This class
    also includes methods for getting current values, resetting them to 'default' 
    position, a complex 'move' method for changing the nod and turn, and set_ / change_
    methods for granular control of each attribute.
    
    Attributes
    ----------
    turn : int
        The left/right motion of the head. Defaults to 1800 (center).
    nod : int
        The up/down motion of the head. Defaults to 1800 (horizontal).
    roll : int
        The tilt motion of the head. Defaults to 1800 (no tilt).
    TURN_MAX : int
        The maximum turn amount. Constant 2250
    TURN_MIN : int
        The minimum turn amount. Constant 1350
    TURN_RANGE : int
        The difference between TURN_MAX and TURN_MIN.
    NOD_MAX : int
        The maximum nod amount. Constant 2100
    NOD_MIN : int
        The minimum nod amount. Constant 1500
    NOD_RANGE : int
        The difference between NOD_MAX and NOD_MIN.
    ROLL_MAX : int
        The maximum roll amount. Constant 2000
    ROLL_MIN : int
        The minimum roll amount. Constant 1600
    ROLL_RANGE : int
        The difference between ROLL_MAX and ROLL_MIN.
    
    """
    def __init__(self):
        self.turn = 1800
        self.nod = 1800
        self.roll = 1800
        
        # set up max/min/range attribute values
        self.TURN_MAX = 2250
        self.TURN_MIN = 1350
        self.TURN_RANGE = self.TURN_MAX - self.TURN_MIN
        self.NOD_MAX = 2100
        self.NOD_MIN = 1500
        self.NOD_RANGE = self.NOD_MAX - self.NOD_MIN
        self.ROLL_MAX = 2000
        self.ROLL_MIN = 1600
        self.ROLL_RANGE = self.ROLL_MAX - self.ROLL_MIN
    
    def get_values(self):
        """Return a dict of all current attribute names and values
        
        Returns
        -------
        dict
            Key: Attribute name, in a format ready to be added to .sequence file
            Value: value of the specified attribute
        
        """
        return {"Head Turn": self.turn, "Head Nod": self.nod, "Head Roll": self.roll}
    
    def reset(self):
        """Set all attr back to default values; return a dict of all attr names and values
        
        Returns
        -------
        dict
            Key: Attribute name, in a format ready to be added to .sequence file
            Value: default value of the specified attribute`
        
        """
        self.turn = 1800
        self.nod = 1800
        self.roll = 1800
        return self.get_values()
    
    def move(self, x, y):
        """Change head nod and turn values and return a list with a string and int
        
        Parameters
        ----------
        x : int
            The requested 'turn' value. Must be between 0 and 100.
        y : int
            The requested 'nod' value. Must be between 0 and 100.
            
        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        
        """
        # string defaults to empty if nod and turn were already at requested values
        string = ""
        
        # timing for all movements defaults to 0.40 sec
        time = 0.40
        
		# Convert requested x and y values to percentages of possible nod/turn range
        mapX = round(x / 100 * self.TURN_RANGE)
        mapY = round(y / 100 * self.NOD_RANGE)
        
        # Check if requested position is already the current position
        if self.TURN_MIN+mapX != self.turn:
            # determine the amount of distance that will be moved
            diff = self.turn - (self.TURN_MIN+mapY)
            
            # determine the time necessary to move this amount, set time to that value
            time = check_timing(diff)
            
            # set turn to new value
            self.turn = self.TURN_MIN + mapX
            
            # append string with instructions for the sequence file
            string += "Head Turn={}\n".format(self.turn)
                
        # same as above, but for 'nod' positions
        if self.NOD_MIN+mapY != self.nod:
            diff = self.nod - (self.NOD_MIN+mapY)
            if abs(diff) > 200 and abs(diff) < 400:
                time = 0.50
            elif abs(diff) > 400:
                time = 0.75
            self.nod = self.NOD_MIN + mapY
            string += "Head Nod={}\n".format(self.nod)
            
        return [string, time]
        
    def set_nod(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.NOD_RANGE)
        if self.nod != self.NOD_MIN+map:
            diff = self.nod - (self.NOD_MIN+map)
            time = check_timing(diff)
            self.nod = self.NOD_MIN + map
            string += "Head Nod={}\n".format(self.nod)
        return [string, time]
        
    def set_turn(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.TURN_RANGE)
        if self.turn != self.TURN_MIN+map:
            diff = self.turn - (self.TURN_MIN+map)
            time = check_timing(diff)
            self.turn = self.TURN_MIN + map
            string += "Head Turn={}\n".format(self.turn)
        return [string, time]
        
    def set_roll(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.ROLL_RANGE)
        if self.roll != self.ROLL_MIN+map:
            diff = self.roll - (self.ROLL_MIN+map)
            time = check_timing(diff)
            self.roll = self.ROLL_MIN + map
            string += "Head Roll={}\n".format(self.roll)
        return [string, time]
    
    def change_nod(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.NOD_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.nod+map <= self.NOD_MAX and self.nod+map >= self.NOD_MIN:
                self.nod += map
            elif self.nod+map > self.NOD_MAX:
                self.nod = self.NOD_MAX
                print("Went past maximum 'nod' value; setting 'nod' to max.")
            elif self.nod+map < self.NOD_MIN:
                self.nod = self.NOD_MIN
                print("Went past minimum 'nod' value; setting 'nod' to min.")
            string += "Head Nod={}\n".format(self.nod)
        return [string, time]
        
    def change_turn(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.TURN_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.turn+map <= self.TURN_MAX and self.turn+map >= self.TURN_MIN:
                self.turn += map
            elif self.turn+map > self.TURN_MAX:
                self.turn = self.TURN_MAX
                print("Went past maximum 'turn' value; setting 'turn' to max.")
            elif self.turn+map < self.TURN_MIN:
                self.turn = self.TURN_MIN
                print("Went past minimum 'turn' value; setting 'turn' to min.")
            string += "Head Turn={}\n".format(self.turn)
        return [string, time]
        
    def change_roll(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.ROLL_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.roll+map <= self.ROLL_MAX and self.roll+map >= self.ROLL_MIN:
                self.roll += map
            elif self.roll+map > self.ROLL_MAX:
                self.roll = self.ROLL_MAX
                print("Went past maximum 'roll' value; setting 'roll' to max.")
            elif self.roll+map < self.ROLL_MIN:
                self.roll = self.ROLL_MIN
                print("Went past minimum 'roll' value; setting 'roll' to min.")
            string += "Head Roll={}\n".format(self.roll)
        return [string, time]
        
class Torso:
    """A torso that can BEND FORWARD, bend SIDEWAYS, or twist/TURN"""
    def __init__(self):
        self.bendForward = 1800
        self.sideways = 1800
        self.turn = 1800
        
        # Set up attribute min/max/range values
        self.BENDFORWARD_MAX = 1950
        self.BENDFORWARD_MIN = 1650
        self.BENDFORWARD_RANGE = self.BENDFORWARD_MAX - self.BENDFORWARD_MIN
        self.SIDEWAYS_MAX = 1860
        self.SIDEWAYS_MIN = 1740
        self.SIDEWAYS_RANGE = self.SIDEWAYS_MAX - self.SIDEWAYS_MIN
        self.TURN_MAX = 2000
        self.TURN_MIN = 1600
        self.TURN_RANGE = self.TURN_MAX - self.TURN_MIN
        
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
        mapX = round(x / 100 * self.TURN_RANGE)
        mapY = round(y / 100 * self.BENDFORWARD_RANGE)
        if self.TURN_MIN+mapX != self.turn:
            diff = self.turn - (self.TURN_MIN+mapX)
            time = check_timing(diff)
            self.turn = self.TURN_MIN + mapX
            string += "Torso Turn={}\n".format(self.turn)
        if self.BENDFORWARD_MAX-mapY != self.bendForward:
            diff = self.bendForward - (self.BENDFORWARD_MAX-mapY)
            if abs(diff) > 200 and abs(diff) < 400:
                time = 0.50
            elif abs(diff) > 400:
                time = 0.75
            self.bendForward = self.BENDFORWARD_MAX - mapY
            string += "Torso Bend Forward={}\n".format(self.bendForward)
        return [string, time]
        
    def set_turn(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.TURN_RANGE)
        if self.turn != self.TURN_MIN+map:
            diff = self.turn - (self.TURN_MIN+map)
            time = check_timing(diff)
            self.turn = self.TURN_MIN + map
            string += "Torso Turn={}\n".format(self.turn)
        return [string, time]
        
    def set_bendForward(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.BENDFORWARD_RANGE)
        if self.bendForward != self.BENDFORWARD_MIN+map:
            diff = self.bendForward - (self.BENDFORWARD_MIN+map)
            time = check_timing(diff)
            self.bendForward = self.BENDFORWARD_MIN + map
            string += "Torso Bend Forward={}\n".format(self.bendForward)
        return [string, time]
        
    def set_sideways(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.SIDEWAYS_RANGE)
        if self.sideways != self.SIDEWAYS_MIN+map:
            diff = self.sideways - (self.SIDEWAYS_MIN+map)
            time = check_timing(diff)
            self.sideways = self.SIDEWAYS_MIN + map
            string += "Torso Sidways={}\n".format(self.sideways)
        return [string, time]

    def change_turn(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.TURN_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.turn+map <= self.TURN_MAX and self.turn+map >= self.TURN_MIN:
                self.turn += map
            elif self.turn+map > self.TURN_MAX:
                self.turn = self.TURN_MAX
                print("Went past maximum 'turn' value; setting 'turn' to max.")
            elif self.turn+map < self.TURN_MIN:
                self.turn = self.TURN_MIN
                print("Went past minimum 'turn' value; setting 'turn' to min.")
            string += "Torso Turn={}\n".format(self.turn)
        return [string, time]
    
    def change_bendForward(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.BENDFORWARD_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.bendForward+map <= self.BENDFORWARD_MAX and self.bendForward+map >= self.BENDFORWARD_MIN:
                self.bendForward += map
            elif self.bendForward+map > self.BENDFORWARD_MAX:
                self.bendForward = self.BENDFORWARD_MAX
                print("Went past maximum 'bendForward' value; setting 'bendForward' to max.")
            elif self.bendForward+map < self.BENDFORWARD_MIN:
                self.bendForward = self.BENDFORWARD_MIN
                print("Went past minimum 'bendForward' value; setting 'bendForward' to min.")
            string += "Torso Bend Forward={}\n".format(self.bendForward)
        return [string, time]
        
    def change_sideways(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.SIDEWAYS_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.sideways+map <= self.SIDEWAYS_MAX and self.sideways+map >= self.SIDEWAYS_MIN:
                self.sideways += map
            elif self.sideways+map > self.SIDEWAYS_MAX:
                self.sideways = self.SIDEWAYS_MAX
                print("Went past maximum 'sideways' value; setting 'sideways' to max.")
            elif self.sideways+map < self.SIDEWAYS_MIN:
                self.sideways = self.SIDEWAYS_MIN
                print("Went past minimum 'sideways' value; setting 'sideways' to min.")
            string += "Torso Sideways={}\n".format(self.sideways)
        return [string, time]
    
class Arm:
    """An arm with a SIDE (left/right). Can go UP, OUT, TWIST at the shoulder, rotate/twist the FORE ARM, 
       bend at the ELBOW, and bend at the WRIST"""
    def __init__(self, side):
        self.side = side
        self.up = 950
        self.out = 950
        self.twist = 1800
        self.foreArm = 1800
        self.elbow = 1350
        self.wrist = 1800
        
		# SET MAX VALUES FOR EACH ATTRIBUTE
        self.UP_MAX = 1900
        self.UP_MIN = 900
        self.UP_RANGE = self.UP_MAX - self.UP_MIN
        self.OUT_MAX = 1450
        self.OUT_MIN = 920
        self.OUT_RANGE = self.OUT_MAX - self.OUT_MIN
        self.TWIST_MAX = 2200
        self.TWIST_MIN = 1700
        self.TWIST_RANGE = self.TWIST_MAX - self.TWIST_MIN
        self.FOREARM_MAX = 2700
        self.FOREARM_MIN = 900
        self.FOREARM_RANGE = self.FOREARM_MAX - self.FOREARM_MIN
        self.ELBOW_MAX = 1900
        self.ELBOW_MIN = 1350
        self.ELBOW_RANGE = self.ELBOW_MAX - self.ELBOW_MIN
        self.WRIST_MAX = 2200
        self.WRIST_MIN = 1400
        self.WRIST_RANGE = self.WRIST_MAX - self.WRIST_MIN
        
    def get_values(self):
        return {"{} Arm Up".format(self.side): self.up,
                "{} Arm Out".format(self.side): self.out,
                "{} Arm Twist".format(self.side): self.twist,
                "{} Fore Arm Rotate".format(self.side): self.foreArm,
                "{} Arm Elbow".format(self.side): self.elbow,
                "{} Arm Wrist".format(self.side): self.wrist
                }
    
    def reset(self):
        self.up = self.UP_MIN
        self.out = self.OUT_MIN
        self.twist = 1800
        self.foreArm = 1800
        self.elbow = self.ELBOW_MIN
        self.wrist = 1800
        return self.get_values()
    
    def move(self, x=0, y=0):
        string = ""
        time = 0.40
        mapX = round(x / 100 * self.OUT_RANGE)
        mapY = round(y / 100 * self.UP_RANGE)
        elbow = round(1.05 ** y * 4)
        twist = round(1.05 ** x * 3.75)
        if self.UP_MIN+mapY != self.up:
            diff = self.up - (self.UP_MIN+mapY)
            time = check_timing(diff)
            self.up = self.UP_MIN+mapY
            self.elbow = self.ELBOW_MIN + elbow
            string += "{} Arm Elbow={}\n".format(self.side, self.elbow)
            string += "{} Arm Up={}\n".format(self.side, self.up)
        if self.OUT_MIN+mapX != self.out:
            diff = self.out - (self.OUT_MIN+mapX)
            time = check_timing(diff)
            self.out = self.OUT_MIN+mapX
            self.twist = self.TWIST_MIN + twist
            string += "{} Arm Out={}\n".format(self.side, self.out)
            string += "{} Arm Twist={}\n".format(self.side, self.twist)
        return [string, time]
	
    def set_up(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.UP_RANGE)
        if self.up != self.UP_MIN+map:
            diff = self.up - (self.UP_MIN+map)
            time = check_timing(diff)
            self.up = self.UP_MIN + map
            string += "{} Arm Up={}\n".format(self.side, self.up)
        return [string, time]
    
    def set_out(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.OUT_RANGE)
        if self.out != self.OUT_MIN+map:
            diff = self.out - (self.OUT_MIN+map)
            time = check_timing(diff)
            self.out = self.OUT_MIN + map
            string += "{} Arm Out={}\n".format(self.side, self.out)
        return [string, time]
    
    def set_twist(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.TWIST_RANGE)
        if self.twist != self.TWIST_MIN+map:
            diff = self.twist - (self.TWIST_MIN+map)
            time = check_timing(diff)
            self.twist = self.TWIST_MIN + map
            string += "{} Arm Twist={}\n".format(self.side, self.twist)
        return [string, time]
        
    def set_foreArm(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.FOREARM_RANGE)
        if self.foreArm != self.FOREARM_MIN+map:
            diff = self.foreArm - (self.FOREARM_MIN+map)
            time = check_timing(diff)
            self.foreArm = self.FOREARM_MIN + map
            string += "{} Fore Arm Rotate={}\n".format(self.side, self.foreArm)
        return [string, time]
    
    def set_elbow(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.ELBOW_RANGE)
        if self.elbow != self.ELBOW_MIN+map:
            diff = self.elbow - (self.ELBOW_MIN+map)
            time = check_timing(diff)
            self.elbow = self.ELBOW_MIN + map
            string += "{} Arm Elbow={}\n".format(self.side, self.elbow)
        return [string, time]
    
    def set_wrist(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.WRIST_RANGE)
        if self.wrist != self.WRIST_MIN+map:
            diff = self.wrist - (self.WRIST_MIN+map)
            time = check_timing(diff)
            self.wrist = self.WRIST_MIN + map
            string += "{} arm Wrist={}\n".format(self.side, self.wrist)
        return [string, time]

    def change_up(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.UP_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.up+map <= self.UP_MAX and self.up+map >= self.UP_MIN:
                self.up += map
            elif self.up+map > self.UP_MAX:
                self.up = self.UP_MAX
                print("Went past maximum 'up' value; setting 'up' to max.")
            elif self.up+map < self.UP_MIN:
                self.up = self.UP_MIN
                print("Went past minimum 'up' value; setting 'up' to min.")
            string += "{} Arm Up={}\n".format(self.side, self.up)
        return [string, time]
        
    def change_out(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.OUT_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.out+map <= self.OUT_MAX and self.out+map >= self.OUT_MIN:
                self.out += map
            elif self.out+map > self.OUT_MAX:
                self.out = self.OUT_MAX
                print("Went past maximum 'out' value; setting 'out' to max.")
            elif self.out+map < self.OUT_MIN:
                self.out = self.OUT_MIN
                print("Went past minimum 'out' value; setting 'out' to min.")
            string += "{} Arm Out={}\n".format(self.side, self.out)
        return [string, time]
        
    def change_twist(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.TWIST_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.twist+map <= self.TWIST_MAX and self.twist+map >= self.TWIST_MIN:
                self.twist += map
            elif self.twist+map > self.TWIST_MAX:
                self.twist = self.TWIST_MAX
                print("Went past maximum 'twist' value; setting 'twist' to max.")
            elif self.twist+map < self.TWIST_MIN:
                self.twist = self.TWIST_MIN
                print("Went past minimum 'twist' value; setting 'twist' to min.")
            string += "{} Arm Twist={}\n".format(self.side, self.twist)
        return [string, time]
        
    def change_foreArm(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.FOREARM_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.foreArm+map <= self.FOREARM_MAX and self.foreArm+map >= self.FOREARM_MIN:
                self.foreArm += map
            elif self.foreArm+map > self.FOREARM_MAX:
                self.foreArm = self.FOREARM_MAX
                print("Went past maximum 'foreArm' value; setting 'foreArm' to max.")
            elif self.foreArm+map < self.FOREARM_MIN:
                self.foreArm = self.FOREARM_MIN
                print("Went past minimum 'foreArm' value; setting 'foreArm' to min.")
            string += "{} Fore Arm Rotate={}\n".format(self.side, self.foreArm)
        return [string, time]
        
    def change_elbow(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.ELBOW_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.elbow+map <= self.ELBOW_MAX and self.elbow+map >= self.ELBOW_MIN:
                self.elbow += map
            elif self.elbow+map > self.ELBOW_MAX:
                self.elbow = self.ELBOW_MAX
                print("Went past maximum 'elbow' value; setting 'elbow' to max.")
            elif self.elbow+map < self.ELBOW_MIN:
                self.elbow = self.ELBOW_MIN
                print("Went past minimum 'elbow' value; setting 'elbow' to min.")
            string += "{} Arm Elbow={}\n".format(self.side, self.elbow)
        return [string, time]
        
    def change_wrist(self, amt):
        string = ""
        time = 0.0
        map = round(amt / 100 * self.WRIST_RANGE)
        if amt != 0:
            time = check_timing(map)
            if self.wrist+map <= self.WRIST_MAX and self.wrist+map >= self.WRIST_MIN:
                self.wrist += map
            elif self.wrist+map > self.WRIST_MAX:
                self.wrist = self.WRIST_MAX
                print("Went past maximum 'wrist' value; setting 'wrist' to max.")
            elif self.wrist+map < self.WRIST_MIN:
                self.wrist = self.WRIST_MIN
                print("Went past minimum 'wrist' value; setting 'wrist' to min.")
            string += "{} Arm Wrist={}\n".format(self.side, self.wrist)
        return [string, time]

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
        left = self.leftArm.move(0, 55)
        right = self.rightArm.move(0, 55)
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
        left = self.leftArm.move(0, 55)
        right = self.rightArm.move(0, 55)
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
        left = self.leftArm.move(0, 55)
        right = self.rightArm.move(0, 55)
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

from random import randint
from datetime import datetime
        
class Sequencer:
    """A sequencer that writes to a FILE. Has a ROBOT and TIMER to keep track of actions. Uses KEYFRAMES 
       to generate animations. Recognizes ACTIONS to call robot methods"""
    def __init__(self, file, user, id, description):
        self.file = file
        self.user = user
        self.id = id
        self.description = description
        self.sequence_id = randint(0, 99999)
        self.created = datetime.now().strftime("%Y-%m-%dT%I:%M.%S")
        self.robot = Robot()
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
            
