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
        """Set head nod value to given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'nod' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Set head turn value to given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'turn' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Set head roll value to given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'roll' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change head nod value by given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'nod' requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change head turn value by given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'turn' requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change head roll value by given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'roll' requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
    """Has turn, bendForward, and sideways attr that can be set, given an amt
    
    The Torso class has three movements: bendForward (at the waist, forward or back), 
    turn (twist at the waist, left or right), and sideways (stretch to the left or 
    right at the waist). Each of these values has a min and max value. This class
    also includes methods for getting current values, resetting them to 'default' 
    position, a complex move command for changing bendForward and turn simultaneously, 
    and set_ / change_ methods for granular control of each attribute.
    
    Attributes
    ----------
    bendForward : int
        The lean forward/backward motion of the torso. Defaults to 1800 (center).
    turn : int
        The left/right motion of the torso. Defaults to 1800 (center).
    sideways : int
        The sideways lean left/right motion of the torso. Defaults to 1800 (no lean).
    BENDFORWARD_MAX : int
        The maximum forward bend amount. Constant 1950
    BENDFORWARD_MIN : int
        The minimum backward bend amount. Constant 1650
    BENDFORWARD_RANGE : int
        The difference between BENDFORWARD_MAX and BENDFORWARD_MIN.
    TURN_MAX : int
        The maximum turn amount (full left). Constant 2000
    TURN_MIN : int
        The minimum turn amount (full right). Constant 1600
    TURN_RANGE : int
        The difference between TURN_MAX and TURN_MIN.
    SIDEWAYS_MAX : int
        The maximum sideways lean amount (full right). Constant 1860
    SIDEWAYS_MIN : int
        The minimum sideways lean amount (full left). Constant 1740
    SIDEWAYS_RANGE : int
        The difference between SIDEWAYS_MAX and SIDEWAYS_MIN.
    
    """
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
        """Return a dict of all current attribute names and values
        
        Returns
        -------
        dict
            Key: Attribute name, in a format ready to be added to .sequence file
            Value: value of the specified attribute
        
        """
        return {"Torso Bend Forward": self.bendForward, "Torso Sideways": self.sideways, "Torso Turn": self.turn}
    
    def reset(self):
        """Set all attr back to default values; return a dict of all attr names and values
        
        Returns
        -------
        dict
            Key: Attribute name, in a format ready to be added to .sequence file
            Value: default value of the specified attribute`
        
        """
        self.bendForward = 1800
        self.sideways = 1800
        self.turn = 1800
        return self.get_values()
    
    def move(self, x=0, y=0):
        """Change torso turn and bendForward values; return a list with a string and int
        
        Parameters
        ----------
        x : int
            The requested 'turn' value. Must be between 0 and 100.
        y : int
            The requested 'bendForward' value. Must be between 0 and 100.
            
        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        
        """
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
        """Set torso turn value to given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'turn' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Set torso bendForward value to given amt; return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'bendForward' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Set torso sideways value to given amount; return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'sideways' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change torso turn value by given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'turn' value requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change torso bendForward value by given amt; return a list w a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'bendForward' value requested. Must be between -100 & 100

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change torso sideways value by given amt; return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'sideways' value requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
    """Has up, out, twist, foreArm, elbow, and wrist attr. Can set_ or change_ any of 
       these attr, given an amt
    
    The Arm class has six movements: 
    - up (raising/lowering arm perpendicular to torso), 
    - out (raising/lowering arm at the shoulder, away from torso), 
    - twist (rotating upper arm toward or away from torso), 
    - foreArm (rotating the forearm to palm up/down),
    - elbow (bending the elbow), 
    - and wrist (bending the hand palm out or palm in). 
    Each of these values has a min and max value. This class also includes methods for 
    getting current values, resetting them to 'default' position, a complex 'move' 
    method for changing the nod and turn, and set_ / change_ methods for granular 
    control of each attribute.
    
    Attributes
    ----------
    up : int
        The up/down motion of the arm, close to the torso. Defaults to 950 (vertical).
    out : int
        The up/down motion of the arm, away from torso. Defaults to 950 (horizontal).
    twist : int
        The in/out rotation of the upper arm. Defaults to 1800 (no twist).
    foreArm : int
        The rotation of the forearm (palm up/down). Defaults to 1800 (no rotation).
    elbow : int
        The bending of the elbow. Defaults to 1350 (no bend).
    wrist : int
        The bending of the wrist, palm in/out. Defaults to 1800 (no bend).
    UP_MAX : int
        The maximum up amount. Constant 1900
    UP_MIN : int
        The minimum up amount. Constant 900
    UP_RANGE : int
        The difference between UP_MAX and UP_MIN.
    OUT_MAX : int
        The maximum out amount. Constant 1450
    OUT_MIN : int
        The minimum out amount. Constant 920
    OUT_RANGE : int
        The difference between OUT_MAX and OUT_MIN.
    TWIST_MAX : int
        The maximum twist amount. Constant 2200
    TWIST_MIN : int
        The minimum twist amount. Constant 1700
    TWIST_RANGE : int
        The difference between TWIST_MAX and TWIST_MIN.
    FOREARM_MAX : int
        The maximum foreArm amount. Constant 2700
    FOREARM_MIN : int
        The minimum foreArm amount. Constant 900
    FOREARM_RANGE : int
        The difference between FOREARM_MAX and FOREARM_MIN.
    ELBOW_MAX : int
        The maximum elbow amount. Constant 1900
    ELBOW_MIN : int
        The minimum elbow amount. Constant 1350
    ELBOW_RANGE : int
        The difference between ELBOW_MAX and ELBOW_MIN.
    WRIST_MAX : int
        The maximum wrist amount. Constant 2200
    WRIST_MIN : int
        The minimum wrist amount. Constant 1400
    WRIST_RANGE : int
        The difference between WRIST_MAX and WRIST_MIN.
    
    """
    def __init__(self, side):
        self.side = side
        self.up = 950
        self.out = 950
        self.twist = 1800
        self.foreArm = 1800
        self.elbow = 1350
        self.wrist = 1800
        
		# SET MAX/MIN VALUES FOR EACH ATTRIBUTE
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
        """Return a dict of all current attribute names and values
        
        Returns
        -------
        dict
            Key: Attribute name, in a format ready to be added to .sequence file
            Value: value of the specified attribute
        
        """
        return {"{} Arm Up".format(self.side): self.up,
                "{} Arm Out".format(self.side): self.out,
                "{} Arm Twist".format(self.side): self.twist,
                "{} Fore Arm Rotate".format(self.side): self.foreArm,
                "{} Arm Elbow".format(self.side): self.elbow,
                "{} Arm Wrist".format(self.side): self.wrist
                }
    
    def reset(self):
        """Set all attr back to default values; return a dict of all attr names and values
        
        Returns
        -------
        dict
            Key: Attribute name, in a format ready to be added to .sequence file
            Value: default value of the specified attribute`
        
        """
        self.up = self.UP_MIN
        self.out = self.OUT_MIN
        self.twist = 1800
        self.foreArm = 1800
        self.elbow = self.ELBOW_MIN
        self.wrist = 1800
        return self.get_values()
    
    def move(self, x=0, y=0):
        """Change arm up/elbow and out/twist values; return a list with a string and int
        
        Parameters
        ----------
        x : int
            The requested 'out' value. Must be between 0 and 100.
        y : int
            The requested 'up' value. Must be between 0 and 100.
            
        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        
        """
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
        """Set arm up value to given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'up' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Set arm out value to given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'out' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Set arm twist value to given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'twist' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Set forearm rotate value to given amount; return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'foreArm' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Set arm's elbow value to given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'elbow' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Set arm's wrist value to given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The requested 'wrist' value. Must be between 0 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change arm's up value by given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'up' value requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change arm's out value by given amount and return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'out' value requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change arm's twist value by given amount; return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'twist' value requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change arm's foreArm value by given amt; return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'foreArm' value requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change arm's elbow value by given amount; return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'elbow' value requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
        """Change arm's wrist value by given amount; return a list with a string and int
        
        Parameters
        ----------
        amt : int
            The difference in 'wrist' value requested. Must be between -100 and 100.

        Returns
        -------
        list
            0: string
                A string of all sequence actions to be added to the file
            1: int
                The amount of time this action should take to complete
        """
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
    """Has index, middle, ring, and baby attr that can be set or toggled
    
    The Hand class has five attributes: a name, given on instantiation,
    and four other attributes that represent fingers. Each of these fingers
    can be 0 (open) or 1 (closed). The trigger, buttonA, and buttonB functions
    toggle the finger, then release it again after a short period. The grip and
    drop methods set the attributes "permanently."
    
    Attributes
    ----------
    side : string
        The side of the body to which the hand is attached. Either "L" or "R"
    index : int
        The index (trigger) finger of the hand. Defaults to 0.
    middle : int
        The middle (grip) finger of the hand. Defaults to 0.
    ring : int
        The ring (buttton A) finger of the hand. Defaults to 0.
    baby : int
        The baby (button B) finger of the hand. Defaults to 0.
    """
    def __init__(self, side):
        self.side = side
        self.index = 0
        self.middle = 0
        self.ring = 0
        self.baby = 0
        
    def get_values(self):
        """Return a dict of all current attribute names and values
        
        Returns
        -------
        dict
            Key: Attribute name, in a format ready to be added to .sequence file
            Value: value of the specified attribute
        
        """
        return {"{} Finger index".format(self.side): self.index,
                "{} Finger middle".format(self.side): self.middle,
                "{} Finger Ring".format(self.side): self.ring,
                "{} Finger Baby".format(self.side): self.baby
                }
    
    def reset(self):
        """Set all attr back to default values; return a dict of all attr names and values
        
        Returns
        -------
        dict
            Key: Attribute name, in a format ready to be added to .sequence file
            Value: default value of the specified attribute`
        
        """
        self.index = 0
        self.middle = 0
        self.ring = 0
        self.baby = 0
        return self.get_values()
    
    def trigger(self):
        """Return a list of a list (string instructions for sequencer) and int timer val
        
        This method sets off two finger motions: first, a toggle of the finger's 
        current state; then, a toggle of the finger back to its initial state. The timer
        value is used to control the length of time for the action
        
        """
        if not self.index:
            return [["{} Finger index={}".format(self.side, 1), "{} Finger index={}\n".format(self.side, 0)], 0.40]
        else:
            return [["{} Finger index={}".format(self.side, 0), "{} Finger index={}\n".format(self.side, 1)], 0.40]
    
    def grip(self):
        """Return a list of a string with .sequencer instructions and an int timer value
        
        This method sets the middle finger's value to 1 and returns a string for the 
        .sequence file and a timing value
        
        """
        if not self.middle:
            self.middle = 1
        return ["{} Finger middle={}".format(self.side, self.middle), 0.40]
    
    def drop(self):
        """Return a list of a string with .sequencer instructions and an int timer value
        
        This method sets the middle finger's value to 0 and returns a string for the 
        .sequence file and a timing value
        
        """
        if self.middle:
            self.middle = 0
        return ["{} Finger middle={}".format(self.side, self.middle), 0.40]
    
    def buttonA(self):
        """Return a list of a list (string instructions for sequencer) and int timer val
        
        This method sets off two finger motions: first, a toggle of the finger's 
        current state; then, a toggle of the finger back to its initial state. The timer
        value is used to control the length of time for the action
        
        """
        if self.ring:
            self.ring = 0
        else:
            self.ring = 1
        return [["{} Finger ring={}".format(self.side, self.ring), '', "{} Finger ring={}".format(self.side, self.ring - self.ring)], 0.40]
    
    def buttonB(self):
        """Return a list of a list (string instructions for sequencer) and int timer val
        
        This method sets off two finger motions: first, a toggle of the finger's 
        current state; then, a toggle of the finger back to its initial state. The timer
        value is used to control the length of time for the action
        
        """
        if self.baby:
            self.baby = 0
        else:
            self.baby = 1
        return [["{} Finger baby={}".format(self.side, self.baby), '', "{} Finger baby={}".format(self.side, self.baby - self.baby)], 0.40]
        
class Robot:
    """Has Head, Torso, Arms, Hands. Performs actions that are a combo of limb movements
    
    The Robot class is a combination of limb instances. It is what the user will command
    to change, and it can perform actions that are a combination of limb movements, such
    as aiming, pointing, and firing.
    
    Attributes
    ----------
    head : Head instance
        The head of the robot. See Head definition above for attributes and methods.
    torso : Torso instance
        The torso of the robot. See Torso definition above for attributes and methods.
    leftArm : Arm instance
        The left arm of the robot. See Arm definition above for attributes and methods.
    rightArm : Arm instance
        The right arm of the robot. See Arm definition above for attributes and methods.
    leftHand : Hand instance
        The left hand of the robot. See Hand definition above for attributes and methods.
    rightHand : Hand instance
        The right hand of the robot. See Hand definition above for attributes and methods.
    
    """
    def __init__(self):
        self.head = Head()
        self.torso = Torso()
        self.leftArm = Arm("L")
        self.rightArm = Arm("R")
        self.leftHand = Hand("L")
        self.rightHand = Hand("R")
    
    def default(self):
        """Returns a list with a string for the .sequence file and a timing int of 0.40
        
        This method resets all body part values to their defaults. It is useful when
        you want the robot to return to its initial state (limbs centered and hands
        at sides, all fingers released). It calls each limb's .reset() method and
        appends limb changes to a string, which it returns.
        
        Returns
        -------
        list
            0: string of .sequence commands for how each limb needs to change
            1: int of 0.40, which is the amount of time to reserve for this movement
        
        """
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
        """Returns a list with a string for the .sequence file and a timing int
        
        This method ensures that the robot faces forward, with head slightly bowed
        and both arms pointed straight in front of the robot. Once all limb methods
        are called, it appends commands to a string and determines the furthest 
        distance any limbs need to move in order to ensure that timing is sufficient.
        
        Returns
        -------
        list
            0: string of .sequence commands for how each limb needs to change
            1: int representing timing, the amount of time to reserve for this movement
        
        """
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
        """Returns a list with a string for the .sequence file and a timing int
        
        This method ensures that the robot faces left with its torso, with head 
        slightly bowed and both arms pointed straight in front of the robot. Once 
        all limb methods are called, it appends commands to a string and determines 
        the furthest distance any limbs need to move in order to ensure that timing 
        is sufficient.
        
        Returns
        -------
        list
            0: string of .sequence commands for how each limb needs to change
            1: int representing timing, the amount of time to reserve for this movement
        
        """
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
        """Returns a list with a string for the .sequence file and a timing int
        
        This method ensures that the robot faces right with its torso, with head 
        slightly bowed and both arms pointed straight in front of the robot. Once 
        all limb methods are called, it appends commands to a string and determines 
        the furthest distance any limbs need to move in order to ensure that timing 
        is sufficient.
        
        Returns
        -------
        list
            0: string of .sequence commands for how each limb needs to change
            1: int representing timing, the amount of time to reserve for this movement
        
        """
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
        """Returns a list with a string for the .sequence file and a timing int
        
        This method causes the robot to aim with its left hand and arm at the
        given point. The robot's head and torso also move to focus on the point.
        The robot's right hand will point up toward the sky.
        
        Returns
        -------
        list
            0: string of .sequence commands for how each limb needs to change
            1: int representing timing, the amount of time to reserve for this movement
        
        """
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
        """Returns a list with a string for the .sequence file and a timing int
        
        This method causes the robot to aim with its right hand and arm at the
        given point. The robot's head and torso also move to focus on the point.
        The robot's left hand will point up toward the sky.
        
        Returns
        -------
        list
            0: string of .sequence commands for how each limb needs to change
            1: int representing timing, the amount of time to reserve for this movement
        
        """
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
        """Returns a list with a string for the .sequence file and a timing int
        
        This method makes both index fingers on the robot toggle on and off at the
        same time. Each hand's trigger() method is called, and the strings for 
        sequencer are stored in a new variable (the timing instructions are ignored).
        They are then re-combined so that each hand's fire commands are followed by
        the release commands, and finally returned with appropriate timing (0.40).
        
        Returns
        -------
        list
            0: string of .sequence commands for how each limb needs to change
            1: int representing timing, the amount of time to reserve for this movement
        
        """
        left = self.leftHand.trigger()
        right = self.rightHand.trigger()
        left_fire = left[0]
        right_fire = right[0]
        fire = left_fire[0] + '\n' + right_fire[0] + '\n'
        release = left_fire[1] + '\n' + right_fire[1] + '\n'
        string = [fire, release]
        
        return [string, 0.40]
    
    def gripBoth(self):
        """Returns a list with a string for the .sequence file and a timing int
        
        This method causes the robot's middle fingers to both turn on, which will press
        the "grip" Touch buttons.
        
        Returns
        -------
        list
            0: string of .sequence commands for how each limb needs to change
            1: int representing timing, the amount of time to reserve for this movement
        
        """
        string = ""
        string += self.leftHand.grip()[0] + "\n"
        string += self.rightHand.grip()[0] + "\n"
        
        return [string, 0.40]
        
    def dropBoth(self):
        """Returns a list with a string for the .sequence file and a timing int
        
        This method causes the robot's middle fingers to both turn off, which will 
        release the "grip" Touch buttons.
        
        Returns
        -------
        list
            0: string of .sequence commands for how each limb needs to change
            1: int representing timing, the amount of time to reserve for this movement
        
        """
        string = ""
        string += self.leftHand.drop()[0] + "\n"
        string += self.rightHand.drop()[0] + "\n"
        
        return [string, 0.40]