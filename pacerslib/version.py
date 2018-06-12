################################################################################
# version.py

# Copyright (C) 2016-2017 Yoonsang Lee

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
import os, subprocess
from unicode import *

############################################
# version functions
def getCMakeVersionWindows(ignored):
    versionStrs = []
    # cmake
    try: versionStr = toUnicode(subprocess.check_output('(vcvars32.bat > nul) && cmake --version', stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e: versionStrs.append(e.output)
    else: versionStrs.append(versionStr.split(os.linesep)[0])

    # nmake
    try: versionStr = toUnicode(subprocess.check_output('(vcvars32.bat > nul) && nmake /help', stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e: versionStrs.append(e.output)
    else: versionStrs.append(versionStr.split(os.linesep)[1])

    # cl
    try: versionStr = toUnicode(subprocess.check_output('(vcvars32.bat > nul) && cl /help', stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e: versionStrs.append(e.output)
    else: versionStrs.append(versionStr.split(os.linesep)[0])

    return versionStrs

def getCMakeVersionPosix(ignored):
    versionStrs = []
    # cmake
    try: versionStr = toUnicode(subprocess.check_output('cmake --version', stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e: versionStrs.append(e.output)
    else: versionStrs.append(versionStr.split(os.linesep)[0])

    # nmake
    try: versionStr = toUnicode(subprocess.check_output('make -v', stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e: versionStrs.append(e.output)
    else: versionStrs.append(versionStr.split(os.linesep)[0])

    # cl
    try: versionStr = toUnicode(subprocess.check_output('gcc --version', stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e: versionStrs.append(e.output)
    else: versionStrs.append(versionStr.split(os.linesep)[0])

    return versionStrs

def getVisulCppVersionWindows(ignored):
    versionStrs = []
    # msbuild
    try: versionStr = toUnicode(subprocess.check_output('(vcvars32.bat > nul) && msbuild /help', stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e: versionStrs.append(e.output)
    else: versionStrs.append(versionStr.split(os.linesep)[0])

    # cl
    try: versionStr = toUnicode(subprocess.check_output('(vcvars32.bat > nul) && cl /help', stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e: versionStrs.append(e.output)
    else: versionStrs.append(versionStr.split(os.linesep)[0])

    return versionStrs

def getPythonVersion(interpreterCmd):
    pythonCmd = interpreterCmd

    versionStrs = []
    # python
    try: versionStr = toUnicode(subprocess.check_output('%s --version'%pythonCmd, stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e: versionStrs.append(e.output)
    else: versionStrs.append(versionStr.split(os.linesep)[0])

    return versionStrs
