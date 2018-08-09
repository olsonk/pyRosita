import re
from os import listdir
from os.path import isfile, join
import json
import datetime

def match(phrase):
    if phrase in vrapi_data:
        try:
            return re.search(r'{}=([0123456789]+)'.format(phrase), line).group(1)
        except AttributeError:
            return ""
    elif phrase in insideout_data or phrase in oculus_os_dml_data:
        try:            
            return re.search(r'(?:"{}":)(.*?)(?:,)'.format(phrase), line).group(1)
        except AttributeError:
            return ""


# Get list of all filenames ending in .txt.logcat in traces/ directory
TRACES_FILEPATH = os.path.dirname(os.path.realpath(__file__))
TRACES_FILEPATH = os.path.join(TEST_RUN_FILEPATH, "traces/")
onlyfiles = [f for f in listdir(TRACES_FILEPATH) if isfile(join(TRACES_FILEPATH, f))]
files = []
for file in onlyfiles:
    if ".txt.logcat" in file:
        files.append(file)
print(files)

# Specify what data to pull from the logcat file
vrapi_data = ['FPS', 
              'Prd', 
              'Tear', 
              'Early', 
              'Stale', 
              'VSnc', 
              'Lat', 
              'Fov', 
              'Free', 
              'Temp',
              'current_now',
              'voltage_now']
insideout_data = ['duration', 
                  'frames', 
                  'inliers_avg', 
                  'has_tracking', 
                  'keyframes_avg', 
                  'map_points_avg', 
                  'mapper_queue_max', 
                  'realtime_ms', 
                  'reprojection_err_avg', 
                  'tracker_dur_p50', 
                  'tracker_dur_p90', 
                  'uptime_ms', 
                  'vision_jitter_p50', 
                  'vision_jitter_p90', 
                  'visionlib_sourcecodeversion']
oculus_os_dml_data = ['controller_button_average_rtt', 
                      'controller_button_max_rtt', 
                      'controller_button_samples', 
                      'controller_imu_average_rtt', 
                      'controller_imu_max_rtt', 
                      'controller_imu_samples', 
                      'imu_hmd_average_rtt', 
                      'imu_hmd_max_rtt', 
                      'imu_hmd_samples', 
                      'mag_average_rtt', 
                      'mag_max_rtt', 
                      'mag_samples', 
                      'sync_average_rtt', 
                      'sync_max_rtt', 
                      'sync_samples', 
                      'vsync_average_rtt', 
                      'vsync_max_rtt', 
                      'vsync_samples']
                      
data_to_grab = []
for item in vrapi_data:
    data_to_grab.append(item)
for item in insideout_data:
    data_to_grab.append(item)
for item in oculus_os_dml_data:
    data_to_grab.append(item)

# Set the file to write the parsed results to
now = datetime.datetime.now()
filepath = join(mypath, now.strftime("%Y%m%d-%H%M%S_results.csv"))
result = open(filepath, "w")

# Write headers for file
result.write("timestamp,")
for item in data_to_grab:
    result.write(item+",")
result.write("\n")

# Set regex for identifying the timestamp on a line
time_regex = r'[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}'

for file in files:
    opened_file = open(join(mypath, file), "rb")
    for line in opened_file:
        if b"FPS=" in line or b'insideout_periodic' in line or b'controller_imu_average_rtt' in line or b'current_now' in line:
            line = str(line)
            # Relevant lines with data to grab come from VrApi (that 
            # include FPS, or example), insideout_period, or oculus_os_dml.
            
            try:
                timestamp = re.search(time_regex, line).group()
                result.write(timestamp+",")
            except:
                result.write(",")
            for item in data_to_grab:
                result.write(match(item)+',')
            result.write('\n')
result.close()