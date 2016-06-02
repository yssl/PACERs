#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
PACERs
    : Programming Assignments Compiling, Executing, and Reporting system

Requirements:
    python 2.x
    cmake
    Pygments
        : Install in Windows - "pip install pygments"
          Install in Linux - "sudo pip install pygments" or "sudo apt-get install python-pygments"
    Unidecode (install via pip install unidecode)
        : Install in Windows - "pip install unidecode"
          Install in Linux - "sudo pip install unidecode" or "sudo apt-get install python-unidecode"

Tested language, compiler(interpreter), platform:
    C - Microsoft Visual Studio 2010 - Windows 10 (Kor)
    C - Microsoft Visual C++ 2010 Express - Windows 8.1 with Bing (Eng)
    C - gcc 4.8.4 - Ubuntu 14.04 (Kor)

Required environment setting:
    On MS Windows, please add following paths to the system path. XX.X means your Visual Studio version.
        C:\Program Files (x86)\Microsoft Visual Studio XX.X\VC\bin
        C:\Program Files (x86)\Microsoft Visual Studio XX.X\Common7\IDE

Quick start:
    1) Run: git clone https://github.com/yssl/PACERs.git

    2) On Linux, run: ./pacers.py test-assignments/C/assignment-1
       On Windows, run: pacers.py test-assignments\C\assignment-1

    3) Open ./output/assignment-1/report-assignment-1.html in any web browser
    The generated html file is written in unicode (utf-8), so if your browser shows broken characters
    please try to change the text encoding option for the page to unicode or utf-8.
    
Other examples:
    pacers.py test-assignments/C/assignment-2 --user-input "3 5"
    pacers.py test-assignments/C/assignment-2 --user-input "1 2" "3 4"
    pacers.py test-assignments/C/assignment-3 --user-dict "{'1':[''], '2':['2 5', '10 20']}"
    pacers.py test-assignments/C/assignment-4 --user-dict "{'1':[''], '2':['2 5', '10 20']}"

usage: pacers.py [-h] [--user-input USER_INPUT [USER_INPUT ...]]
                 [--user-dict USER_DICT] [--timeout TIMEOUT] [--run-only]
                 [--assignment-alias ASSIGNMENT_ALIAS]
                 [--output-dir OUTPUT_DIR] [--source-encoding SOURCE_ENCODING]
                 assignment_dir

Programming Assignments Compiling, Executing, and Reporting system

positional arguments:
  assignment_dir        A direcory that has submitted files.
                        In assignment_dir, one source file runs one program.
                        Each submission might have only one source file or a
                        zip file or a directory including multiple source files

optional arguments:
  -h, --help            show this help message and exit
  --user-input USER_INPUT [USER_INPUT ...]
                        Specify USER_INPUT to be sent to the stdin of target
                        programs. This option should be located after
                        assignment_dir if no other optional arguments are
                        given. Two types of user input are available.
                        default is an empty string.

                        | Type     | Example                  | Example's meaning                          |
                        |----------|--------------------------|--------------------------------------------|
                        | Single   | --user-input 15          | run each source file with input 15         |
                        | value    | --user-input "hello"     | run each source file with input "hello"    |
                        |          | --user-input "1 2"       | run each source file with input "1 2"      |
                        |----------|--------------------------|--------------------------------------------|
                        | Multiple | --user-input 1 2 3       | run each source 3 times: with 1, 2, 3      |
                        | values   | --user-input "1 2" "3 4" | run each source 2 times: with "1 2", "3 4" |

  --user-dict USER_DICT
                        Specify USER_DICT to be sent to the stdin of target
                        programs. Argument should be python dictionary
                        representation. Each 'key' of the dictionary item
                        is 'suffix' that should match with the last parts of
                        each source file name. 'value' is user input for
                        those matched source files.
                        If both --user-input and --user-dict are specified,
                        only --user-dict is used.

                        Example:
                        --user-dict {'1':['1','2'], '2':['2,'5','7']}

                        runs a source file whose name ends with '1'
                        (e.g. prob1.c) 2 times (with '10', '20')
                        and run a source file whose name ends with
                        '2' (e.g. prob2.c) 3 times (with '2','5','7').

  --timeout TIMEOUT     Each target program is killed when TIMEOUT(seconds)
                        is reached. Useful for infinite loop cases.
                        default: 2.0
  --run-only            When specified, run each target program without build.
                        You may use it when you want change USER_INPUT without
                        build. if the programming language of source files
                        does not require build process, PACERs
                        automatically skips the build process without
                        specifying this option.
  --assignment-alias ASSIGNMENT_ALIAS
                        Specify ASSIGNMENT_ALIAS for each assignment_dir.
                        ASSIGNMENT_ALIAS is used when making a sub-directory
                        in OUTPUT_DIR and the final report file.
                        default: "basename" of assignment_dir (bar if
                        assignment_dir is /foo/bar/).
  --output-dir OUTPUT_DIR
                        Specify OUTPUT_DIR in which the final report file
                        and build output files to be generated.
                        Avoid including hangul characters in its full path.
                        default: .\output
  --source-encoding SOURCE_ENCODING
                        Specify SOURCE_ENCODING in which source files
                        are encoded. You don't need to use this option if
                        source code only has english characters or
                        the platform where source code is written and
                        the platform PACERs is running is same.
                        If source files are written in another platform,
                        you might need to specify default encoding for
                        the platform to run PACERs correctly.
                        default: system default encoding
'''

import os, sys, shutil, subprocess, threading, time, argparse, zipfile, fnmatch
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter
from unidecode import unidecode

if os.name=='nt':
    reload(sys)
    sys.setdefaultencoding('cp949')
elif os.name=='posix':
    reload(sys)
    sys.setdefaultencoding('utf-8')

############################################
# utility functions
def unico2decoPath(unicoPath, deco2unicoMap):
    unicoTokens = os.path.normpath(unicoPath).split(os.sep)
    hasExt = '.' in unicoTokens[-1]
    if hasExt:
        name, ext = os.path.splitext(unicoTokens[-1])
        unicoTokens[-1] = name
    decoTokens = []
    for unicoToken in unicoTokens:
        decoToken = unidecode(unicoToken)
        decoToken = decoToken.replace(' ', '_')
        decoToken = decoToken.replace('(', '_')
        decoToken = decoToken.replace(')', '_')
        if decoToken not in deco2unicoMap:
            deco2unicoMap[decoToken] = unicoToken
        decoTokens.append(decoToken)
    decoPath = reduce(os.path.join, decoTokens)
    if hasExt:
        decoPath += ext
    return decoPath

def deco2unicoPath(decoPath, deco2unicoMap):
    decoTokens = os.path.normpath(decoPath).split(os.sep)
    hasExt = '.' in decoTokens[-1]
    if hasExt:
        name, ext = os.path.splitext(decoTokens[-1])
        decoTokens[-1] = name
    unicoTokens = []
    for decoToken in decoTokens:
        unicoToken = deco2unicoMap[decoToken]
        unicoTokens.append(unicoToken)
    unicoPath = reduce(os.path.join, unicoTokens)
    if hasExt:
        unicoPath += ext
    return unicoPath

############################################
# functions for preparation

def unzipInAssignDir(assignDir):
    zipFileNames = []
    unzipDirNames = []
    for name in os.listdir(assignDir):
        filePath = opjoin(assignDir, name)
        if zipfile.is_zipfile(filePath):
            with zipfile.ZipFile(filePath, 'r') as z:
                unzipDir = os.path.splitext(filePath)[0]
                unzipDir = unzipDir.strip()
                z.extractall(unzipDir)
                zipFileNames.append(name)
                unzipDirNames.append(unzipDir)
    return zipFileNames, unzipDirNames

def removeUnzipDirsInAssignDir(assignDir, unzipDirNames):
    for d in unzipDirNames:
        shutil.rmtree(opjoin(assignDir, d))

def copyAndDecodeAssignDirToOutDirRecursive(assignDir, outputDir, assignAlias, deco2unicoMap, doNotCopy):
    decodeAlias = unico2decoPath(unicode(assignAlias), deco2unicoMap)
    srcDir = assignDir
    destDir = opjoin(outputDir, decodeAlias)

    if not doNotCopy:
        if os.path.exists(destDir):
            shutil.rmtree(destDir)
            time.sleep(.01)
        shutil.copytree(assignDir, destDir)
    else:
        if not os.path.exists(destDir):
            os.mkdir(destDir)
        try:
            os.remove(getReportFilePath(gArgs))
        except OSError:
            pass

    if doNotCopy:
        for root, dirs, files in os.walk(assignDir, topdown=False):
            for name in dirs:
                decoName = unico2decoPath(unicode(name), deco2unicoMap)
            for name in files:
                decoName = unico2decoPath(unicode(name), deco2unicoMap)
    else:
        for root, dirs, files in os.walk(destDir, topdown=False):
            for name in dirs:
                decoName = unico2decoPath(unicode(name), deco2unicoMap)
                os.rename(opjoin(root, name), opjoin(root, decoName))
            for name in files:
                decoName = unico2decoPath(unicode(name), deco2unicoMap)
                os.rename(opjoin(root, name), opjoin(root, decoName))

    return destDir

def removeZipFileInDestDir(destDir, zipFileNames):
    for name in zipFileNames:
        try:
            os.remove(opjoin(destDir, unidecode(unicode(name))))
        except OSError:
            pass

def preProcess():
    deco2unicoMap = {'':''}
    doNotCopy = gArgs.run_only
    zipFileNames, unzipDirNames = unzipInAssignDir(gArgs.assignment_dir)
    destDir = copyAndDecodeAssignDirToOutDirRecursive(gArgs.assignment_dir, gArgs.output_dir, gArgs.assignment_alias, deco2unicoMap, doNotCopy)
    removeZipFileInDestDir(destDir, zipFileNames)

    return destDir, deco2unicoMap, unzipDirNames

def postProcess(unzipDirNames):
    removeUnzipDirsInAssignDir(gArgs.assignment_dir, unzipDirNames)

############################################
# main functions

# return CMakeLists.txt code
def getCMakeListsFileContents(projName, srcFileNames):
    srcFileCount = 0
    code = ''
    code += 'cmake_minimum_required(VERSION 2.6)\n'
    code += 'project(%s)\n'%projName
    code += 'add_executable(%s.exe '%projName
    for fileName in srcFileNames:
        ext = os.path.splitext(fileName)[1].lower()
        if ext=='.c' or ext=='.cpp':
            code += '%s '%fileName
            srcFileCount += 1
    code += ')\n'
    return code

# return errorCode, buildLog
def build(extension, srcRootDir, projName, srcFileNames):

    if extension in gCodeExt:
        return gCodeExt[extension]['build-func'](srcRootDir, projName, srcFileNames)
    else:
        errorMsg = '%s is not a supported source file type.'%extension
        print '%s%s'%(gLogPrefix, errorMsg)
        return -1, errorMsg 

def onTimeOut(proc):
    proc.kill()

# def kill_windows(proc):
    # # http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
    # subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=proc.pid))

# return exitType, output(stdout) of target program
# exitType:
#   0 - normal exit
#   1 - forced kill due to timeout
#   2 - cannot find the executable file (not built yet)
def run(extension, srcRootDir, projName, userInput, timeOut):
    try:
        proc = subprocess.Popen([gCodeExt[extension]['runcmd-func'](srcRootDir, projName)], \
                cwd=gCodeExt[extension]['runcwd-func'](srcRootDir, projName), stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    except OSError:
        return 2, gCodeExt[extension]['runcmd-func'](srcRootDir, projName)

    timer = threading.Timer(timeOut, onTimeOut, [proc])
    timer.start()
    stdoutStr, stderrStr = proc.communicate(userInput)

    if timer.is_alive():
        timer.cancel()
        return 0, stdoutStr
    else:
        return 1, stdoutStr

############################################
# functions for report
def generateReport(args, submittedFileNames, srcFileLists, buildRetCodes, buildLogs, exitTypeLists, stdoutStrLists, userInputLists):
    htmlCode = ''

    # header
    htmlCode += '''<html>
<head>
<title>Assignment %s Report</title>
<style type="text/css">
%s
</style>
</head>
<body>'''%(args.assignment_alias, HtmlFormatter().get_style_defs())

    # beginning
    htmlCode += '''<pre>
    Assignment %s Report

    Assignment directory: %s
    Output directory: %s
    User input: %s
    User dict: %s
    Timeout: %f
    Run only: %d
</pre>'''%(args.assignment_alias, os.path.abspath(args.assignment_dir), opjoin(os.path.abspath(args.output_dir), unidecode(unicode(args.assignment_alias))), 
        args.user_input, args.user_dict, args.timeout, args.run_only)

    # main table
    htmlCode += '''<table border=1>
<tr>
<td>Submission Name</td>
<td>Source File Path in Assignment Directory</td>
<td>Output</td>
<td>Score</td>
<td>Comment</td>
</tr>'''

    for i in range(len(submittedFileNames)):
        htmlCode += '<tr>\n'
        htmlCode += '<td>%s</td>\n'%submittedFileNames[i]
        htmlCode += '<td>%s</td>\n'%getSourcesTable(srcFileLists[i])
        htmlCode += '<td>%s</td>\n'%getOutput(buildRetCodes[i], buildLogs[i], userInputLists[i], exitTypeLists[i], stdoutStrLists[i])
        htmlCode += '<td>%s</td>\n'%''
        htmlCode += '<td>%s</td>\n'%''
        htmlCode += '</tr>\n'

    htmlCode += '</table>\n'

    # footer
    htmlCode += '''</body>
</html>'''

    # write html
    with open(getReportFilePath(args), 'w') as f:
        f.write(htmlCode.encode('utf-8'))
        
def getReportFilePath(args):
    return opjoin(opjoin(args.output_dir, unidecode(unicode(args.assignment_alias))),'report-%s.html'%args.assignment_alias)

def getSourcesTable(srcPaths):
    htmlCode = ''
    for srcPath in srcPaths:
        htmlCode += '%s\n'%srcPath.replace(gArgs.assignment_dir, '')
        htmlCode += '%s\n'%getRenderedSource(srcPath)
    return htmlCode 

def getRenderedSource(srcPath):
    try:
        with open(srcPath, 'r') as f:
            sourceCode = f.read()
            sourceCode = unicode(sourceCode, gArgs.source_encoding)
        return highlight(sourceCode, guess_lexer_for_filename(srcPath, sourceCode), HtmlFormatter())
    except UnicodeDecodeError as e:
        return '<p></p>'+format(e)

def getOutput(buildRetCode, buildLog, userInputList, exitTypeList, stdoutStrList):
    s = '<pre>\n'
    if buildRetCode!=0: # build error
        s += buildLog
    else:
        for i in range(len(userInputList)):
            userInput = userInputList[i]
            exitType = exitTypeList[i]
            stdoutStr = stdoutStrList[i]
            s += '(user input: %s)\n'%userInput
            if exitType == 0:
                try:
                    s += unicode(stdoutStr, gArgs.source_encoding)
                except UnicodeDecodeError as e:
                    s += format(e)
            elif exitType == 1:   # time out
                s += 'Timeout'
            elif exitType == 2:   # no executable exists
                s += 'Cannot find %s\n(Maybe not built yet)'%os.path.basename(stdoutStr)
            s += '\n'
    return s
 
############################################
# functions for each source file extension

# return errorCode, buildLog
def build_c_cpp(srcRootDir, projName, srcFileNames):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    os.makedirs(buildDir)

    # make CMakeLists.txt
    cmakeCode = getCMakeListsFileContents(projName, ['../'+name for name in srcFileNames])
    with open(opjoin(buildDir,'CMakeLists.txt'), 'w') as f:
        f.write(cmakeCode)

    # build
    try:
        buildLog = subprocess.check_output('cd %s && %s'%(buildDir, gBuildCmd), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output
    else:
        return 0, buildLog

def runcmd_c_cpp(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    return os.path.abspath(opjoin(buildDir, '%s.exe'%projName))

def runcwd_c_cpp(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    return buildDir


############################################
# pre-defined

env = {'nt':{}, 'posix':{}}

env['nt']['build-cmd'] = 'vcvars32.bat && cmake ./ -G "NMake Makefiles" && nmake'
env['posix']['build-cmd'] = 'cmake ./; make'

gBuildCmd = env[os.name]['build-cmd']

gCodeExt = {'.c':{}, '.cpp':{}}

gCodeExt['.c']['build-func'] = build_c_cpp
gCodeExt['.c']['runcmd-func'] = runcmd_c_cpp
gCodeExt['.c']['runcwd-func'] = runcwd_c_cpp

gCodeExt['.cpp']['build-func'] = build_c_cpp
gCodeExt['.cpp']['runcmd-func'] = runcmd_c_cpp
gCodeExt['.cpp']['runcwd-func'] = runcwd_c_cpp

opjoin = os.path.join
gLogPrefix = '# '
gBuildDirPrefix = 'pacers-build-'

############################################
# main routine

parser = argparse.ArgumentParser(prog='pacers.py', description='Programming Assignments Compiling, Executing, and Reporting system', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('assignment_dir',
                    help='''A direcory that has submitted files.
In assignment_dir, one source file runs one program. 
Each submission might have only one source file or a 
zip file or a directory including multiple source files''')
parser.add_argument('--user-input', nargs='+', default=[''],
                    help='''Specify USER_INPUT to be sent to the stdin of target
programs. This option should be located after
assignment_dir if no other optional arguments are
given. Two types of user input are available.
default is an empty string.

| Type     | Example                  | Example's meaning                          |
|----------|--------------------------|--------------------------------------------|
| Single   | --user-input 15          | run each source file with input 15         |
| value    | --user-input "hello"     | run each source file with input "hello"    |
|          | --user-input "1 2"       | run each source file with input "1 2"      |
|----------|--------------------------|--------------------------------------------|
| Multiple | --user-input 1 2 3       | run each source 3 times: with 1, 2, 3      |
| values   | --user-input "1 2" "3 4" | run each source 2 times: with "1 2", "3 4" |

''')
parser.add_argument('--user-dict', default=None,
                    help='''Specify USER_DICT to be sent to the stdin of target
programs. Argument should be python dictionary 
representation. Each 'key' of the dictionary item
is 'suffix' that should match with the last parts of 
each source file name. 'value' is user input for 
those matched source files.
If both --user-input and --user-dict are specified,
only --user-dict is used.

Example:
--user-dict {'1':['1','2'], '2':['2,'5','7']}

runs a source file whose name ends with '1'   
(e.g. prob1.c) 2 times (with '10', '20')     
and run a source file whose name ends with   
'2' (e.g. prob2.c) 3 times (with '2','5','7').

''')
# parser.add_argument('--file-layout', default=0, type=int,
                    # help='''indicates file layout in the assignment_dir. \ndefault: 0
# 0 - one source file runs one program. 
# each submission might have only one source file or a 
# zip file or a directory including multiple source files.''')
parser.add_argument('--timeout', default=2., type=float,
                    help='''Each target program is killed when TIMEOUT(seconds)
is reached. Useful for infinite loop cases.
default: 2.0''')
parser.add_argument('--run-only', action='store_true',
                    help='''When specified, run each target program without build.
You may use it when you want change USER_INPUT without
build. if the programming language of source files 
does not require build process, PACERs 
automatically skips the build process without 
specifying this option.''')
parser.add_argument('--assignment-alias',
                    help='''Specify ASSIGNMENT_ALIAS for each assignment_dir. 
ASSIGNMENT_ALIAS is used when making a sub-directory 
in OUTPUT_DIR and the final report file. 
default: "basename" of assignment_dir (bar if 
assignment_dir is /foo/bar/).''')
parser.add_argument('--output-dir', default=opjoin('.', 'output'),
                    help='''Specify OUTPUT_DIR in which the final report file 
and build output files to be generated. 
Avoid including hangul characters in its full path.
default: %s'''%opjoin('.', 'output'))
parser.add_argument('--source-encoding', default=sys.getdefaultencoding(),
                    help='''Specify SOURCE_ENCODING in which source files 
are encoded. You don't need to use this option if
source code only has english characters or 
the platform where source code is written and 
the platform PACERs is running is same. 
If source files are written in another platform,
you might need to specify default encoding for 
the platform to run PACERs correctly. 
default: system default encoding''')

gArgs = parser.parse_args()

# print gArgs
# exit()

if not gArgs.assignment_alias:
    gArgs.assignment_alias = os.path.basename(os.path.abspath(gArgs.assignment_dir))

submittedFileNames = []
srcFileLists = []
buildRetCodes = []
buildLogs = []
exitTypeLists = []
stdoutStrLists = []
userInputLists = []

############################################
# main routine

destDir, deco2unicoMap, unzipDirNames = preProcess()

# preprocess --user-dict
if gArgs.user_dict!=None:
    gArgs.user_dict = eval(gArgs.user_dict)

submissionNames = [name for name in os.listdir(destDir) if gBuildDirPrefix not in name]
for i in range(len(submissionNames)):
    submissionName = submissionNames[i]

    print
    print '%s'%gLogPrefix
    print '%sSubmission %d / %d: %s'%(gLogPrefix, i+1, len(submissionNames), submissionName)

    if True:    # no project file exists
        if os.path.isdir(opjoin(destDir, submissionName)):
            # test-assignment-3
            #   student01
            #       prob1.c
            #       prob2.c
            #   student02
            #       prob1.c
            #       prob2.c
            submissionDir = opjoin(destDir, submissionName)
            srcFileNames = [name for name in os.listdir(submissionDir) if gBuildDirPrefix not in name]
        else:
            # test-assignment-1
            #   student01.c
            #   student02.c
            #   student03.c
            submissionDir = destDir
            srcFileNames = [submissionName]

        for i in range(len(srcFileNames)):
            srcFileName = srcFileNames[i]
            projName, ext = os.path.splitext(srcFileName)
            ext = ext.lower()

            print '%s'%gLogPrefix
            print '%sProject %d / %d: %s'%(gLogPrefix, i+1, len(srcFileNames), projName)

            # build
            if not gArgs.run_only:
                print '%sBuilding...'%gLogPrefix
                buildRetCode, buildLog = build(ext, submissionDir, projName, [srcFileName])

            else:
                buildRetCode = 0
                buildLog = ''

            # set userInputs
            if gArgs.user_dict!=None:
                userInputs = None
                for key in gArgs.user_dict:
                    if projName.endswith(key):
                        userInputs = gArgs.user_dict[key] 
                        break
                if userInputs == None:
                    userInputs = []
                    for key in gArgs.user_dict:
                        userInputs.extend(gArgs.user_dict[key])
            else:
                userInputs = gArgs.user_input

            # run
            exitTypeList = []
            stdoutStrList = []
            userInputList = userInputs
            if buildRetCode!=0:
                print '%sBuild error. Go on a next file.'%gLogPrefix
            else:
                print '%sRunning...'%gLogPrefix
                for userInput in userInputs:
                    exitType, stdoutStr = run(ext, submissionDir, projName, userInput, gArgs.timeout)
                    exitTypeList.append(exitType)
                    stdoutStrList.append(stdoutStr)
                print '%sDone.'%gLogPrefix

            # add report data
            submittedFileNames.append(deco2unicoPath(submissionName, deco2unicoMap))

            # full path -> \hagsaeng01\munje2\munje2.c
            destSrcFilePath = opjoin(submissionDir, srcFileName)
            destSrcFilePathAfterDestDir = destSrcFilePath.replace(destDir, '')
            origSrcFilePathAfterAssignDir = deco2unicoPath(destSrcFilePathAfterDestDir, deco2unicoMap)
            srcFileLists.append([opjoin(gArgs.assignment_dir, origSrcFilePathAfterAssignDir)])

            buildRetCodes.append(buildRetCode)
            buildLogs.append(buildLog)
            exitTypeLists.append(exitTypeList)
            stdoutStrLists.append(stdoutStrList)
            userInputLists.append(userInputList)

print
print '%s'%gLogPrefix
print '%sGenerating Report for %s...'%(gLogPrefix, gArgs.assignment_alias)
generateReport(gArgs, submittedFileNames, \
                srcFileLists, buildRetCodes, buildLogs, exitTypeLists, stdoutStrLists, userInputLists)

postProcess(unzipDirNames)
print '%sDone.'%gLogPrefix
