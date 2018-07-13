# pyRosita
for controlling a RoboThespian robot via Python script

## Dependencies
* `requests` library from Python - install with `pip` (`pip install requests`)

## Usage
1. In a new blank Python file, import `requests` and the `pyRosita` library (make sure the file is in the same directory as `pyRosita.py`
2. Open a new file with write access. It must end in `.sequence` in order to be recognized by RoboThespian
```python
f = open('sample-file.sequence', 'w')
```
3. Make an instance of the `Sequencer` from pyRosita. This is how you will indicate the timing and order of commands for your animation. Pass your file instance into the `Sequencer`.
```python
seq = pyRosita.Sequencer(f)
```
4. Add movements to the sequencer using the `.add()` method. Usage is to name the action you want RoboThespian to perform, along with any extra required information using keyword arguments. A list of all possible actions, along with required arguments, can be found [below](https://github.com/olsonk/pyRosita/blob/master/README.md#recognized-actions).
```python
seq.add("both grip")
seq.add("left aim", x=40, y=50)
seq.add("left trigger")
seq.add("look point left")
seq.add("both trigger")
seq.add("both drop")
seq.add("default")
```
5. When you are finished with your animation, call `.generate_animation()` to write all your animations to your `.sequence` file. Finally, close the file instance and run this Python script.
```python
seq.generate_animation()

f.close()
```

## Recognized Actions
1. `default` - Resets RoboThespian to its default pose (centered, with both arms at its sides and hands "open").
2. `wait, time=__` - Creates a pause in the animation for the desired number of seconds.
3. `head move, x=__, y=__` - Changes the head `turn` and `nod` attributes. Accepts a number between 0 and 100.
  * 0 = full right/down
  * 50 = center
  * 100 = full left/up
4. `head nod/turn/roll, amt=__` - Sets the head `nod`, `turn`, or `roll` attribute to the given `amt`
5. `change head not/turn/roll, amt=__` - Changes the head `nod`, `turn`, or `roll` attribute by a given `amt`
6. `torso sideways/turn/bend forward, amt=__` - Sets the torso `sideways`, `turn`, or `bendForward` attribute to the given `amt`
7. `change torso sideways/turn/bend forward, amt=__` - Changes the torso `sideways`, `turn`, or `bendForward` attribute by a given `amt`
8. `left/right arm up/out/twist, amt=__` - Sets the left/right arm's `up`, `out`, or `twist` attribute to the given `amt`
9. `left/right forearm/elbow/wrist, amt=__` - Sets the left/right arm's `foreArm` rotate, `elbow`, or `wrist` attribute to the given `amt`
10. `change left/right arm up/out/twist, amt=__` - Changes the left/right arm's `up`, `out`, or `twist` attribute by the given `amt`
11. `change left/right forearm/elbow/wrist, amt=__` - Changes the left/right arm's `foreArm` rotate, `elbow`, or `wrist` attribute by the given `amt`
12. `left/right arm move, x=__, y=__` - Changes the specified arm `out` and `up` attributes. Elbow bends naturally as `y`/`up` value increases. Accepts a number between 0 and 100 (see above).
13. `left/right aim, x=__, y=__` - Moves RoboThespian's head, torso, and left/right arm to all point toward a given point. Accepts a number between 0 and 100.
14. `look point forward/left/right` - Moves both of RoboThespian's arms, as well as torso and head, to point the given direction.
15. `left/right trigger/grip/drop/buttonA/buttonB` - Sets RoboThespian's finger controls for the specified button. `trigger`, `buttonA`, and `buttonB` automatically release the button quickly. `grip` and `drop` are a lasting change.
16. `both trigger/grip/drop` - Same as above, but modifies relevant fingers on both hands simultaneously.

## TODO
* Flesh out documentation (how to control other robot device attributes and add new actions)
* Add new actions
  * Reload
  * Set individual body parts to given settings
  * Change individual body parts by a given amount
  * More complicated sets of movement (e.g. fire left, fire right, reload, point forward)
* Integrate `requests` to upload and start playback of the sequence on RoboThespian automatically.
* Implement `os` library to call other system actions and trigger sequence playback when ready.
* Extensive testing to ensure accuracy of movements and timing
