#!/usr/bin/env python3
import subprocess
import sys

if sys.version_info.major < 3 or sys.version_info.minor < 6:
    raise EnvironmentError('package requires python3.6+!')
subprocess.run('python3 -m pip install -r requirements.txt'.split(' '))
