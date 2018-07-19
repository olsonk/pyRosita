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
    
def limit_value(val):
    """Return an int between 0 and 100
    
    Parameters
    ----------
    val : int
        val is the requested value for a movement. Nearly all robot methods accept
        values between 0 and 100, so this helper function verifies that any requested
        values are within this range. If the requested value is greater than 100 or 
        less than 0, the function returns 100 or 0, respectively. Otherwise, it simply
        returns the value requested.
        
    Returns
    -------
    int
        A number between 0 and 100
    
    """
    if val > 100:
        print("Values must be between 0 and 100.")
        print("Requested value, {}, exceeded maximum. Setting to 100".format(val))
        return 100
    elif val < 0:
        print("Values must be between 0 and 100.")
        print("Requested value, {}, exceeded minimum. Setting to 0".format(val))
        return 0
    else:
        return val

def limit_change(amt, current, max, min):
    """Returns an int for new robot device setting, within required min/max values
    
    This helper function accepts information about a given attribute, along with
    a requested 'change' amount, and guarantees that the requested value is within
    allowable limits.
    
    Parameters
    ----------
    amt : int
        The amount of change requested; may be between -100 and 100
    current : int
        The current value of the attribute being changed
    max : int
        The maximum allowable value for the attribute being changed
    min : int
        The minimum allowable value for the attribute being changed
        
    Returns
    -------
    int
        The value requested, guaranteeing it is within the allowable bounds of the attr
    
    """
    if current+amt <= max and current+amt >= min:
        new = current + amt
        return new
    elif current+amt > max:
        new = max
        print("Requested value of {}. Maximum allowable is {}".format(current+amt, max))
        print("Setting value to {}".format(max))
        return new
    elif current+amt < min:
        new = min
        print("Requested value of {}. Minimum allowable is {}".format(current+amt, min))
        print("Setting value to {}".format(min))
        return new

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
        x = limit_value(x)
        y = limit_value(y)
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
        
    def set(self, part, amt):
        """Return string (formatted for .sequence file) and int (amount of time needed)
        
        This method is used to set a Head attribute to a specified value. It accepts
        an attribute name and a value (should be from 0-100), then adds onto a string
        in a format that can be read by Virtual Robot and with a timing value 
        appropriate for the distance the head needs to move.
        
        Parameters
        ----------
        attr : string
            The attribute of the head that being set. Must be "nod", "turn", or "roll"
        
        amt : int
            The requested attribute value. Must be between 0 and 100.

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
        amt = limit_value(amt)
        if part == "nod":
            map = round(amt / 100 * self.NOD_RANGE)
            if self.nod != self.NOD_MIN+map:
                diff = self.nod - (self.NOD_MIN+map)
                time = check_timing(diff)
                self.nod = self.NOD_MIN + map
                string += "Head Nod={}\n".format(self.nod)
        elif part == "turn":
            map = round(amt / 100 * self.TURN_RANGE)
            if self.turn != self.TURN_MIN+map:
                diff = self.turn - (self.TURN_MIN+map)
                time = check_timing(diff)
                self.turn = self.TURN_MIN + map
                string += "Head Turn={}\n".format(self.turn)
        elif part == "roll":
            map = round(amt / 100 * self.ROLL_RANGE)
            if self.roll != self.ROLL_MIN+map:
                diff = self.roll - (self.ROLL_MIN+map)
                time = check_timing(diff)
                self.roll = self.ROLL_MIN + map
                string += "Head Roll={}\n".format(self.roll)
        else:
            print("Must specify an attribute of 'nod', 'turn', or 'roll'")
        return [string, time]  
            
    def change(self, part, amt):
        """Return string (formatted for .sequence file) and int (amount of time needed)
        
        This method is used to change a Head attribute by a specified value. It accepts
        an attribute name and a value (should be from -100-100), then adds onto a string
        in a format that can be read by Virtual Robot and with a timing value 
        appropriate for the distance the head needs to move.
        
        Parameters
        ----------
        attr : string
            The attribute of the head that being set. Must be "nod", "turn", or "roll"
        
        amt : int
            The requested attribute value. Must be between -100 and 100.

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
        if part == "nod":
            map = round(amt / 100 * self.NOD_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.nod = limit_change(map, self.nod, self.NOD_MAX, self.NOD_MIN)
                string += "Head Nod={}\n".format(self.nod)
        elif part == "turn":
            map = round(amt / 100 * self.TURN_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.turn = limit_change(map, self.turn, self.TURN_MAX, self.TURN_MIN)
                string += "Head Turn={}\n".format(self.turn)
        elif part == "roll":
            map = round(amt / 100 * self.ROLL_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.roll = limit_change(map, self.roll, self.ROLL_MAX, self.ROLL_MIN)
                string += "Head Roll={}\n".format(self.roll)
        else:
            print("Must specify an attribute of 'nod', 'turn', or 'roll'")
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
        x = limit_value(x)
        y = limit_value(y)
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
        
    def set(self, part, amt):
        """Return string (formatted for .sequence file) and int (amount of time needed)
        
        This method is used to set a Torso attribute to a specified value. It accepts
        an attribute name and a value (should be from 0-100), then adds onto a string
        in a format that can be read by Virtual Robot and with a timing value 
        appropriate for the distance the torso needs to move.
        
        Parameters
        ----------
        attr : string
            The attribute of the torso that is being set. Must be "bend_forward", 
            "sideways", or "turn"
        
        amt : int
            The requested attribute value. Must be between 0 and 100.

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
        amt = limit_value(amt)
        if part == "bend_forward":
            map = round(amt / 100 * self.BENDFORWARD_RANGE)
            if self.bendForward != self.BENDFORWARD_MIN+map:
                diff = self.bendForward - (self.BENDFORWARD_MIN+map)
                time = check_timing(diff)
                self.bendForward = self.BENDFORWARD_MIN + map
                string += "Torso Bend Forward={}\n".format(self.bendForward)
        elif part == "sideways":
            map = round(amt / 100 * self.SIDEWAYS_RANGE)
            if self.sideways != self.SIDEWAYS_MIN+map:
                diff = self.sideways - (self.SIDEWAYS_MIN+map)
                time = check_timing(diff)
                self.sideways = self.SIDEWAYS_MIN + map
                string += "Torso Sideways={}\n".format(self.sideways)
        elif part == "turn":
            map = round(amt / 100 * self.TURN_RANGE)
            if self.turn != self.TURN_MIN+map:
                diff = self.turn - (self.TURN_MIN+map)
                time = check_timing(diff)
                self.turn = self.TURN_MIN + map
                string += "Torso Turn={}\n".format(self.turn)
        else:
            print("Must specify an attribute of 'bend_forward', 'turn', or 'sideways'")
        return [string, time]    
            
    def change(self, part, amt):
        """Return string (formatted for .sequence file) and int (amount of time needed)
        
        This method is used to change a Torso attribute by a specified value. It accepts
        an attribute name and a value (should be from -100-100), then adds onto a string
        in a format that can be read by Virtual Robot and with a timing value 
        appropriate for the distance the torso needs to move.
        
        Parameters
        ----------
        attr : string
            The attribute of the torso that is being changed. Must be "bend_forward", 
            "sideways", or "turn"
        
        amt : int
            The requested attribute value. Must be between -100 and 100.

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
        amt = limit_value(amt)
        if part == "turn":
            map = round(amt / 100 * self.BENDFORWARD_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.turn = limit_change(map, self.turn, self.TURN_MAX, self.TURN_MIN)
                string += "Torso Turn={}\n".format(self.turn)
        elif part == "bend_forward":
            map = round(amt / 100 * self.SIDEWAYS_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.bendForward = limit_change(map, self.bendForward, self.BENDFORWARD_MAX, self.BENDFORWARD_MIN)
                string += "Torso Bend Forward={}\n".format(self.bendForward)
        elif part == "sideways":
            map = round(amt / 100 * self.TURN_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.sideways = limit_change(map, self.sideways, self.SIDEWAYS_MAX, self.SIDEWAYS_MIN)
                string += "Torso Sideways={}\n".format(self.sideways)
        else:
            print("Must specify an attribute of 'bend_forward', 'turn', or 'sideways'")
        return [string, time]
        
class Arm:
    """Has up, out, twist, foreArm, elbow, and wrist attr. Can set or change with an amt
    
    The Arm class has six movements: 
    - up (raising/lowering arm perpendicular to torso), 
    - out (raising/lowering arm at the shoulder, away from torso), 
    - twist (rotating upper arm toward or away from torso), 
    - foreArm (rotating the forearm to palm up/down),
    - elbow (bending the elbow), 
    - and wrist (bending the hand palm out or palm in). 
    Each of these values has a min and max value. This class also includes methods for 
    getting current values, resetting them to 'default' position, a complex 'move' 
    method for changing the nod and turn, and set / change methods for granular 
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
        x = limit_value(x)
        y = limit_value(y)
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
	
    def set(self, attr, amt):
        """Return string (formatted for .sequence file) and int (amount of time needed)
        
        This method is used to set an Arm attribute to a specified value. It accepts
        an attribute name and a value (should be from 0-100), then adds onto a string
        in a format that can be read by Virtual Robot and with a timing value 
        appropriate for the distance the arm needs to move.
        
        Parameters
        ----------
        attr : string
            The attribute of the arm that is being set. Must be "up", "out", "twist",
            "fore_arm", "elbow", or "wrist"
        
        amt : int
            The requested attribute value. Must be between 0 and 100.

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
        amt = limit_value(amt)
        if attr == "up":
            map = round(amt / 100 * self.UP_RANGE)
            if self.up != self.UP_MIN+map:
                diff = self.up - (self.UP_MIN+map)
                time = check_timing(diff)
                self.up = self.UP_MIN + map
                string += "{} Arm Up={}\n".format(self.side, self.up)
        elif attr == "out":
            map = round(amt / 100 * self.OUT_RANGE)
            if self.out != self.OUT_MIN+map:
                diff = self.out - (self.OUT_MIN+map)
                time = check_timing(diff)
                self.out = self.OUT_MIN + map
                string += "{} Arm Out={}\n".format(self.side, self.out)
        elif attr == "twist":
            map = round(amt / 100 * self.TWIST_RANGE)
            if self.twist != self.TWIST_MIN+map:
                diff = self.twist - (self.TWIST_MIN+map)
                time = check_timing(diff)
                self.twist = self.TWIST_MIN + map
                string += "{} Arm Twist={}\n".format(self.side, self.twist)
        elif attr == "fore_arm":
            map = round(amt / 100 * self.FOREARM_RANGE)
            if self.foreArm != self.FOREARM_MIN+map:
                diff = self.foreArm - (self.FOREARM_MIN+map)
                time = check_timing(diff)
                self.foreArm = self.FOREARM_MIN + map
                string += "{} Fore Arm Rotate={}\n".format(self.side, self.foreArm)
        elif attr == "elbow":
            map = round(amt / 100 * self.ELBOW_RANGE)
            if self.elbow != self.ELBOW_MIN+map:
                diff = self.elbow - (self.ELBOW_MIN+map)
                time = check_timing(diff)
                self.elbow = self.ELBOW_MIN + map
                string += "{} Arm Elbow={}\n".format(self.side, self.elbow)
        elif attr == "wrist":
            map = round(amt / 100 * self.WRIST_RANGE)
            if self.wrist != self.WRIST_MIN+map:
                diff = self.wrist - (self.WRIST_MIN+map)
                time = check_timing(diff)
                self.wrist = self.WRIST_MIN + map
                string += "{} Arm Wrist={}\n".format(self.side, self.wrist)
        else:
            print("Must specify an attribute of 'up', 'out', 'twist', 'fore_arm', 'elbow', or 'wrist'")
        return [string, time]
    
    def change(self, part, amt):
        """Return string (formatted for .sequence file) and int (amount of time needed)
        
        This method is used to change an Arm attribute by a specified value. It accepts
        an attribute name and a value (should be from -100 to 100), then adds onto a 
        string in a format that can be read by Virtual Robot and with a timing value 
        appropriate for the distance the arm needs to move.
        
        Parameters
        ----------
        attr : string
            The attribute of the arm that is being set. Must be "up", "out", "twist",
            "fore_arm", "elbow", or "wrist"
        
        amt : int
            The requested change amount. Must be between -100 and 100.

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
        if part == "up":
            map = round(amt / 100 * self.UP_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.up = limit_change(map, self.up, self.UP_MAX, self.UP_MIN)
                string += "{} Arm Up={}\n".format(self.side, self.up)
        elif part == "out":
            map = round(amt / 100 * self.OUT_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.out = limit_change(map, self.out, self.OUT_MAX, self.OUT_MIN)
                string += "{} Arm Out={}\n".format(self.side, self.out)
        elif part == "twist":
            map = round(amt / 100 * self.TWIST_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.twist = limit_change(map, self.twist, self.TWIST_MAX, self.TWIST_MIN)
                string += "{} Arm Twist={}\n".format(self.side, self.twist)
        elif part == "fore_arm":
            map = round(amt / 100 * self.FOREARM_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.foreArm = limit_change(map, self.foreArm, self.FOREARM_MAX, self.FOREARM_MIN)
                string += "{} Fore Arm Rotate={}\n".format(self.side, self.foreArm)
        elif part == "elbow":
            map = round(amt / 100 * self.ELBOW_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.elbow = limit_change(map, self.elbow, self.ELBOW_MAX, self.ELBOW_MIN)
                string += "{} Arm Elbow={}\n".format(self.side, self.elbow)
        elif part == "wrist":
            map = round(amt / 100 * self.WRIST_RANGE)
            if amt != 0:
                time = check_timing(map)
                self.wrist = limit_change(map, self.wrist, self.WRIST_MAX, self.WRIST_MIN)
                string += "{} Arm Wrist={}\n".format(self.side, self.wrist)
        else:
            print("Must specify an attribute of 'up', 'out', 'twist', 'fore_arm', 'elbow', or 'wrist'")
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