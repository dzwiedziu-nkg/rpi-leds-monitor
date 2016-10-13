#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""stats module v1.0-alpha under GPL 3.0 license
Copyright (C) by Michał Niedźwiecki 2016

Get stats about disk usage and network usage.

Disk stats is acquired from /proc/diskstat file.
Network stats is acquired from /sys/class/net/*/statistics/* files.

Usage:
    See: Stats class. You can use read_disk_stats and read_network_stats too.

Example:
    Show received and send bytes via wlan0 in 1 second.

    stats = Stats()
    while True:
        time.sleep(1)
        stats.update_all_stats()
        diffs = stats.get_values_different()
        print(str(diffs['network']['wlan0']['rx_bytes']) + " " + str(diffs['network']['wlan0']['tx_bytes']))

"""
import datetime
import glob


disk_stats_values = ['major_number',
    'minor_number',
    'device_name',
    'reads_completed_successfully',
    'reads_merged',
    'sectors_read',
    'time_spent_reading',
    'writes_completed',
    'writes_merged',
    'sectors_written',
    'time spent writing',
    'IOs_currently_in_progress',
    'time_spent_doing_IOs',
    'weighted_time_spent_doing_IOs']


def values_different(old_tree, new_tree):
    """
    Different between new values and old values.

    This method make a subtraction of values from new_tree and old_tree. new_tree and old_tree is a tree based on dict.
    Branches is a dict objects, nodes is a int values. Other values is only copied from new_tree.
    :param old_tree: tree with old values
    :param new_tree: tree with new values
    :return: new tree with branch structure copied from new_tree and node values as subtraction of new_tree nodes
    old_tree nodes
    """
    ret = {}
    for (key, value) in new_tree.items():
        if isinstance(value, dict):
            ret[key] = values_different(old_tree[key], new_tree[key])
        elif isinstance(value, int):
            if key in old_tree:
                ret[key] = new_tree[key] - old_tree[key]
            else:
                ret[key] = 0
        else:
            ret[key] = value

    return ret


def read_disk_stats():
    """
    Read disk stats from /proc/diskstats file.
    :return: two-level dictionary where first level is the device name and second level is the stat name
    """
    global disk_stats_values

    stats = {}
    with open("/proc/diskstats", "r") as f:
        lines = f.readlines()

    for (i, line) in enumerate(lines):
        split = line.split()
        device = {}
        for (j, value) in enumerate(split):
            if j == 2:
                device[disk_stats_values[j]] = value
            else:
                device[disk_stats_values[j]] = int(value)
        stats[split[2]] = device

    return stats


def read_network_stats():
    """
    Read network stats from /sys/class/net/*/statistics/* files.
    :return: two-level dictionary where first level is the network interface name and second level is the stat name
    """
    interfaces = glob.glob('/sys/class/net/*')
    stats = {}

    for interface in interfaces:
        stat = {}
        names = glob.glob(interface + '/statistics/*')

        for name in names:
            with open(name, "r") as f:
                lines = f.readlines()
            stat[name.split('/')[-1]] = int(lines[0])

        stats[interface.split('/')[-1]] = stat

    return stats


class Stats:
    """
    Keeps time and values from latest read of stats and previous read of stats.

    Usage:
        Create new object of this class. Now you can read current stats from current_values field. Then wait for example
        1 second and run update_all_stats(). Now you can use get_values_different() to get difference from previous
        read of stats.

    Attributes:
        current_checked_time (int): timestamp of latest stats read
        previous_checked_time (int): timestamp of previous stats read

        current_values (dict): contains latest values of stats
        previous_values (dict): contains previous values of stats

        current_values and previous_values is a tree structure based on dict as branches and int as nodes. In 99% times
        both trees have the same structure. Only values of nodes is different.
    """
    current_checked_time = None
    previous_checked_time = None

    current_values = {}
    previous_values = {}

    def __init__(self):
        """
        Initialize object and read all current stats.
        """
        self.previous_checked_time = datetime.datetime.now().timestamp()
        self.update_all_stats()

    def update_checked_time(self):
        """
        Set current time as current_checked_time and previous_checked_time as old current_checked_time value.
        :return:
        """
        self.previous_checked_time = self.current_checked_time
        self.current_checked_time = datetime.datetime.now().timestamp()

    def update_value(self, name, value):
        """
        Set current value as given and previous value and old current value.
        :param name: value name as str
        :param value: value as int value (single) or tree structure based on dict
        """
        if name in self.current_values:
            self.previous_values[name] = self.current_values[name]

        self.current_values[name] = value

    def update_all_stats(self):
        """
        Read disk stats and network stats and store as current stats. Earlier old current stats saved as previous stats.
        """
        self.update_value('storage', read_disk_stats())
        self.update_value('network', read_network_stats())
        self.update_checked_time()

    def get_time_different(self):
        """
        Subtraction of latest time of stats read and old time of stats read.
        :return: second between latest stats read and previous stat read.
        """
        return self.current_checked_time - self.previous_checked_time

    def get_values_different(self):
        """
        Subtraction of latest stats values and previous stats values.
        :return: tree based on dict with subtraction of latest stats values and previous stats values
        """
        return values_different(self.previous_values, self.current_values)
