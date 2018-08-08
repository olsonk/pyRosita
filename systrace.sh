# These get expanded by git when doing archive, as instructed in the .gitattributes
# file
SCRIPT_COMMIT='41e66916917f0cbea0a82c7987aaaa35aa07c66f'
SCRIPT_DATE='2018-07-21 23:53:50 -0700'
SYSTRACE_DIR=/sys/kernel/debug/tracing

TRACE_DIRNAME=/data/local/tmp/traces
TRACE_FILEPATH=$TRACE_DIRNAME/trace.txt

#
# Externally configurable variables
#

# Set to 1 to enable use Android's atrace (enables Android Java tracing)
SYSTRACE_USE_ATRACE=${SYSTRACE_USE_ATRACE:-0}

# On Monterey's syncboss CPU (chattiest)
# 8 seconds takes 98MB HTML and more than 8192 KB
# 10 seconds takes 104MB HTML and 10240 KB
# SYSTRACE_BUFFER_SIZE_IN_KB=16384
SYSTRACE_BUFFER_SIZE_IN_KB=${SYSTRACE_BUFFER_SIZE_IN_KB:-8192}

# Systrace options as per $TRACE_DIRNAME/trace_options
SYSTRACE_TRACE_OPTIONS=${SYSTRACE_TRACE_OPTIONS:-"nooverwrite print-tgid"}

# Configuration for the periodic systrace
# Seconds to sleep inside systrace, set to zero for no systrace
SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE=${SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE:-5}
# Seconds to sleep outside of systrace
SYSTRACE_PERIODIC_SLEEP_SECONDS_OUTSIDE_TRACE=${SYSTRACE_PERIODIC_SLEEP_SECONDS_OUTSIDE_TRACE:-25}
# Iterations to do (one of inside, one of outside)
SYSTRACE_PERIODIC_ITERATIONS=${SYSTRACE_PERIODIC_ITERATIONS:-10}


function echod() {
    echo "$(date +%Y-%m-%d-%H:%M:%S): $*"
}

function logp() {
    # Note both "logcat" and "log" are existing android commands, don't overload
    # them and use logp (log psytrace) as this function's name
    log -t psytrace $*
}

function set_max_frequencies() {
    echod "Setting max frequencies"
    echo 1900800 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq
    echo 1900800 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq
    echo 2304000 > /sys/devices/system/cpu/cpu4/cpufreq/scaling_max_freq
    echo 2304000 > /sys/devices/system/cpu/cpu4/cpufreq/scaling_min_freq
    echo 710000000 > /sys/class/kgsl/kgsl-3d0/devfreq/max_freq
    echo 710000000 > /sys/class/kgsl/kgsl-3d0/devfreq/min_freq
}

function write_systrace_marker() {
   echo $* > $SYSTRACE_DIR/trace_marker
}

function write_psytrace_marker() {
    write_systrace_marker "psytrace: $*"
}

function log_initial_state() {
    logp "script_commit: $SCRIPT_COMMIT"
    logp "script_date: $SCRIPT_DATE"

    # Log system properties
    for d in "ro.build.date" "ro.build.date.utc" "ro.build.fingerprint" \
             "ro.product.device" "ro.serialno" \
             "debug.atrace.tags.enableflags" ; do
        logp "getprop: name=$d value=$(getprop $d)"
    done

    # Log CPU state
    for d in /sys/devices/system/cpu/cpu? ; do
       logp  "cpufreq: scaling_governor: cpu=${d: -1} $(cat $d/cpufreq/scaling_governor)"
       logp  "cpufreq: scaling_cur_freq: cpu=${d: -1} $(cat $d/cpufreq/scaling_cur_freq)"
       logp  "cpufreq: scaling_min_freq: cpu=${d: -1} $(cat $d/cpufreq/scaling_min_freq)"
       logp  "cpufreq: scaling_max_freq: cpu=${d: -1} $(cat $d/cpufreq/scaling_max_freq)"
    done

    # Log GPU state
    logp  "devfreq: scaling_governor: gpu=0 $(cat /sys/class/kgsl/kgsl-3d0/devfreq/governor)"
    logp  "devfreq: scaling_cur_freq: gpu=0 $(cat /sys/class/kgsl/kgsl-3d0/devfreq/cur_freq)"
    logp  "devfreq: scaling_max_freq: gpu=0 $(cat /sys/class/kgsl/kgsl-3d0/devfreq/min_freq)"
    logp  "devfreq: scaling_min_freq: gpu=0 $(cat /sys/class/kgsl/kgsl-3d0/devfreq/max_freq)"
    logp  "gpu_busy: $(cat /sys/class/kgsl/kgsl-3d0/gpubusy)"
}

function trace_initial_state() {
    echod "Tracing initial state"

    # Write the script version and date
    write_psytrace_marker "script_commit: $SCRIPT_COMMIT"
    write_psytrace_marker "script_date: $SCRIPT_DATE"

    # Write the current date to both systrace and logcat to be able to synchronize
    current_date=$(date +%Y-%m-%d-%H:%M:%S)
    write_psytrace_marker "datetime: $current_date"
    logp "datetime: $current_date"

    # Trace device information (eg "vs1 proto3")
    for d in "/sys/firmware/devicetree/base/model" ; do
        write_psytrace_marker "devicetree: model=$(cat $d)"
    done

    # Trace display information
    # /sys/devices/virtual/graphics/fb0/msm_fb_panel_info
    FB_PANEL_INFO_FILEPATH="/sys/devices/virtual/graphics/fb0/msm_fb_panel_info"
    while read line; do
        if [[ $line == max_fps* ]] || [[ $line == min_fps* ]] || [[ $line == panel_name* ]] ;
        then
            write_psytrace_marker "msm_fb_panel_info: $line"
        fi
    done < $FB_PANEL_INFO_FILEPATH

    # Trace system properties
    for d in "ro.build.date" "ro.build.date.utc" "ro.build.fingerprint" \
             "ro.product.device" "ro.serialno" \
             "debug.atrace.tags.enableflags" ; do
        write_psytrace_marker "getprop: name=$d value=$(getprop $d)"
    done

    # Trace CPU state
    for d in /sys/devices/system/cpu/cpu? ; do
       write_psytrace_marker "cpufreq: scaling_governor: cpu=${d: -1} $(cat $d/cpufreq/scaling_governor)"
       write_psytrace_marker "cpufreq: scaling_cur_freq: cpu=${d: -1} $(cat $d/cpufreq/scaling_cur_freq)"
       write_psytrace_marker "cpufreq: scaling_min_freq: cpu=${d: -1} $(cat $d/cpufreq/scaling_min_freq)"
       write_psytrace_marker "cpufreq: scaling_max_freq: cpu=${d: -1} $(cat $d/cpufreq/scaling_max_freq)"
    done

    # Trace GPU state
    write_psytrace_marker "devfreq: scaling_governor: gpu=0 $(cat /sys/class/kgsl/kgsl-3d0/devfreq/governor)"
    write_psytrace_marker "devfreq: scaling_cur_freq: gpu=0 $(cat /sys/class/kgsl/kgsl-3d0/devfreq/cur_freq)"
    write_psytrace_marker "devfreq: scaling_max_freq: gpu=0 $(cat /sys/class/kgsl/kgsl-3d0/devfreq/min_freq)"
    write_psytrace_marker "devfreq: scaling_min_freq: gpu=0 $(cat /sys/class/kgsl/kgsl-3d0/devfreq/max_freq)"
    write_psytrace_marker "gpu_busy: $(cat /sys/class/kgsl/kgsl-3d0/gpubusy)"

    # Trace systrace state
    write_psytrace_marker "tracing: buffer_size_kb: $(cat $SYSTRACE_DIR/buffer_size_kb)"
    write_psytrace_marker "tracing: requested_buffer_size_kb: $SYSTRACE_BUFFER_SIZE_IN_KB"
    write_psytrace_marker "tracing: buffer_total_size_kb: $(cat $SYSTRACE_DIR/buffer_size_kb)"
    for d in $SYSTRACE_DIR/per_cpu/cpu? ; do
       write_psytrace_marker "tracing: per_cpu_buffer_size_kb: cpu=${d: -1} $(cat $d/buffer_size_kb)"
    done
    write_psytrace_marker "tracing: trace_options: $(cat $SYSTRACE_DIR/trace_options)"
    write_psytrace_marker "tracing: requested_trace_options: $SYSTRACE_TRACE_OPTIONS"

    # Trace cpusets
    for d in /dev/cpuset/*/ ; do
        write_psytrace_marker "cpuset: dir=$d cpus=$(cat ${d}cpus)"
    done

    # Trace process state
    # Show each ps line in a different psytrace marker since tracing_mark_write
    # has a limit and will split into multiple trace entries otherwise.
    old_ifs=$IFS
    IFS=$'\n'
    # Show threads -t, time -x, policy -P, prio -p,
    # See https://android.googlesource.com/platform/system/core/+/nougat-release/toolbox/ps.c
    threads=$(ps -t -x -P -p)
    threads=( $threads )
    j=0
    n=${#threads[*]}
    for thread in ${threads[*]} ; do
        write_psytrace_marker "ps: $j/$n $thread"
        let j=$j+1
    done
    IFS=$old_ifs

    # Trace battery state
    write_psytrace_marker "battery: status: $(cat /sys/class/power_supply/battery/status)"
    write_psytrace_marker "battery: capacity: $(cat /sys/class/power_supply/battery/capacity)"
    write_psytrace_marker "battery: power: current_now=$(cat /sys/class/power_supply/battery/current_now) voltage_now=$(cat /sys/class/power_supply/battery/voltage_now)"
}

function setup_adreno_tracing() {
    # XXX The Adreno driver shows in logcat that is reading these settings, but
    #     they are not taking effect for some reason (wrong drivers/stale flags?)
    mkdir -p /data/misc/gpu
    printf 'DebugTracingGroupsEnabled=0x4000001f\nGpuScopeMode=Stage' > /data/misc/gpu/esx_config.txt
    # echo "DebugTracingGroupsEnabled=0x7fffffff" > /data/misc/gpu/esx_config.txt
    # echo "DebugTracingGroupsEnabled=0x7fffffff\nGpuScopeMode=Stage" > /data/misc/gpu/esx_config.txt
}

function setup_systrace() {
    echod "Setting up systrace"
    # Create the output dir
    mkdir -p $TRACE_DIRNAME
    # Enable a few events
    for ev in "sched/sched_switch" "sched/sched_wakeup" \
                   "power/suspend_resume" "power/cpu_idle" "power/cpu_frequency" \
                   "thermal/thermal_temperature" "thermal/tsens_read" \
                   "net/net_dev_xmit" "net/netif_receive_skb" \
                   "kgsl/kgsl_pwrlevel" "kgsl/kgsl_clk" "kgsl/kgsl_gpubusy" \
                   "kgsl/adreno_cmdbatch_queued" "kgsl/adreno_cmdbatch_submitted" \
                   "kgsl/adreno_cmdbatch_retired" "kgsl/kgsl_pwr_set_state" \
                   "kgsl/kgsl_pwrlevel" "kgsl/kgsl_buslevel" \
                   "kgsl/adreno_hw_preempt_trig_to_comp_int" ; do
        echo 1 > $SYSTRACE_DIR/events/$ev/enable
    done

    # The kernel won't automatically reclaim file caches for systrace reallocation,
    # so sync the disk (not strictly necessary, but it maximizes the effect of the
    # drop since drop is not supposed to drop dirty caches) and drop those caches
    # to minimize the chance of systrace reallocation failing (see T31870780)
    echod "Syncing disk"
    sync
    echod "Dropping caches"
    echo 3 > /proc/sys/vm/drop_caches

    echod "Setting systrace buffer size to $SYSTRACE_BUFFER_SIZE_IN_KB KB"
    echo $SYSTRACE_BUFFER_SIZE_IN_KB > $SYSTRACE_DIR/buffer_size_kb
    echo "global" > $SYSTRACE_DIR/trace_clock

    # Modifying the options requires root
    for op in $SYSTRACE_TRACE_OPTIONS ; do
        echod "Setting trace option $op"
        echo $op > $SYSTRACE_DIR/trace_options
    done

    # Clear the trace
    echo '' > $SYSTRACE_DIR/trace
}

function start_systrace() {
    # Start the systrace
    if [ $SYSTRACE_USE_ATRACE == 1 ]; then
        # Note setting buffer_size_kb after invoking atrace doesn't work, not
        # clear what would need to be done (restart the trace?), so set it as
        # atrace parameter instead
        atrace --async_start -k gfx input view camera wm am freq idle load sched -b $SYSTRACE_BUFFER_SIZE_IN_KB

        # Set the options again since atrace resets a few (overwite, etc)
        for op in $SYSTRACE_TRACE_OPTIONS ; do
            echod "Setting trace option $op"
            echo $op > $SYSTRACE_DIR/trace_options
        done

    else
        echo 1 > $SYSTRACE_DIR/tracing_on
    fi
}


function dump_systrace() {
    # Retrieve the systrace, do an intermediate copy since adb pull cannot fetch
    # directly from /d/tracing/trace
    echod "Dumping systrace from to $TRACE_FILEPATH"
    cp $SYSTRACE_DIR/trace $TRACE_FILEPATH
    # Clear the trace
    echo '' > $SYSTRACE_DIR/trace
}

function stop_systrace() {
    # End the systrace
    echo 0 > $SYSTRACE_DIR/tracing_on

    dump_systrace

    if [ $SYSTRACE_USE_ATRACE == 1 ]; then
        # Pulling the trace via atrace takes forever (atrace.cpp uses sendfile,
        # this could be slow on Android?), that's why the trace is pulled
        # manually and then stopped & ignored here
        atrace --async_stop > /dev/null
    fi

    ## echod Compressing trace from $TRACE_FILEPATH to $TRACE_FILEPATH.gz
    ## gzip $TRACE_FILEPATH
}

function periodic_systrace() {
    echod "Periodic systrace iters: $SYSTRACE_PERIODIC_ITERATIONS secs inside: " \
          "$SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE secs outside: $SYSTRACE_PERIODIC_SLEEP_SECONDS_OUTSIDE_TRACE"

    # Create the output dir
    mkdir -p $TRACE_DIRNAME

    echod "Deleting existing traces and logcats"
    rm -rf $TRACE_DIRNAME/*.txt
    rm -rf $TRACE_DIRNAME/*.logcat
    rm -rf $TRACE_DIRNAME/*.txt.gz

    echod "Saving initial logcat"
    logcat  -d > $TRACE_FILEPATH.$(date "+%Y%m%d-%H%M%S").initial.txt.logcat
    logcat -c

    # Enlarge logcat buffer size, 256KB by default
    # Note this resets the buffer if the size changed, so it's important to save
    # it above
    echod "Configuring logcat"
    logcat --buffer-size=2M

    # Enable 1 second power sampling on pacific
    echod "Enabling 1-second power sampling"
    echo 1000 > /sys/module/qpnp_fg/parameters/sram_update_period_ms

    if [ $SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE != 0 ]; then
        setup_systrace
    fi

    echod "Starting periodic systrace"
    i=0
    while [ $i -lt $SYSTRACE_PERIODIC_ITERATIONS ]; do
        echod "Starting iteration $i"

        TRACE_ITERATION_FILEPATH=$TRACE_FILEPATH.$(date "+%Y%m%d-%H%M%S").$i.txt

        log_initial_state

        if [ $SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE != 0 ]; then

            # Clear the trace
            echo '' > $SYSTRACE_DIR/trace

            start_systrace
            echod "Tracing for $SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE seconds"

            # Set the max frequencies while tracing so any frequency changes can be
            # observed
            # set_max_frequencies

            trace_initial_state

            # Write power updates, note the sysfs entry only refreshes every 2 or 1.5
            # seconds at most
            j=0
            while [ $j -lt $SYSTRACE_PERIODIC_SLEEP_SECONDS_INSIDE_TRACE ]; do
                power_marker="battery: power: current_now=$(cat /sys/class/power_supply/battery/current_now) voltage_now=$(cat /sys/class/power_supply/battery/voltage_now)"
                write_psytrace_marker $power_marker
                logp $power_marker
                sleep 1
                let j=$j+1
            done

            # Stop it (which dumps to the trace to a file) and move it to the
            # final filename in the background to minimize the overhead over the
            # loop iteration
            echod "Stopping systrace in the background"
            (
              stop_systrace
              echod "Moving systrace from $TRACE_FILEPATH to $TRACE_ITERATION_FILEPATH"
              mv $TRACE_FILEPATH $TRACE_ITERATION_FILEPATH
            ) &
        fi

        # sleep for some time
        echod "Sleeping for $SYSTRACE_PERIODIC_SLEEP_SECONDS_OUTSIDE_TRACE seconds"
        j=0
        while [ $j -lt $SYSTRACE_PERIODIC_SLEEP_SECONDS_OUTSIDE_TRACE ]; do
            logp "battery: power: current_now=$(cat /sys/class/power_supply/battery/current_now) voltage_now=$(cat /sys/class/power_supply/battery/voltage_now)"
            sleep 1
            let j=$j+1
        done

        let i=$i+1

        echod "Saving logcat to $TRACE_ITERATION_FILEPATH.logcat"
        logcat -d > $TRACE_ITERATION_FILEPATH.logcat
        echod "Clearing logcat"
        logcat -c
    done

    echod "Finished periodic systrace"
}

function normal_systrace() {
    setup_systrace
    start_systrace

    trace_initial_state

    sleep 10

    stop_systrace
}

function async_systrace_start() {
    #  We want the systrace to no-overwrite (wraparound and keep writing)
    SYSTRACE_TRACE_OPTIONS+=" overwrite"

    setup_adreno_tracing
    setup_systrace
    start_systrace

    trace_initial_state
}

function async_systrace_stop() {
    stop_systrace
}

function async_systrace_dump() {
    THIS_TRACE_FILEPATH=$TRACE_FILEPATH.$(date "+%Y%m%d-%H%M%S").txt

    trace_initial_state

    dump_systrace

    ## echod "Moving systrace from $TRACE_FILEPATH to $THIS_TRACE_FILEPATH"
    ## mv $TRACE_FILEPATH $THIS_TRACE_FILEPATH
}

# async_systrace_start
# async_systrace_start

# periodic_systrace
# sleep 20
# normal_systrace
