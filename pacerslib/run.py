################################################################################
# run.py

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
import os, subprocess, threading, glob, re, shlex
from global_const import *
from unicode import *

def runOneProj(projInfo, timeOut, interpreterCmd, preShellCmd):
    submissionType = projInfo['submissionType']
    projName = projInfo['projName']
    submissionDir = projInfo['submissionDir']
    filesInProj = projInfo['filesInProj']
    userInputs = projInfo['userInputs']

    exitTypeList = []
    stdoutStrList = []
    userInputList = userInputs
    exitTypeList, stdoutStrList = runProj(submissionType, submissionDir, projName, filesInProj, userInputs, timeOut, interpreterCmd, preShellCmd)

    return exitTypeList, stdoutStrList, userInputList

############################################
# run functions

# return exitType, output(stdout) of target program
# exitType:
#   -1 - execution failed due to internal error (not supported extension, not built yet)
#   0 - normal exit
#   1 - forced kill due to timeout

def runProj(submissionType, submissionDir, projName, projSrcFileNames, userInputs, timeOut, interpreterCmd, preShellCmd):
    exitTypeList = []
    stdoutStrList = []

    for userInput in userInputs:

        if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
            exitType, stdoutStr = run_single_source(submissionDir, projName, projSrcFileNames[0], userInput, timeOut, interpreterCmd, preShellCmd)
        elif submissionType==CMAKE_PROJECT:
            exitType, stdoutStr = run_cmake(submissionDir, projName, userInput, timeOut, preShellCmd)
        elif submissionType==VISUAL_CPP_PROJECT:
            exitType, stdoutStr = run_vcxproj(submissionDir, projName, userInput, timeOut, preShellCmd)

        exitTypeList.append(exitType)
        stdoutStrList.append(stdoutStr)

    return exitTypeList, stdoutStrList

####
# run_single functions
def run_single_source(srcRootDir, projName, singleSrcFileName, userInput, timeOut, interpreterCmd, preShellCmd):
    extension = os.path.splitext(singleSrcFileName)[1].lower()
    if extension in gSourceExt:
        runcmd = eval(gSourceExt[extension]['runcmd-single-source-func'])(srcRootDir, projName)
        if interpreterCmd!='':
            runcmd = interpreterCmd + ' ' + runcmd  # python with specified command
        else:
            if 'default-interpreter-cmd' in gSourceExt[extension]:
                runcmd = gSourceExt[extension]['default-interpreter-cmd'] + ' ' + runcmd  # python with default command
            else:
                pass    # c & c++
        runcwd = eval(gSourceExt[extension]['runcwd-single-source-func'])(srcRootDir, projName)
        return __run(runcmd, runcwd, userInput, timeOut, preShellCmd)
    else:
        return run_single_else(extension)

def runcmd_single_c_cpp(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    return os.path.abspath(opjoin(buildDir, '%s'%projName))

def runcwd_single_c_cpp(srcRootDir, projName):
    # run output executable from srcRootDir
    return srcRootDir
    # run output executable from buildDir
    # buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    # return buildDir

def runcmd_single_py(srcRootDir, projName):
    return os.path.abspath(opjoin(srcRootDir, '%s.py'%projName))

def runcwd_single_py(srcRootDir, projName):
    # run output executable from srcRootDir
    return srcRootDir

def run_single_else(extension):
    errorMsg = 'Running %s is not supported.'%extension
    return -1, errorMsg 

####
# run_cmake functions
def run_cmake(srcRootDir, projName, userInput, timeOut, preShellCmd):
    runcmd = runcmd_cmake(srcRootDir, projName)
    runcwd = runcwd_single_c_cpp(srcRootDir, projName)
    return __run(runcmd, runcwd, userInput, timeOut, preShellCmd)

def runcmd_cmake(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    execName = projName
    with open(opjoin(srcRootDir,'CMakeLists.txt'), 'r') as f:
        tokens = re.split(' |\n|\(|\)', f.read())
        for i in range(len(tokens)):
            if tokens[i].lower()=='add_executable' and i < len(tokens)-1:
                execName = tokens[i+1]
    return os.path.abspath(opjoin(buildDir, execName))

####
# run_vcxproj functions
def run_vcxproj(srcRootDir, projName, userInput, timeOut, preShellCmd):
    runcmd = runcmd_vcxproj(srcRootDir, projName)
    runcwd = runcwd_single_c_cpp(srcRootDir, projName)
    return __run(runcmd, runcwd, userInput, timeOut, preShellCmd)

def runcmd_vcxproj(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    vcxprojNames = glob.glob(opjoin(srcRootDir, '*.vcxproj'))
    vcxprojNames.extend(glob.glob(opjoin(srcRootDir, '*.vcxproj')))
    execName = os.path.splitext(os.path.basename(vcxprojNames[0]))[0]
    return os.path.abspath(opjoin(buildDir, execName))

def __run(runcmd, runcwd, userInput, timeOut, preShellCmd):
    # append newline to finish stdin user input and flush input buffer
    realInput = userInput+'\n'

    # # insert newline character after each single character in userInput 
    # # for example, for a user input for scanf("%c", ...);
    # # TODO: make this as cmd argument
    # realInput = ''
    # for i in range(len(userInput)):
        # realInput += userInput[i]+'\n'

    try:
        if preShellCmd!='':
            if os.name=='posix':
                shell = '/bin/bash -c'
                connector = ';'
            else:
                shell = 'cmd /c'
                connector = '&'
            runcmd = '%s %s %s %s'%(shell, preShellCmd, connector, runcmd)

        proc = subprocess.Popen(shlex.split(toString(runcmd), posix=os.name=='posix'), cwd=toString(runcwd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    except OSError:
        return -1, 'Cannot execute \'%s\' \n(Maybe an executable file has not been created (compiled languages) or \n--interpreter-cmd should have been specified (interpreted languages))'%runcmd

    if timeOut != 0:
        # call onTimeOut() after timeOut seconds
        timer = threading.Timer(timeOut, onTimeOut, [proc])
        timer.start()

        # block until proc is finished
        try:
            stdoutStr, stderrStr = proc.communicate(realInput)
        except Exception as e:
            return -1, toUnicode(str(type(e)) + ' ' + str(e))

        if timer.is_alive():    # if proc has finished without calling onTimeOut() (finished before timeOut)
            timer.cancel()
            if proc.returncode==0:
                return 0, toUnicode(stdoutStr)
            else:
                return -1, toUnicode(stdoutStr) + toUnicode(stderrStr)
        else:
            return 1, toUnicode(stdoutStr) # 1 means 'forced kill due to timeout'
    else:
        # block until proc is finished
        stdoutStr, stderrStr = proc.communicate(realInput)
        if proc.returncode==0:
            return 0, toUnicode(stdoutStr)
        else:
            return -1, toUnicode(stdoutStr) + toUnicode(stderrStr)

def onTimeOut(proc):
    if os.name=='posix':
        proc.kill()
    else:
        # windows specific - to kill both cmd.exe and its subprocess (required when --pre-shell-cmd is specified)
        # http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=proc.pid))
