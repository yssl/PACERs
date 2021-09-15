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
    stdInputs = projInfo['stdInputs']
    cmdArgss = projInfo['cmdArgss']

    exitTypeList, stdoutStrList, stdInputList, cmdArgsList = runProj(submissionType, submissionDir, projName, filesInProj, stdInputs, cmdArgss, timeOut, interpreterCmd, preShellCmd)

    return exitTypeList, stdoutStrList, stdInputList, cmdArgsList

############################################
# run functions

# return exitType, output(stdout) of target program
# exitType:
#   -1 - execution failed due to internal error (not supported extension, not built yet)
#   0 - normal exit
#   1 - forced kill due to timeout

def runProj(submissionType, submissionDir, projName, projSrcFileNames, stdInputs, cmdArgss, timeOut, interpreterCmd, preShellCmd):
    exitTypeList = []
    stdoutStrList = []
    stdInputList = []
    cmdArgsList = []

    len_std = len(stdInputs)
    len_cmd = len(cmdArgss)
    len_longer = len_std if len_std > len_cmd else len_cmd
    for i in range(len_longer):
        i_std = i if i < len_std else len_std-1
        i_cmd = i if i < len_cmd else len_cmd-1
        stdInput = stdInputs[i_std]
        cmdArg = cmdArgss[i_cmd]

        if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
            exitType, stdoutStr = run_single_source(submissionDir, projName, projSrcFileNames[0], stdInput, cmdArg, timeOut, interpreterCmd, preShellCmd)
        elif submissionType==CMAKE_PROJECT:
            exitType, stdoutStr = run_cmake(submissionDir, projName, stdInput, cmdArg, timeOut, preShellCmd)
        elif submissionType==MAKE_PROJECT:
            exitType, stdoutStr = run_make(submissionDir, projName, stdInput, cmdArg, timeOut, preShellCmd)
        elif submissionType==VISUAL_CPP_PROJECT:
            exitType, stdoutStr = run_vcxproj(submissionDir, projName, stdInput, cmdArg, timeOut, preShellCmd)

        exitTypeList.append(exitType)
        stdoutStrList.append(stdoutStr)
        stdInputList.append(stdInput)
        cmdArgsList.append(cmdArg)

    return exitTypeList, stdoutStrList, stdInputList, cmdArgsList

####
# run_single functions
def run_single_source(srcRootDir, projName, singleSrcFileName, stdInput, cmdArg, timeOut, interpreterCmd, preShellCmd):
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
        return __run(runcmd, runcwd, stdInput, cmdArg, timeOut, preShellCmd)
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
def run_cmake(srcRootDir, projName, stdInput, cmdArg, timeOut, preShellCmd):
    runcmd = runcmd_cmake(srcRootDir, projName)
    runcwd = srcRootDir
    return __run(runcmd, runcwd, stdInput, cmdArg, timeOut, preShellCmd)

def runcmd_cmake(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    execName = projName
    with open(opjoin(srcRootDir,'CMakeLists.txt'), 'r') as f:
        tokens = re.split(' |\t|\n|\(|\)', f.read())
        tokens = [x for x in tokens if x]   # remove empty strings
        for i in range(len(tokens)):
            if tokens[i].lower()=='add_executable' and i < len(tokens)-1:
                execName = tokens[i+1]
    return os.path.abspath(opjoin(buildDir, execName))

####
# run_make functions
def run_make(srcRootDir, projName, stdInput, cmdArg, timeOut, preShellCmd):
    runcmd = runcmd_make(srcRootDir, projName)
    runcwd = srcRootDir
    return __run(runcmd, runcwd, stdInput, cmdArg, timeOut, preShellCmd)

def runcmd_make(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    execName = projName

    ################
    # NOT USED NOW becuase this approach cannot deal with cases where default target name != executable name.
    ## This code assumes that the default target name is identical to the executable file name, so reports errors when
    ## 1) default target name != executable name
    ## 2) no executable file name is specified in the commands
    ## 3) additionally, there are some warning messages from 'make -p' which results in incorrect default target name extraction
    # try:
        # grepStr = subprocess.check_output("make -p --just-print | grep 'DEFAULT_GOAL'", cwd=srcRootDir, stderr=subprocess.STDOUT, shell=True)
    # except subprocess.CalledProcessError as e:
        # execName = 'Failed to find the executable name in Makefile'
    # else: 
        # execName = grepStr.split()[2]
    ################

    ################
    # NOT USED NOW becuase this approach cannot deal with cases where source files also have the exeutable permission (e.g. uploaded from Windows)
    ## To find the executable name, now we use os.access(filename, os.X_OK)
    # execNames = [fname for fname in os.listdir(buildDir) if os.access(opjoin(buildDir, fname), os.X_OK) and os.path.isfile(opjoin(buildDir, fname))]
    # if len(execNames)==0:
        # execName = 'Failed to find the executable name in the output directory %s'%buildDir
    # else:
        # execName = execNames[0]
    ################

    ################
    # IN USE NOW
    # the executable file is a file (in the build dir) that
    # 1) has an executable permission
    # 2) has DYN or EXEC as Type: in the readelf -h output.
    execCandiNames = [fname for fname in os.listdir(buildDir) if os.access(opjoin(buildDir, fname), os.X_OK) and os.path.isfile(opjoin(buildDir, fname))]
    if len(execCandiNames)==0:
        execName = 'Failed to find any file that has an executable permission in the output directory %s'%buildDir
    else:
        execName = 'Failed to find any ELF executable file in the output directory %s'%buildDir
        for execCandiName in execCandiNames:
            try:
                grepStr = subprocess.check_output("readelf -h %s | grep 'Type:'"%execCandiName, cwd=buildDir, stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                # print e
                # print 'Failed to execute readelf to find executable file'
                pass
            else: 
                if grepStr.split()[1]=='DYN' or grepStr.spilt()[1]=='EXEC':
                    execName = execCandiName
    ################
            
    return os.path.abspath(opjoin(buildDir, execName))

####
# run_vcxproj functions
def run_vcxproj(srcRootDir, projName, stdInput, cmdArg, timeOut, preShellCmd):
    runcmd = runcmd_vcxproj(srcRootDir, projName)
    runcwd = srcRootDir
    return __run(runcmd, runcwd, stdInput, cmdArg, timeOut, preShellCmd)

def runcmd_vcxproj(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    vcxprojNames = glob.glob(opjoin(srcRootDir, '*.vcxproj'))
    vcxprojNames.extend(glob.glob(opjoin(srcRootDir, '*.vcxproj')))
    execName = os.path.splitext(os.path.basename(vcxprojNames[0]))[0]
    return os.path.abspath(opjoin(buildDir, execName))

def __run(runcmd, runcwd, stdInput, cmdArg, timeOut, preShellCmd):
    # append newline to finish stdin user input and flush input buffer
    realStdInput = stdInput+'\n'

    try:
        if preShellCmd!='':
            if os.name=='posix':
                shell = '/bin/bash -c'
                connector = ';'
            else:
                shell = 'cmd /c'
                connector = '&'
            runcmd = '%s %s %s %s'%(shell, preShellCmd, connector, runcmd)

        proc = subprocess.Popen(shlex.split(toString(runcmd)+' '+toString(cmdArg), posix=os.name=='posix'), cwd=toString(runcwd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    except OSError:
        return -1, 'Cannot execute \'%s\' \n(Maybe an executable file has not been created (compiled languages) or \n--interpreter-cmd should have been specified (interpreted languages))'%runcmd

    if timeOut != 0:
        # call onTimeOut() after timeOut seconds
        timer = threading.Timer(timeOut, onTimeOut, [proc])
        timer.start()

        # block until proc is finished
        try:
            stdoutStr, stderrStr = proc.communicate(realStdInput)
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
        stdoutStr, stderrStr = proc.communicate(realStdInput)
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
