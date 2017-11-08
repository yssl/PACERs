import os, subprocess
from unicode import *

############################################
# version functions
def getCMakeVersionWindows():
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

def getCMakeVersionPosix():
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

def getVisulCppVersionWindows():
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


