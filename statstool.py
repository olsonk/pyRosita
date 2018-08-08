#!/usr/bin/env python
import glob
import logging
import sys

logger = logging.getLogger(__name__)

OP_CODE_AVERAGE = 0
OP_CODE_SUBTRACT = 1
OP_CODE_SUM = 2
OP_NAMES_TO_CODE = { "avg" : OP_CODE_AVERAGE, "average" : OP_CODE_AVERAGE,
                     "diff" : OP_CODE_SUBTRACT, "sub" : OP_CODE_SUBTRACT,
                     "sum" : OP_CODE_SUM, "add" : OP_CODE_SUM,
                     }

operation = OP_CODE_SUBTRACT

# Load a schedstats file
# Schedstats files are csv with a header and rows
# Note the data rows are comma-terminated, but the header is not
#          process,           parent, pids,  seconds,       cycles,  sec%,  cyc%, nsec%, ncyc%, CPU 0  sec%,  cyc%, nsec%, ncyc%, CPU 1  sec%,  cyc%, nsec%, ncyc%, CPU 2  sec%,  cyc%, nsec%, ncyc%, CPU 3  sec%,  cyc%, nsec%, ncyc%, CPU 4  sec%,  cyc%, nsec%, ncyc%, CPU 5  sec%,  cyc%, nsec%, ncyc%, CPU 6  sec%,  cyc%, nsec%, ncyc%, CPU 7  sec%,  cyc%, nsec%, ncyc%
#          Mapper,              750,    1,   5.1766,         0.00, 12.36,  0.00, 12.36,  0.00,        0.00,  0.00,  0.00,  0.00,        0.00,  0.00,  0.00,  0.00,        0.00,  0.00,  0.00,  0.00,        0.00,  0.00,  0.00,  0.00,        0.00,  0.00,  0.00,  0.00,       98.98,  0.00, 98.98,  0.00,        0.00,  0.00,  0.00,  0.00,        0.00,  0.00,  0.00,  0.00,

def load_stats(filepath):
    """
    :param filepath: *string* Full filepath to the csv stats file
    :return: List of rows, first row is the headers, all rows should have the
            same number of columns, all elements are stripped and numeric elements
            converted to float.
    """
    f = open(filepath, "r")

    # Read the header row, note the header row is not comma-terminated, but remove
    # the last element if empty, in case it is
    l = f.readline()
    headers = l.split(",")
    headers = [header.strip() for header in headers]
    if (headers[-1] == ""):
        headers.pop()

    # We expect 8 initial columns and 4 per core
    assert ((len(headers) - 9) % 4 == 0), "Found unexpected number of columns %d in %s, read %s, headers are %s" % (
            len(headers), repr(filepath), repr(l), repr(headers))

    rows = [headers]
    # Read the rows
    for l in f:
        # Use rsplit in the unlikely case the process name (first column) has commas
        fields = l.rsplit(",", len(headers) + 1)
        # Strip the fields, convert numeric fields to floats and drop the last
        # field because it's always empty (rows are comma terminated)
        fields = [field.strip() for field in fields[:2]] + [float(field.strip()) for field in fields[2:-1]]
        rows.append(fields)
        assert len(fields) == len(headers), "Lenght of fields is %d but headers is %d, %s %s" % (
                            len(fields), len(headers), repr(fields), repr(headers))

    return rows

def rows_match(row_a, row_b):
    """
    :param row_a: Row of schedstat fields
    :param row_b: Row of schedstat fields
    :return: True if row_a and row_b are a match, ie refer to the same process
        in two different schedstat files
    """
    # Do exact process name matching
    # XXX In the future this could do parent and partial name matching, eg match
    #  - Binder:2377_4,  lusvr.dabmobile to Binder:2383_4,  lusvr.dabmobile
    #  - or even Binder:686_4,   surfaceflinger to Binder:689_4, 689
    return (row_a[0] == row_b[0])

def operate_row(row_a, row_b, fn):
    """
    :param row_a: *list* Row of schedstat fields, may be None
    :param row_b: *list* Row of schedstat fields, may be None
    :param fn: Function that will be called with the numerical elements of row_a and row_b,
               The numerical element for row_b will be None if row_b was empty
    :return: Resulting of applying fn to each pair of numerical elements of row_a and row_b
    """

    row = row_a
    if (row_a is None):
        row_a = []
        row = row_b

    if (row_b is None):
        row_b = []

    num_cols = max(len(row_a), len(row_b))
    assert num_cols > 0, "At least one row must not be empty!!"

    # Column 0 is process name, 1 is parent, 2 is pids, 3 is seconds, then numeric columns
    res = row[:2]
    for col in xrange(2, num_cols):
        value_a = None if (col >= len(row_a)) else row_a[col]
        value_b = None if (col >= len(row_b)) else row_b[col]
        value = fn(value_a, value_b)
        res.append(value)

    return res

def operate_stats(stats_a, stats_b, fn):
    """
    :param stats_a: Rows of schedstats. Each row split into fields, first row is
                    headers
    :param stats_b: Rows of schedstats. Each row split into fields, first row is
                    headers
    :param fn: Function to apply
    :return:
    """

    # Operate the rows present in A, and maybe in B
    stats_c = [ stats_a[0] ]
    for row_a in stats_a[1:]:
        for row_b in stats_b[1:]:
            if (rows_match(row_a, row_b)):
                row = operate_row(row_a, row_b, fn)
                stats_c.append(row)
                break
        else:
            # This row doesn't exist in B
            row = operate_row(row_a, None, fn)
            stats_c.append(row)

    # Operate the rows in B but not in A
    for row_b in stats_b[1:]:
        for row_a in stats_a[1:]:
            if (rows_match(row_a, row_b)):
                break
        else:
            row = operate_row(None, row_b, fn)
            stats_c.append(row)

    return stats_c

def diff_stats(stats_a, stats_b):

    # Do A - B
    stats_c = operate_stats(stats_a, stats_b, lambda a, b : (a if a is not None else 0) -
                                                            (b if b is not None else 0))

    # Go through and change the process names:
    # - processes in a but not in b, prefix them with +
    # - processes in b but not in a, prefix them with -

    for row_c in stats_c:
        for row_a in stats_a:
            if (rows_match(row_c, row_a)):
                for row_b in stats_b:
                    if (rows_match(row_c, row_b)):
                        # Row on both, keep name
                        break
                else:
                    # Row only on A, prefix with +
                    row_c[0] = "+" + row_c[0]
                break
        else:
            # Row not in A, has to be only in B, prefix with -
            row_c[0] = "-" + row_c[0]

    return stats_c

def print_stats(stats):
    # Output the generated schedstat file

    headers = stats[0]
    fmt_mask = " %16s, %16s, %4s, %8s, %12s, "
    for cpu in xrange(((len(headers) - 4) / 4)):
        fmt_mask += "%6s, %6s, %6s, %6s, "
    print fmt_mask % tuple(headers)

    # Output sorted by absolute values of columns 4,5,6,7
    for row in sorted(stats[1:], reverse=True,
                      cmp=lambda x, y: cmp(
                          abs(x[4]) if (x[4] != 0) else abs(x[5]),
                          abs(y[4]) if (y[4] != 0) else abs(y[5]))):
        fmt_mask = "%16s, %16s, %4d, %8.4f, %12.2f, "
        for cpu in xrange(((len(row) - 4) / 4)):
            if (cpu > 0):
                fmt_mask += "     "
            fmt_mask += "%6.2f, %6.2f, %6.2f, %6.2f, "

        # left align - or + signs in the process name, these come from a diff
        # operation
        name = row[0]
        if (name[0] in ['-', '+']):
            fmt_mask = name[0] + fmt_mask
            name = name[1:]
        else:
            fmt_mask = " " + fmt_mask

        print fmt_mask % tuple([name] + row[1:])


if (__name__ == "__main__"):
    logging_format = "%(asctime).23s %(levelname)s:%(filename)s(%(lineno)d) [%(thread)d]: %(message)s"

    logger_handler = logging.StreamHandler()
    logger_handler.setFormatter(logging.Formatter(logging_format))
    logger.addHandler(logger_handler)
    logger.setLevel(logging.INFO)

    first_filepath_index = 1

    # The first argument should be an operation
    if ((len(sys.argv) <2) or (sys.argv[1] not in OP_NAMES_TO_CODE)):
        print "Tool to manipulate psytrace schedstat files"
        print "https://our.intern.facebook.com/intern/wiki/Users/atejada/psytrace/#statstool.py"
        print
        print "usage: statstool.py [avg|sum|diff] filepathpattern1 filepathpattern2 ..."
        print "Operations:"
        print "- sum: output a schedstat file sum of filepathpattern1 filepathpattern2 ..."
        print "- avg: output a schedstat file average of filepathpattern1 filepathpattern2 ..."
        print "- diff: output a schedstat file difference of filepathpattern1 minus filepathpattern2"
        sys.exit(-1)

    logger.info("Starting")

    operation = OP_NAMES_TO_CODE[sys.argv[1]]
    first_filepath_index += 1

    if (operation == OP_CODE_SUBTRACT):
        # Diff is followed by two filepaths A and B to generate A - B

        src_filepath = sys.argv[first_filepath_index]
        stats_a = load_stats(src_filepath)

        src_filepath = sys.argv[first_filepath_index + 1]
        stats_b = load_stats(src_filepath)

        stats_c = diff_stats(stats_a, stats_b)

        print_stats(stats_c)


    elif ((operation == OP_CODE_AVERAGE) or (operation == OP_CODE_SUM)):
        # Sum and average are followed by one or more filepaths, optionally with
        # wildcards

        # Sum the stats
        num_stats = 0
        stats_c = None
        for filepathpattern in sys.argv[1:]:
            for filepath in glob.glob(filepathpattern):
                logger.info("Loading trace file %s" % repr(filepath))
                stats_a = load_stats(filepath)
                if (stats_c is None):
                    stats_c = stats_a
                else:
                    stats_c = operate_stats(stats_a, stats_c, lambda a, b: (a if a is not None else 0) +
                                                                           (b if b is not None else 0))
                num_stats += 1

        if (operation == OP_CODE_AVERAGE):
            # Average all the stats
            stats_c = operate_stats(stats_c, [], lambda a, b: a / num_stats)

        print_stats(stats_c)
