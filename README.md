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
4. Add movements to the sequencer using the `.add()` method. Usage is to name the action you want RoboThespian to perform, along with any extra required information using keyword arguments. A list of all possible actions, along with required arguments, can be found below.
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
