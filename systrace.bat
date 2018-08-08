
adb root
adb wait-for-device

adb shell mkdir -p /data/local/tmp/traces

echo pushing systrace.sh
adb push systrace.sh /data/local/tmp
adb shell chmod a+x /data/local/tmp/systrace.sh

rem echo Disabling Android
rem adb shell stop
rem adb wait-for-device
rem adb shell stop trackingservice

rem echo Setting performance
rem adb shell "echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
rem adb shell "echo performance > /sys/devices/system/cpu/cpu4/cpufreq/scaling_governor"

echo Capturing systrace
adb shell "echo 'source /data/local/tmp/systrace.sh && SYSTRACE_PERIODIC_SLEEP_SECONDS_OUTSIDE_TRACE=5 SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE=5 SYSTRACE_PERIODIC_ITERATIONS=4 periodic_systrace > /data/local/tmp/traces/trace.log 2>&1' > /data/local/tmp/s.sh"
adb shell chmod a+x /data/local/tmp/s.sh
adb shell "cd /data/local/tmp && nohup /data/local/tmp/s.sh"

rem adb shell "source /data/local/tmp/systrace.sh && periodic_systrace"

echo Waiting for device to be available
adb wait-for-device

REM echo Maps are
REM adb shell "cat /proc/$(pidof trackingservice.old)/maps" | grep tracker --max-count=2
REM adb shell "cat /proc/$(pidof trackingservice.old)/maps  | grep tracker --max-count=1 | cut -d '-' -f 1 " > REM BASE_ADDRESS
REM set /p BASE_ADDRESS=<BASE_ADDRESS

REM echo Compressing systrace
REM adb shell gzip /data/local/tmp/traces/trace.txt

echo Pulling systrace
del traces\trace*.*
adb pull /data/local/tmp/traces/

echo Running psytrace
for /r %%i in (traces\*.txt) do psytrace.py %%i  %%i.out

echo zipping traces
set year=%date:~10,4%
set month=%date:~4,2%
set day=%date:~7,2%
set hour=%time:~0,2%
set min=%time:~3,2%
set sec=%time:~6,2%
set filename=traces_%year%%month%%day%-%hour%%min%%sec%_self_serve.zip

del %filename%
zip -j %filename% traces/*.*


REM psytrace.py trace.txt.gz %1