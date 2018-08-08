#!/usr/bin/env python2
"""
Systrace parser.

Enhances a systrace and optionally builds an html

"""

import __builtin__
import gzip
import logging
import os
import re
import subprocess
import sys

logger = logging.getLogger(__name__)

def xopen(filepath, mode):
    if (filepath.endswith(".gz")):
        # Always open gzip files in binary mode
        # XXX This doesn't support writing at the moment
        assert mode in ["r", "rb" ]
        return gzip.open(filepath, "rb")
    else:
        return open(filepath, mode)

def sum(l):
    """
    Override built-in sum to make sure this is never called with a dict instead
    of a list
    :param l:
    :return:
    """
    assert isinstance(l, list)
    return __builtin__.sum(l)

def wsum(l, w):
    """
    Weighted sum

    :param l: list of numbers
    :param w: list of weights, with as many weights as numbers in l
    :return: l[i] * w[i] for all elements in l
    """
    assert len(l) == len(w)

    return sum([w[i] * l[i] for i in xrange(len(l))])



class Struct(dict):
    """!
    Use with
    struct = Struct(field1='foo', field2='bar', field3=42)
    self.assertEquals('bar', struct.field2)
    self.assertEquals(42, struct['field3'])
    """
    def __init__(self, **kwargs):
        super(Struct, self).__init__(**kwargs)
        self.__dict__ = self

class Task(object):
    def __init__(self, comm, pid, tgid = None, tgid_name = None):
        self.pid = pid
        self.comm = comm
        self.tgid = tgid
        self.tgid_name = tgid_name

        # Aggregated data, per cpu
        self.cycles = {}
        self.seconds = {}

    def setTgid(self, tgid, tgid_name = None):
        self.tgid = tgid
        self.tgid_name = tgid_name

    def addCyclesSeconds(self, cpu_id, cycles, seconds):
        try:
            self.cycles[cpu_id] += cycles
            self.seconds[cpu_id] += seconds

        except KeyError:
            self.cycles[cpu_id] = cycles
            self.seconds[cpu_id] = seconds

    def getCycles(self, cpu_id):
        return self.cycles[cpu_id]

    def getSeconds(self, cpu_id):
        return self.seconds[cpu_id]

    def id(self):
        # Linux is aggressive recycling pids, use both name and pid as key
        return "%s-%d" % (self.comm, self.pid)

class Cpu(object):
    def __init__(self, index):
        self.index = index

        # Aggregated data
        self.cycles = 0
        self.seconds = 0
        self.seconds_per_frequency = {}

        # Transient data
        self.frequency = 0
        self.current_task = None

        # Last timestamp the scheduler dealt with this cpu
        self.last_timestamp = None

    def addSeconds(self, seconds):
        self.cycles += self.frequency * seconds
        self.seconds += seconds
        self.seconds_per_frequency[self.frequency] = self.seconds_per_frequency.get(self.frequency, 0) + seconds

    def getCycles(self):
        return self.cycles

    def getSeconds(self):
        return self.seconds

    def getFrequency(self):
        return self.frequency

    def getCurrentTask(self):
        return self.current_task

class SoC(object):
    def __init__(self):
        self.cpus = {}
        self.tasks = {}

    def changeFrequency(self, timestamp, cpu_id, frequency):
        try:
            cpu = self.cpus[cpu_id]
        except KeyError:
            cpu = Cpu(cpu_id)
            self.cpus[cpu_id] = cpu

        # Account cycles for current task at old frequency
        task = cpu.current_task
        # Task may be none if we haven't seen a task on this cpu yet
        if (task is not None):
            # Account for the cycles done at the old frequency
            if (cpu.last_timestamp is None):
                cpu.last_timestamp = timestamp

            seconds = timestamp - cpu.last_timestamp
            task.addCyclesSeconds(cpu_id, seconds * frequency, seconds)
            cpu.addSeconds(seconds)

        cpu.frequency = frequency
        cpu.last_timestamp = timestamp

    def contextSwitch(self, timestamp, cpu_id, prev_comm, prev_pid, prev_tgid, next_comm, next_pid):

        try:
            prev_task = Task(prev_comm, prev_pid, prev_tgid)
            prev_task = self.tasks[prev_task.id()]
            if (prev_task.tgid_name is None):
                # Update the parent process name
                # XXX Do a lookup instead of a linear search
                prev_tgid_name = None
                for task in self.tasks.values():
                    if (task.pid == prev_tgid):
                        prev_tgid_name = task.comm
                prev_task.setTgid(prev_tgid, prev_tgid_name)

        except KeyError:
            self.tasks[prev_task.id()] = prev_task

        try:
            next_task = Task(next_comm, next_pid)
            next_task = self.tasks[next_task.id()]
        except KeyError:
            self.tasks[next_task.id()] = next_task

        try:
            cpu = self.cpus[cpu_id]
        except KeyError:
            cpu = Cpu(cpu_id)
            cpu.last_timestamp = timestamp
            self.cpus[cpu_id] = cpu

            cpu.current_task = prev_task

        # XXX Looks like some tasks can be scheduled on cpus via sched_wakeup, fix it
        #     or migrated or start of cpu log?
        # ##### CPU 0 buffer started ####
        #   <...>-1621  [000] d..3 134626.984532: sched_switch: prev_comm=android.display prev_pid=1621 prev_prio=116 prev_state=S ==> next_comm=swapper/0 next_pid=0 next_prio=120
        if (cpu.last_timestamp is None):
            logger.warning("Task %s was scheduled via wakeup?" % prev_task.id())
            prev_task.last_timestamp = timestamp
            assert(prev_task.last_timestamp is not None)

        # If the current task mismatches prev_task, the process has changed name
        # while in the cpu (eg when adbd spawns a shell)
        # Update the name of the current task and delete the newly created prev_task
        if ((cpu.current_task is not None) and (cpu.current_task != prev_task)):
            assert cpu.current_task.pid == prev_task.pid, "Task %s was renamed to %s, but the PID %d vs. %d mismatches" % (cpu.current_task.comm, prev_task.comm, cpu.curren_task.pid, prev_task.pid)
            assert None is logger.debug("Task %s changed name to %s" % (cpu.current_task.id(), prev_task.id()))
            del self.tasks[cpu.current_task.id()]
            cpu.current_task.comm = prev_task.comm
            prev_task = cpu.current_task
            self.tasks[prev_task.id()] = prev_task

        # Finish accounting to prev task
        seconds = timestamp - cpu.last_timestamp
        prev_task.addCyclesSeconds(cpu.index, cpu.getFrequency() * seconds, seconds)
        cpu.addSeconds(seconds)

        # This task is now in this cpu
        cpu.current_task = next_task
        cpu.last_timestamp = timestamp

    def migrate(self, timestamp, pid, old_cpu, new_cpu):
        pass

    def sync(self, timestamp):
        """
        Sync all the measurements, needs to be called so the last timeslice is
        accounted for
        :return:
        """
        # Switch all the cpus to the current frequency so the last timeslice
        # is accounted for
        # Note there may be gaps in this cpu dict
        for cpu_id in self.cpus:
            self.changeFrequency(timestamp, cpu_id, self.cpus[cpu_id].getFrequency())


# Note comm names are free form, can include spaces, slashes, etc
SYSTRACE_PATTERN = "#(?P<comment>.*)"
SYSTRACE_PATTERN += r"|(?P<task>.*)-(?P<pid>\d+)\s+(\((?P<tgid>.*)\)\s+)?\[(?P<cpu>\d+)\] (?P<flags>\S+)\s+(?P<timestamp>\d+\.\d+): (?P<function>[^:]+): (?P<rest>.*)"
SYSTRACE_PATTERN_REGEXP = re.compile(SYSTRACE_PATTERN)

SYSTRACE_SCHED_SWITCH_PATTERN = r"prev_comm=(?P<prev_comm>.*) prev_pid=(?P<prev_pid>\d+) prev_prio=(?P<prev_prio>\d+) prev_state=(?P<prev_state>\S+) ==> next_comm=(?P<next_comm>.*) next_pid=(?P<next_pid>\d+) next_prio=(?P<next_prio>\d+)"
SYSTRACE_SCHED_SWITCH_PATTERN_REGEXP = re.compile(SYSTRACE_SCHED_SWITCH_PATTERN)

SYSTRACE_FREQUENCY_PATTERN = r"state=(?P<frequency>\d+) cpu_id=(?P<cpu_id>\d+)"
SYSTRACE_FREQUENCY_PATTERN_REGEXP = re.compile(SYSTRACE_FREQUENCY_PATTERN)

SYSTRACE_SELF_CHECK_PATTERNS = [
    (
        SYSTRACE_PATTERN_REGEXP,
        [
             "# entries-in-buffer/entries-written: 144290/144290   #P:4\n",
             "Tracking1-4961  ( 4364) [003] d.s2  2081.420093: cpufreq_interactive_target: cpu=0 load=99 cur=652800 actual=652800 targ=960000\n",
             "<idle>-0     [002] dn.2 328325.679110: cpu_idle: state=4294967295 cpu_id=2\n",
             "<...>-3290  [002] d..4 677007.189558: sched_wakeup: comm=adbd pid=26452 prio=120 success=1 target_cpu=001\n",
        ]
    ),
    (
        SYSTRACE_SCHED_SWITCH_PATTERN_REGEXP,
        [
            "prev_comm=cfinteractive prev_pid=313 prev_prio=0 prev_state=D ==> next_comm=swapper/1 next_pid=0 next_prio=120",
        ]
     ),
    (
        SYSTRACE_FREQUENCY_PATTERN_REGEXP,
        [
            "state=2150400 cpu_id=2"
        ]
    )
]

# Self-check patterns
for rx, patterns in SYSTRACE_SELF_CHECK_PATTERNS:
    for p in patterns:
        assert rx.match(p) is not None, "Pattern %s fails self check for regexp %s" % (repr(rx.pattern), repr(p))

def build_android_counter(pid, name, value):
    l = "C|%d|%s|%d" % (pid, name, value)
    return l

def build_android_begin(pid, name):
    l = "B|%d|%s" % (pid, name)
    return l

def build_android_end():
    return "E"

def build_sched_switch(prev_comm, prev_pid, prev_prio, prev_state, next_comm, next_pid, next_prio):
    # sched_switch: prev_comm=swapper/1 prev_pid=0 prev_prio=120 prev_state=R ==> next_comm=ReadFromDisk next_pid=2484 next_prio=120
    rr = "prev_comm=%s prev_pid=%d prev_prio=%d prev_state=%s ==> next_comm=%s next_pid=%d next_prio=%d" % (
        prev_comm, prev_pid, prev_prio, prev_state, next_comm, next_pid, next_prio)
    return rr

def build_systrace_line(task, pid, tgid, cpu, flags, timestamp, function, rest):
    if (tgid is not None):
        return "%16s-%-5d (%5d) [%03d] %4s %05.6f: %s: %s" % (
            task,
            pid,
            tgid,
            cpu,
            flags,
            timestamp,
            function,
            rest
        )
    else:
        return "%16s-%-5d [%03d] %4s %05.6f: %s: %s" % (
            task,
            pid,
            cpu,
            flags,
            timestamp,
            function,
            rest
        )

def wrap_trace_in_html(src_filepath, dst_filepath):
    SYSTRACE_PY_DIR = os.path.dirname(os.path.realpath(__file__))

    #
    # This is lifted from sdk\platform-tools\systrace\catapult\systrace\systrace\output_generator.py
    #

    SYSTRACE_PY_PREFIX_HTML = os.path.join(SYSTRACE_PY_DIR, "prefix.html")
    SYSTRACE_PY_SUFFIX_HTML = os.path.join(SYSTRACE_PY_DIR, "suffix.html")
    SYSTRACE_PY_INFIX_HTML = os.path.join(SYSTRACE_PY_DIR, "systrace_trace_viewer.html")

    # Load the prefix, replace {{SYSTRACE_TRACE_VIEWER_HTML}} with the HTML
    # Insert the trace
    # add the suffix
    infix = open(SYSTRACE_PY_INFIX_HTML, 'rb').read()
    prefix = open(SYSTRACE_PY_PREFIX_HTML, 'rb').read()
    suffix = open(SYSTRACE_PY_SUFFIX_HTML, 'rb').read()

    trace = xopen(src_filepath, 'rb').read()

    prefix = prefix.replace("{{SYSTRACE_TRACE_VIEWER_HTML}}", infix)
    # Open the file in binary mode to prevent python from changing the
    # line endings, then write the prefix.
    with open(dst_filepath, 'wb') as out:
        out.write(prefix)
        # Write the trace data itself. There is a separate section of the form
        # <script class="trace-data" type="application/text"> ... </script>
        # for each tracing agent (including the controller tracing agent).
        out.write('<!-- BEGIN TRACE-->\n')
        out.write('  <script class="trace-data" type="application/text">\n')
        out.write(trace)
        out.write('<!-- END TRACE -->\n')
        out.write(suffix)

def main(src_filepath, dst_filepath, cpu_weights = None):
    is_html = ".html" in src_filepath.lower()
    soc = SoC()
    first_timestamp = None
    last_timestamp = 0
    num_lines = 0
    max_lines = sys.maxint
    corrupted_line = None
    with xopen(src_filepath, 'r') as f_in:
        with open(dst_filepath, 'w') as f_out:
            for l in f_in:
                # Assert if we found corruption before the last line
                assert corrupted_line is None, "Corrupted line found before the last line %s" % repr(corrupted_line)
                # Note that the last line can be corrupted, ignore it
                try:
                    num_lines += 1
                    if (num_lines > max_lines):
                        break
                    assert None is logger.debug("read: %s" % repr(l))
                    m = SYSTRACE_PATTERN_REGEXP.match(l)
                    l = l.strip()

                    # If the input file is html and there's no match, ignore
                    if ((m is None) and is_html):
                        continue


                    if (m.group("comment") is not None):
                        # Comment, ignore
                        pass

                    else:

                        task = m.group("task").strip()
                        pid = int(m.group("pid"))
                        tgid = m.group("tgid")
                        if (tgid is None):
                            # This trace doesn't provide tgids, ignore
                            pass
                        elif (tgid == "-----"):
                            # This process doesn't have a tgid, set to zero
                            tgid = 0
                        else:
                            tgid = int(tgid)
                        cpu = int(m.group("cpu"))
                        flags = m.group("flags")
                        timestamp = float(m.group("timestamp"))
                        function = m.group("function")
                        rest = m.group("rest")

                        assert None is logger.debug("task %s pid %s tgid %s function %s" %
                                                    (task, pid, tgid, function))

                        if ((cpu not in soc.cpus) and (function != "sched_switch")):
                            # Initialize the tasks in each cpu if no tasks are there
                            # yet because no sched_switch was seen on this cpu yet
                            # This makes Chrome render trace start times when the task
                            # is descheduled, but it's really important if the
                            # task is never descheduled in the whole trace
                            # XXX Ideally this should insert a line with the first
                            #     timestamp ever seen, but we don't know the task
                            #     until we find the first event for this CPU is
                            #     seen.
                            #     This could be done if two-pass or line insertion
                            #     capabilities are ever introduced

                            # The comm <idle> actually appears as swapper/<cpu>
                            # in sched_switch events, make sure we preserve that
                            # so anything that depends on sched_switch works
                            # (accounting, etc)
                            next_comm = task if (task != "<idle>") else "swapper/%d" % cpu
                            logger.info("Generating initial fake sched_switch for comm %s (%s) on cpu %d" % (next_comm, task, cpu))

                            # Make accounting regard the start time of this task
                            soc.contextSwitch(timestamp, cpu, "swapper/%d" % cpu, 0, 0, next_comm, pid)
                            # Generate a fake sched_switch from the idle task to this
                            # one, so Chrome renders the bar
                            # XXX Needs a way of updating the tgid and prio if those are ever seen

                            rr = build_sched_switch("swapper/%d" % cpu, 0, 120, "R", next_comm, pid, 120)
                            # <idle>-0     (    0) [001] d..3 3493.438366:
                            ll = build_systrace_line("<idle>", 0, 0, cpu, "d..3",
                                                     timestamp, "sched_switch", rr)
                            f_out.write("%s\n" % ll)

                        # systrace in kernel has a 64-entry cache to keep recent
                        # names to avoid expensive name lookups. When the cache
                        # misses you get "<...>" as task name.
                        # Change "<...>" to the right name using the CPU current task
                        # lookup
                        if (task == "<...>"):
                            # Since this task appears in a systrace line, it has to
                            # be current in some cpu, look for this task's name in the
                            # CPU current tasks
                            # XXX The tasks translate this way don't have a TGID, find
                            #     out why and fix if possible?
                            new_task = None
                            for this_cpu in soc.cpus.values():
                                this_cpu_current_task = this_cpu.getCurrentTask()
                                if ((this_cpu_current_task is not None) and (this_cpu_current_task.pid == pid)):
                                    new_task = this_cpu_current_task.comm

                            if (new_task is not None):
                                assert None is logger.debug("Translating %s-%d to %s" % (task, pid, new_task))
                                task = new_task
                            else:
                                # If this task was already in some CPU when the trace
                                # started, we may not have seen its name yet and we
                                # cannot do the translation
                                logger.warning("Unable to translate task %s-%d" % (task, pid))

                        if (first_timestamp is None):
                            first_timestamp = timestamp

                        # Make sure that timestamps are going forward, some very old
                        # kernels wouldn't synchronize CPU buffers well
                        assert last_timestamp <= timestamp, "Current timestamp %f is less than previous timestamp %f" % (last_timestamp, timestamp)
                        last_timestamp = timestamp

                        if (function == "cpu_frequency"):
                            #    cpu_frequency: state=2150400 cpu_id=2
                            m = re.match("state=(?P<frequency>\d+) cpu_id=(?P<cpu_id>\d+)", rest)
                            frequency = int(m.group("frequency"))
                            cpu_id = int(m.group("cpu_id"))
                            soc.changeFrequency(timestamp, cpu_id, frequency)

                        elif (function == "sched_switch"):
                            #    sched_switch: prev_comm=cfinteractive prev_pid=313 prev_prio=0 prev_state=D ==> next_comm=swapper/1 next_pid=0 next_prio=120
                            m = SYSTRACE_SCHED_SWITCH_PATTERN_REGEXP.match(rest);
                            prev_pid = int(m.group("prev_pid"))
                            prev_comm = m.group("prev_comm")
                            next_pid = int(m.group("next_pid"))
                            next_comm = m.group("next_comm")
                            soc.contextSwitch(timestamp, cpu, prev_comm, prev_pid, tgid, next_comm, next_pid)

                        elif (function == "sched_wakeup"):
                            pass

                        # net_dev_xmit: dev=wlan0 skbaddr=ffffffc041327200 len=66 rc=0
                        # netif_receive_skb: dev=wlan0 skbaddr=ffffffc028d95900 len=1470
                        elif ((function == "net_dev_xmit") or
                              (function == "netif_receive_skb")):
                            m = re.match(r"dev=(?P<dev>\S+) skbaddr=\S+ len=(?P<len_bytes>\d+).*",
                                         rest)
                            len_bytes = int(m.group("len_bytes"))
                            rx_tx = "tx" if (function == "net_dev_xmit") else "rx"
                            rr = build_android_counter(8888, "%s %s" % (m.group("dev"), rx_tx),
                                                       len_bytes)
                            ll = build_systrace_line(task, pid, tgid, cpu,
                                                     flags,
                                                     timestamp,
                                                     "tracing_mark_write", rr)
                            f_out.write("%s\n" % ll)

                            # The event is found when the buffer has been received
                            # or sent, but there's no information on when the first
                            # bytes started, so it doesn't make sense to render
                            # as a block with non zero length.
                            # Drop the counter to zero so this appears as
                            # zero-length block in the trace.
                            rr = build_android_counter(8888,
                                                       "%s %s" % (m.group("dev"), rx_tx),
                                                       0)
                            ll = build_systrace_line(task, pid, tgid, cpu,
                                                     flags,
                                                     timestamp,
                                                     "tracing_mark_write", rr)
                            f_out.write("%s\n" % ll)

                        elif (function == "kgsl_register_event"):
                            # kgsl_register_event: ctx=0 ts=2410408 cb=adreno_ringbuffer_mmu_clk_disable_event+0x0/0x28
                            pass

                        # kgsl_register_event: ctx=0 ts=2410408 cb=adreno_ringbuffer_mmu_clk_disable_event+0x0/0x28
                        elif (function == "kgsl_register_event"):
                            pass

                        # kgsl_process_events: work:ffffffc001b200d0, process_one_work+0x28c/0x444
                        elif (function == "kgsl_process_events"):
                            # kgsl_register_event: ctx=0 ts=2410408 cb=adreno_ringbuffer_mmu_clk_disable_event+0x0/0x28
                            pass

                        # kgsl_pwrstats: d_name=kgsl-3d0 total=12427 busy=8139 ram_time=1159316 ram_wait=301723\n'
                        elif (function == "kgsl_pwrstats"):
                            m = re.match(r"d_name=kgsl-3d0 total=(?P<total>\d+) busy=(?P<busy>\d+) ram_time=(?P<ram_time>\d+) ram_wait=(?P<ram_wait>\d+)", rest)
                            busy_pct = float(m.group("busy")) / float(m.group("total"))
                            rr = build_android_counter(8887, "kgsl_pwrstats_busy", int(busy_pct * 100.0))
                            ll =build_systrace_line(task, pid, tgid, cpu, flags, timestamp, "tracing_mark_write", rr)
                            f_out.write("%s\n" % ll)
                            ramwait_pct = float(m.group("ram_wait")) / float(m.group("ram_time"))
                            rr = build_android_counter(8887, "kgsl_pwrstats_ramwait",
                                                       int(ramwait_pct * 100.0))
                            ll = build_systrace_line(task, pid, tgid, cpu, flags,
                                                     timestamp, "tracing_mark_write",
                                                     rr)
                            f_out.write("%s\n" % ll)

                        # kgsl_clk: d_name=kgsl-3d0 flag=on active_freq=257000000
                        elif (function == "kgsl_clk"):
                            m = re.match(r"d_name=kgsl-3d0 flag=(?P<flag>\S+) active_freq=(?P<active_freq>\d+)", rest)
                            active_freq = int(m.group("active_freq"))
                            rr = build_android_counter(8887, "kgsl_clk", active_freq)
                            ll = build_systrace_line(task, pid, tgid, cpu, flags,
                                                     timestamp,
                                                     "tracing_mark_write", rr)
                            f_out.write("%s\n" % ll)

                        # kgsl_gpubusy: d_name=kgsl-3d0 busy=1032838 elapsed=1032834
                        elif (function == "kgsl_gpubusy"):
                            m = re.match(
                                r"d_name=kgsl-3d0 busy=(?P<busy>\d+) elapsed=(?P<elapsed>\d+)",
                                rest)
                            busy_pct = float(m.group("busy")) / float(
                                m.group("elapsed"))
                            rr = build_android_counter(8887, "kgsl_gpubusy",
                                                       int(busy_pct * 100.0))
                            ll = build_systrace_line(task, pid, tgid, cpu, flags,
                                                     timestamp,
                                                     "tracing_mark_write", rr)
                            f_out.write("%s\n" % ll)

                        # kgsl_fire_event: ctx=0 ts=2412008 type=retired age=0 cb=adreno_ringbuffer_mmu_clk_disable_event+0x0/0x28\n'
                        elif (function == "kgsl_fire_event"):
                            pass

                        # kgsl_issueibcmds: d_name=kgsl-3d0 ctx=24 ib=0x0 numibs=1 ts=14192 flags=CTX_SWITCH result=0 type=GL\n'
                        elif (function == "kgsl_issueibcmds"):
                            pass

                        # kgsl_active_count_put: work:ffffffc001b1f738, adreno_dispatcher_work+0xa14/0xac8\n'
                        elif (function == "kgsl_active_count_put"):
                            pass

                        # kgsl_add_event: ctx:0, ts:2412470, retired:2412470, work:0xffffffc08702f740, adreno_ringbuffer_mmu_disable_clk_on_ts+0x24/0x5c\n'
                        elif (function == "kgsl_add_event"):
                            pass

                        # kgsl_deep_nap_timer: work:ffffffc001b1f738, call_timer_fn+0x88/0x174\n'
                        elif (function == "kgsl_deep_nap_timer"):
                            pass

                        # kgsl_timer: work:ffffffc001b1f738, call_timer_fn+0x88/0x174'
                        elif (function == "kgsl_timer"):
                            pass

                        # kgsl_buslevel: d_name=kgsl-3d0 pwrlevel=4 bus=6\n'
                        elif (function == "kgsl_buslevel"):
                            m = re.match(r"d_name=kgsl-3d0 pwrlevel=(?P<pwrlevel>\d+) bus=(?P<bus>\d+)", rest)

                            rr = build_android_counter(8887, "kgsl_buslevel_bus",
                                                       int(m.group("bus")))
                            ll = build_systrace_line(task, pid, tgid, cpu, flags, timestamp,
                                                     "tracing_mark_write", rr)
                            f_out.write("%s\n" % ll)

                            rr = build_android_counter(8887, "kgsl_buslevel_pwr",
                                                       int(m.group("pwrlevel")))
                            ll = build_systrace_line(task, pid, tgid, cpu, flags,
                                                timestamp, "tracing_mark_write", rr)
                            f_out.write("%s\n" % ll)

                        # kgsl_pwrlevel: d_name=kgsl-3d0 pwrlevel=5 freq=214000000 prev_pwrlevel=0 prev_freq=624000000
                        elif (function == "kgsl_pwrlevel"):
                            m = re.match(r"d_name=kgsl-3d0 pwrlevel=(?P<pwrlevel>\d+) freq=(?P<freq>\d+) prev_pwrlevel=(?P<prev_pwrlevel>\d+) prev_freq=(?P<prev_freq>\d+)",
                                rest)

                            rr = build_android_counter(8887, "kgsl_pwrlevel_freq",
                                                       int(m.group("freq")))
                            ll = build_systrace_line(task, pid, tgid, cpu, flags,
                                                     timestamp,
                                                     "tracing_mark_write", rr)
                            f_out.write("%s\n" % ll)

                        elif ("kgsl" in function):

                            logger.debug("read: %s" % repr(l))

                        # Build the line back in case something was modified
                        l = build_systrace_line(task, pid, tgid, cpu, flags, timestamp, function, rest)

                    f_out.write("%s\n" % l)

                except:
                    # Note that the last line can be corrupted, store and warn
                    # only if we later find this is not the last line
                    # XXX This should record the exception to print it out later
                    corrupted_line = l

            logger.info("Total lines %d" % num_lines)
            # Insert sched_switch to the last timeslices so Chrome renders the
            # full bar for all the tasks currently on the CPUs
            # XXX This happens with any other counter like cpu_freq, etc, find a
            #     way of fixing the start and end of those too?
            #     (start can be fixed putting "initial state information" in
            #      via trace_markers, end can be fixed by hooking on the last
            #      value and extending it to the last timestamp)
            for this_cpu in soc.cpus.values():
                cpu = this_cpu.index
                this_cpu_current_task = this_cpu.getCurrentTask()
                # The task can be none if this cpu never had any task on it
                # for the whole run
                if (this_cpu_current_task is None):
                    logger.debug("Last task is none on cpu %d" % cpu)
                    continue

                pid = this_cpu_current_task.pid
                task = this_cpu_current_task.comm
                # tgid will be none for tasks that have never been scheduled out,
                # set to 0 in that case
                tgid = this_cpu_current_task.tgid if this_cpu_current_task.tgid is not None else 0
                # XXX We don't currently collect the priority in the tas, make
                #     up some value
                prio = 120
                # Make up some flags
                flags = "d..3"

                # XXX If we do this at an earlier time, feeding back into the
                #     trace parser, we wouldn't need to do the .sync below that
                #     closes the accounting
                rr = build_sched_switch(task, pid, prio, "R", "swapper/%d" % cpu, 0, 120)
                ll = build_systrace_line(task, pid, tgid, cpu, flags,
                                         timestamp, "sched_switch", rr)
                f_out.write("%s\n" % ll)

    # Account for the last timeslice
    soc.sync(last_timestamp)

    # Verify there are no duplicated pids (ignore swapper, the idle thread)
    if __debug__:
        tasks = soc.tasks.values()
        for t in tasks:
            for t2 in tasks:
                if ((t.pid == t2.pid) and (t.id() != t2.id()) and (t.pid != 0)):
                    logger.warning("PID %d for task %s matches PID %d for task %s" % (t.pid, t.id(), t2.pid, t2.id()))

    # Gather statistics, grouping by comm name
    tasks = soc.tasks.values()
    tasks = sorted(tasks, key=lambda task: task.comm)

    num_cpus = max(soc.cpus.keys()) + 1
    if (cpu_weights is None):
        cpu_weights = [1.0] * num_cpus
    else:
        num_cpus = max(num_cpus, len(cpu_weights))
    assert len(cpu_weights) >= num_cpus

    grouped_tasks = {}
    for t in tasks:

        comm = t.comm
        if (t.pid == 0):
            # Use a more friendly name for the idle tasks (one on each CPU), called
            # "swapper/0" for cpu 0, etc
            comm = comm.replace("swapper/", "IDLE CPU")

        # If we couldn't resolve the tgid name for the duration of the trace,
        # set to the tgid numerical value
        tgid_name = t.tgid_name
        if (tgid_name is None):
            tgid_name = str(t.tgid)
        # Set an empty name if the tgid is the same as the pid
        if (t.tgid == t.pid):
            tgid_name = ""

        grouped_task = grouped_tasks.get(t.comm, Struct(comm=comm, tgid_name=tgid_name, npids=0, seconds=[0.0] * num_cpus, cycles=[0.0] * num_cpus))
        grouped_tasks[t.comm] = grouped_task

        # If this trace didn't have tgid or this group has multiple tgids, set to empty
        if ((tgid_name is None) or (grouped_task.tgid_name != tgid_name)):
           grouped_task.tgid_name = ""

        for cpu_id in t.seconds:
            grouped_task.seconds[cpu_id] += t.getSeconds(cpu_id)
            grouped_task.cycles[cpu_id] += t.getCycles(cpu_id)

        grouped_task.npids += 1

    with open(dst_filepath + "_schedstats.csv", "w") as f_out:

        # Sort tasks by cycles first, seconds second (in case cycles are 0 because
        # no frequency changes were seen in the trace)
        tasks = sorted(grouped_tasks.values(), cmp=lambda a, b:
            -1 if ((wsum(a.cycles, cpu_weights) < wsum(b.cycles, cpu_weights)) or
                   ((wsum(a.cycles, cpu_weights) == wsum(b.cycles, cpu_weights)) and
                    (wsum(a.seconds, cpu_weights) < wsum(b.seconds, cpu_weights)))) else 1, reverse=True)

        # Write headers
        f_out.write("%16s, %16s, %4s, %8s, %12s, %5s, %5s, %5s, %5s" % ("process", "parent", "pids", "seconds", "cycles", "sec%", "cyc%", "nsec%", "ncyc%"))
        for cpu_id in xrange(num_cpus):
            f_out.write(", CPU %d %5s, %5s, %5s, %5s" % (cpu_id, "sec%", "cyc%", "nsec%", "ncyc%"))
        f_out.write("\n")

        # Note that total cycles can be zero if no frequency changes were observed
        total_cycles = sum([sum(t.cycles) for t in tasks])
        weighted_total_cycles = sum([wsum(t.cycles, cpu_weights) for t in tasks])
        total_seconds = sum([sum(t.seconds) for t in tasks])
        weighted_total_seconds = sum([wsum(t.seconds, cpu_weights) for t in tasks])

        # XXX Some traces (dropdead startup) give a 3.7 instead of 4 scale, need
        #     to investigate if this is ok because of cores down, or not ok because
        #     of accumulated errors when adding seconds (unlikely).
        logger.info("Calculated total seconds/total seconds is %f" % (total_seconds / (last_timestamp - first_timestamp)))

        for t in tasks:
            # Write global information, using global percentages
            total_seconds_this_task = sum(t.seconds)
            weighted_total_seconds_this_task = wsum(t.seconds, cpu_weights)
            pct_seconds_this_task = total_seconds_this_task * 100.0 / total_seconds
            weighted_pct_seconds_this_task = weighted_total_seconds_this_task * 100.0 / weighted_total_seconds
            assert pct_seconds_this_task <= 100.0

            total_cycles_this_task = sum(t.cycles)
            weighted_total_cycles_this_task = wsum(t.cycles, cpu_weights)
            pct_cycles_this_task = total_cycles_this_task * 100.0 / total_cycles if total_cycles > 0 else 0
            weighted_pct_cycles_this_task  = weighted_total_cycles_this_task * 100.0 / weighted_total_cycles if weighted_total_cycles > 0 else 0
            assert pct_cycles_this_task <= 100.0

            f_out.write("%16s, %16s, %4d, %8.4f, %12.2f, %5.2f, %5.2f, %5.2f, %5.2f, " %
                        (t.comm, t.tgid_name, t.npids,
                         total_seconds_this_task, total_cycles_this_task,
                         pct_seconds_this_task, pct_cycles_this_task,
                         weighted_pct_seconds_this_task,
                         weighted_pct_cycles_this_task))

            # Write per cpu information, using per-cpu percentages
            for cpu_id in xrange(num_cpus):
                try:
                    cpu = soc.cpus[cpu_id]
                    cpu_seconds = cpu.seconds
                    cpu_cycles = cpu.cycles
                except KeyError:
                    # This cpu_id didn't run for the whole test, set values to 0
                    cpu_seconds = 0
                    cpu_cycles = 0

                total_seconds_this_cpu = cpu_seconds
                weighted_total_seconds_this_cpu = cpu_seconds * cpu_weights[cpu_id]
                seconds_this_cpu = t.seconds[cpu_id]
                weighted_seconds_this_cpu = t.seconds[cpu_id] * cpu_weights[cpu_id]
                pct_seconds_this_cpu = seconds_this_cpu * 100.0 / total_seconds_this_cpu if total_seconds_this_cpu > 0 else 0
                weighted_pct_seconds_this_cpu = weighted_seconds_this_cpu * 100.0 / weighted_total_seconds_this_cpu if weighted_total_seconds_this_cpu > 0 else 0
                assert pct_seconds_this_cpu <= 100.0

                total_cycles_this_cpu = cpu_cycles
                weighted_total_cycles_this_cpu = cpu_cycles * cpu_weights[cpu_id]
                cycles_this_cpu = t.cycles[cpu_id]
                weighted_cycles_this_cpu = t.cycles[cpu_id] * cpu_weights[cpu_id]
                pct_cycles_this_cpu = cycles_this_cpu * 100.0 / total_cycles_this_cpu if total_cycles_this_cpu > 0 else 0
                weighted_pct_cycles_this_cpu = weighted_cycles_this_cpu * 100.0 / weighted_total_cycles_this_cpu if weighted_total_cycles_this_cpu > 0 else 0
                # Use some epsilon in case of accumulated error on calculations
                ## assert pct_cycles_this_cpu <= 101.0, "pct_cycles_this_cpu %f > 100.0" % pct_cycles_this_cpu

                f_out.write("      %5.2f, %5.2f, %5.2f, %5.2f, " % (pct_seconds_this_cpu, pct_cycles_this_cpu,
                                                                    weighted_pct_seconds_this_cpu, weighted_pct_cycles_this_cpu))


            f_out.write("\n")

    # output freqstats, percentage of time spent on each frequency and CPU
    with open(dst_filepath + "_freqstats.csv", "w") as f_out:

        # Collect all frequencies, sorted higher to lower
        frequencies = []
        for cpu_id in soc.cpus:
            cpu = soc.cpus[cpu_id]
            for freq in cpu.seconds_per_frequency:
                if freq not in frequencies:
                    frequencies.append(freq)
        frequencies = sorted(frequencies)

        # Write headers
        f_out.write("        ")
        for cpu_id in xrange(num_cpus):
            f_out.write("CPU %2d, " % cpu_id)
        f_out.write("\n")

        # Write percentage of time at each frequency (note we cannot use
        # percentage of cycles since we don't know the cycles speent in the "unknown"
        # frequency)
        for freq in frequencies:
            if (freq == 0):
                f_out.write("%8s " % "unknown")
            else:
                f_out.write("%8d " % freq)
            for cpu_id in xrange(num_cpus):
                try:
                    cpu = soc.cpus[cpu_id]
                    total_seconds_this_cpu = sum(cpu.seconds_per_frequency.values())
                    seconds_this_frequency = cpu.seconds_per_frequency.get(freq, 0)
                except KeyError:
                    total_seconds_this_cpu = 0
                    seconds_this_frequency = 0

                pct_seconds_this_frequency = ((seconds_this_frequency * 100.0 / total_seconds_this_cpu)
                                             if (total_seconds_this_cpu > 0) else 0)
                f_out.write("%6.2f, " % pct_seconds_this_frequency)

            f_out.write("\n")


logger.info("Starting")
if (__name__ == "__main__"):
    logging_format = "%(asctime).23s %(levelname)s:%(filename)s(%(lineno)d) [%(thread)d]: %(message)s"

    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(logging.Formatter(logging_format))
    logger.addHandler(logger_handler)
    logger.setLevel(logging.INFO)

    src_filepath = r"c:\Users\atejada\Documents\projects\tomatoee2\trace.html"
    dst_filepath = "psytrace"

    if (len(sys.argv) > 1):
        src_filepath = sys.argv[1]
    if (len(sys.argv) > 2):
        dst_filepath = sys.argv[2]

    cpu_weights = None
    if (len(sys.argv) > 3):
        cpu_weights = sys.argv[3]
        cpu_weights = cpu_weights.split(",")
        cpu_weights = [float(w) for w in cpu_weights]

    logger.info("Input trace %s output trace %s weights %s" % (repr(src_filepath), repr(dst_filepath), repr(cpu_weights)))

    main(src_filepath, dst_filepath, cpu_weights)

    wrap_trace_in_html(dst_filepath, "%s.html" % dst_filepath)