#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""stats module v1.0-alpha under GPL 3.0 license
Copyright (C) by Michał Niedźwiecki 2016

Ping continuously to given host and store in output file the timestamp of the last successful ping and the last failed
ping.

Usage:
    See: Ping class.

"""
import datetime
import time
import subprocess
import threading


global_lock = threading.Lock()


def synchronized(func, lock=global_lock):
    def do_synchronize(*args, **kwargs):
        lock.acquire()
        try:
            return func(*args, **kwargs)
        finally:
            lock.release()
    return do_synchronize


class Ping:
    last_ping_success = 0
    last_ping_error = 0

    timeout = 60
    interval = 60

    do_ping_break = False

    def __init__(self, host, timeout=60, interval=60):
        self.host = host
        self.timeout = timeout
        self.interval = interval
        self.on_update = self.empty_func
        self.on_process_restarted = self.empty_func

    @staticmethod
    def empty_func():
        pass

    @synchronized
    def get_last_ping_success(self):
        return self.last_ping_success

    @synchronized
    def get_last_ping_error(self):
        return self.last_ping_error

    @synchronized
    def update_last_ping_success(self):
        self.last_ping_success = datetime.datetime.now().time()

    @synchronized
    def update_last_ping_error(self):
        self.last_ping_error = datetime.datetime.now().time()

    def ping_process_loop(self):
        process = subprocess.Popen(['ping', '-i', str(self.interval), '-t', str(self.timeout), self.host],
                                   stdout=subprocess.PIPE)

        while process.poll() is None and not self.do_ping_break:
            line = process.stdout.readline()
            if b"time=" in line:
                self.update_last_ping_success()
            elif line.startswith(b"PING"):
                pass
            else:
                self.update_last_ping_error()

            self.on_update()

        if process.returncode != 0:
            self.update_last_ping_error()

        self.on_update()

        return process.returncode

    def ping_loop(self):
        while not self.do_ping_break:
            ret = self.ping_process_loop()
            time.sleep(self.interval)
            self.on_process_restarted(ret)

    def start(self):
        self.do_ping_break = False
        t = threading.Thread(target=self.ping_loop)
        t.daemon = True
        t.start()
        return t

    @synchronized
    def stop(self):
        self.do_ping_break = True
