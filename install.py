#!/usr/bin/env python3
import subprocess
import sys

if sys.version_info.major != 3:
    print('python3+ required')
if sys.version_info.minor < 6:
    print('python3.6+ required')

# install packages
subprocess.run('python3 -m pip install -r requirements.txt')

