import os
import subprocess
import requests
from time import sleep
import argparse

def wait_for_file():
    while True:
        try:
            pull_message = subprocess.check_output("adb pull /storage/emulated/0/Android/data/com.oculus.dabrobot/files/dab_test_demo.json", shell=True)
            print("file created. Proceeding.")
            break
        except:
            print("file not yet created. Waiting 0.5 sec and will try again.")
            sleep (0.5)
        
def main(sequence, time):
    # set up a session in order to call the Tritium Web API 
    # on Rosita to run the sequence
    session = requests.Session()
    token = os.environ["TRITIUM_AUTH_TOKEN"]
    session.cookies.set("tritium_auth_token", token)

    # make sure device is connected and ready
    print("Waiting for Android device to be connected and ready.")
    os.system("adb wait-for-device")

    # ensure that APK is installed on device
    print("Ensuring APK is installed on device")
    package_string = subprocess.check_output("adb shell pm list packages dabrobot", shell=True)
    if b'dabrobot' in package_string:
        print(package_string)
        print("Dead and Buried installed already. Proceeding.")
    else:
        print("Dead and Buried not installed on device. Installing...")
        os.system("adb install -g -r DeadAndBuried-RobotTest.apk")

    # clearing out dab_robot_test.json file
    os.system("adb shell rm /storage/emulated/0/Android/data/com.oculus.dabrobot/files/dab_test_demo.json")
        
        
    # set timeout time for Dead & Buried build
    os.system("adb shell setprop persist.dab_demo_timeout {}".format(time))
    
    # start Dead & Buried build
    os.system("adb shell am start com.oculus.dabrobot/com.unity3d.player.UnityPlayerActivity")

    # watch for D&B to be loaded & ready

    # The next line did't work - inotifyd held up forever and couldn't allow program to continue after file was changed
    #os.system('adb shell inotifyd - /storage/emulated/0/Android/data/com.oculus.dabrobot/files/dab_test_demo.json')

    # This DOES work - just with a half-second potential for missing the cue
    wait_for_file()

    # start Rosita's animations
    play_url = "https://rt-0101.robothespian.co.uk/tritium/sequence_player/play/"
    response = session.put(play_url+sequence)
    print(response)

    # start systrace.py
    # edit to reflect the path of systrace
    systrace_path = "C:\\Users\\olsonkev\\Documents\\psytrace-master\\systrace.py"
    os.system("python {} {}".format(systrace_path, time))

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('sequence', 
                        help='Specify the sequence name to be played on RoboThespian (omit .sequence)')
    parser.add_argument('time', type=int,
                        help='Specify the amount of time (seconds) to run Dead & Buried, RoboThespian animation, and systrace')
    args = parser.parse_args()
    sequence = args.sequence
    time = args.time
    main(sequence, time)