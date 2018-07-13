#Changelog / Updates

## July 13
* Added methods to change torso and arm values by a given amt

##	July 12
* Abstracted “check_timing(diff)” from movements
* Added methods to set left/right arm up/out/twist/forearm/elbow/wrist to an amt
* Added methods to set head nod/turn/roll to an amt
* Added methods to set torso bendForward/sideways/turn to an amt
* Investigated API functions to determine if upload is functional; used new “upload” functionality from GUI
* Added method to change head nod/turn/roll by a set amt

##	July 11
* Improved arm up/down movement by also incorporating elbow movements when arm.move(x, y) is used; elbow value is an exponential function of y-input, creating more natural bends in arms as they are raised/lowered
* Fixed issues with point_look_left and point_look_right that resulted from re-working positions to 0-100 system
* Added left_aim and right_aim methods – opposite arm raises, looks and points at target (head should work nicely with this too
* Improved timing for torso movements – should be much more precise for slow torso movements
* Began documenting usage using Github Readme

##	July 10
* Discovered that we can drag & drop .sequence files into Virtual Robot and they will get imported properly.
* Added pyRosita to Github (https://github.com/olsonk/pyRosita)
* Tested sequences on Rosita – pretty accurate, although robot moves slightly slower than virtual robot
* Modified arguments for torso/head/arm positions to be from 0-100, with 50 being “centered” for all body parts (more user-friendly?)
