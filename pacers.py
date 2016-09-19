#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
PACERs
    : Programming Assignments Compiling, Executing, and Reporting system

Please see https://github.com/yssl/PACERs for more information.

Requirements:
    python 2.x
    cmake
    Pygments
        : Install in Windows - "pip install pygments"
          Install in Linux - "sudo pip install pygments" or "sudo apt-get install python-pygments"
    Unidecode (install via pip install unidecode)
        : Install in Windows - "pip install unidecode"
          Install in Linux - "sudo pip install unidecode" or "sudo apt-get install python-unidecode"
    chardet
        : Install in Windows - "pip install chardet"
          Install in Linux - "sudo pip install chardet"

Required environment setting:
    On MS Windows, please add following paths to the system path. XX.X means your Visual Studio version.
        C:\Program Files (x86)\Microsoft Visual Studio XX.X\VC\bin
        C:\Program Files (x86)\Microsoft Visual Studio XX.X\Common7\IDE

Quick start:
    1) Run: git clone https://github.com/yssl/PACERs.git

    2) On Linux, run: ./pacers.py test-assignments/c-assignment-1
       On Windows, run: pacers.py test-assignments\c-assignment-1

    3) Open ./output/c-assignment-1/report-c-assignment-1.html in any web browser
    The generated html file is written in unicode (utf-8), so if your browser shows broken characters
    please try to change the text encoding option for the page to unicode or utf-8.
    
usage: pacers.py [-h] [--user-input USER_INPUT [USER_INPUT ...]]
                 [--user-dict USER_DICT] [--timeout TIMEOUT] [--run-only]
                 [--build-only] [--assignment-alias ASSIGNMENT_ALIAS]
                 [--output-dir OUTPUT_DIR]
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
  --build-only          When specified, build each target program without running.
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
'''

import os, sys, shutil, subprocess, threading, time, argparse, zipfile, fnmatch, glob, re
import pygments
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter
from unidecode import unidecode
import chardet

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
# functions for unzipping
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
    return unzipDirNames

def removeUnzipDirsInAssignDir(assignDir, unzipDirNames):
    for d in unzipDirNames:
        shutil.rmtree(d)

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
    Build only: %d
</pre>'''%(args.assignment_alias, os.path.abspath(args.assignment_dir), opjoin(os.path.abspath(args.output_dir), unidecode(unicode(args.assignment_alias))), 
        args.user_input, args.user_dict, args.timeout, args.run_only, args.build_only)

    # main table
    htmlCode += '''<table border=1>
<tr>
<td>Submission Title</td>
<td>Source Files (Relative path from Assignment directory)</td>
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
    with open(srcPath, 'r') as f:
        sourceCode = f.read()
        success, unistr = getUnicodeStr(sourceCode)
        if success:
            try:
                lexer = guess_lexer_for_filename(srcPath, unistr)
            except pygments.util.ClassNotFound as e:
                return '<p></p>'+'<pre>'+format(e)+'</pre>'
            return highlight(unistr, lexer, HtmlFormatter())
        else:
            return '<p></p>'+'<pre>'+unistr+'</pre>'

def getOutput(buildRetCode, buildLog, userInputList, exitTypeList, stdoutStrList):
    s = '<pre>\n'
    if buildRetCode!=0: # build error
        s += buildLog
    else:
        for i in range(len(userInputList)):
            userInput = userInputList[i]
            exitType = exitTypeList[i]
            stdoutStr = stdoutStrList[i]
            if exitType == 0:
                s += '(user input: %s)\n'%userInput
                success, unistr = getUnicodeStr(stdoutStr)
                s += unistr
            elif exitType == 1:   # time out
                s += '(user input: %s)\n'%userInput
                s += 'Timeout'
            elif exitType == 2:   # no executable exists
                s += 'Cannot find %s\n(May not be built yet)'%os.path.basename(stdoutStr)
            elif exitType == 3:   # from runcmd_single_dummy()
                pass
            s += '\n'
    return s
 
def getUnicodeStr(str):
    encodingStrs = ['utf-8', sys.getfilesystemencoding(), '(chardet)']
    detected = chardet.detect(str)
    success = True

    for encodingStr in encodingStrs:
        if encodingStr=='(chardet)':
            encoding = detected['encoding']
        else:
            encoding = encodingStr

        try:
            retstr = unicode(str, encoding)
            success = True
            break
        except UnicodeDecodeError as e:
            retstr = format(e)+'\n(chardet detects %s with the confidence level of %f)'%(detected['encoding'], detected['confidence'])
            success = False

    return success, retstr
        
############################################
# build functions
# return errorCode, buildLog

####
# build_single functions
def build_single_source(srcRootDir, projName, srcFileName):
    extension = os.path.splitext(srcFileName)[1].lower()
    if extension in gSourceExt:
        return gSourceExt[extension]['build-single-source-func'](srcRootDir, projName, srcFileName)
    else:
        return build_single_else(extension)

def build_single_c_cpp(srcRootDir, projName, srcFileName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    os.makedirs(buildDir)

    makeCMakeLists_single_c_cpp(projName, srcFileName, buildDir)

    return __build_cmake(buildDir, './')

def build_single_dummy(srcRootDir, projName, srcFileNames):
    return 0, ''

def build_single_else(extension):
    errorMsg = 'Building %s is not supported.'%extension
    print '%s%s'%(gLogPrefix, errorMsg)
    return -1, errorMsg 

####
# build_cmake functions
def build_cmake(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    os.makedirs(buildDir)
    return __build_cmake(buildDir, '../')

def __build_cmake(buildDir, cmakeLocationFromBuildDir):
    try:
        buildLog = subprocess.check_output('cd %s && %s'%(buildDir, gOSEnv[os.name]['cmake-cmd'](cmakeLocationFromBuildDir)), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output
    else:
        return 0, buildLog

# return CMakeLists.txt code
def makeCMakeLists_single_c_cpp(projName, srcFileName, buildDir):
    code = ''
    code += 'cmake_minimum_required(VERSION 2.6)\n'
    code += 'project(%s)\n'%projName
    code += 'add_executable(%s '%projName
    code += '../%s'%srcFileName
    code += ')\n'

    with open(opjoin(buildDir,'CMakeLists.txt'), 'w') as f:
        f.write(code)

####
# build_vcxproj functions
def build_vcxproj(srcRootDir, projName):
    # do not need to make buildDir. msbuild.exe automatically makes the outdir.
    # buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    # os.makedirs(buildDir)
    
    vcxprojNames = glob.glob(opjoin(srcRootDir, '*.vcxproj'))
    vcxprojNames.extend(glob.glob(opjoin(srcRootDir, '*.vcxproj')))
    if len(vcxprojNames)==0:
        errorMsg = 'Cannot find .vcxproj or .vcproj file.'
        print '%s%s'%(gLogPrefix, errorMsg)
        return -1, errorMsg 

    try:
        buildLog = subprocess.check_output('vcvars32.bat && msbuild.exe %s /property:OutDir=%s'
                %(vcxprojNames[0], gBuildDirPrefix+projName), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output
    else:
        return 0, buildLog

############################################
# run functions

# return exitType, output(stdout) of target program
# exitType:
#   0 - normal exit
#   1 - forced kill due to timeout
#   2 - cannot find the executable file (not built yet)
#   3 - from runcmd_single_dummy() 

def run_single_source(srcRootDir, projName, srcFileName, userInput, timeOut):
    extension = os.path.splitext(srcFileName)[1].lower()
    if extension in gSourceExt:
        runcmd = gSourceExt[extension]['runcmd-single-source-func'](srcRootDir, projName)
        runcwd = gSourceExt[extension]['runcwd-single-source-func'](srcRootDir, projName)
        return __run(runcmd, runcwd, userInput, timeOut)
    else:
        return run_single_else(extension)

def run_single_else(extension):
    errorMsg = 'Running %s is not supported.'%extension
    print '%s%s'%(gLogPrefix, errorMsg)
    return 0, errorMsg 

def run_cmake(srcRootDir, projName, userInput, timeOut):
    runcmd = runcmd_cmake(srcRootDir, projName)
    runcwd = runcwd_single_c_cpp(srcRootDir, projName)
    return __run(runcmd, runcwd, userInput, timeOut)

def run_vcxproj(srcRootDir, projName, userInput, timeOut):
    runcmd = runcmd_vcxproj(srcRootDir, projName)
    print runcmd
    runcwd = runcwd_single_c_cpp(srcRootDir, projName)
    return __run(runcmd, runcwd, userInput, timeOut)

def __run(runcmd, runcwd, userInput, timeOut):
    if runcmd == '':
        return 3, ''

    try:
        proc = subprocess.Popen([runcmd], cwd=runcwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    except OSError:
        return 2, runcmd

    timer = threading.Timer(timeOut, onTimeOut, [proc])
    timer.start()
    stdoutStr, stderrStr = proc.communicate(userInput)

    if timer.is_alive():
        timer.cancel()
        return 0, stdoutStr
    else:
        return 1, stdoutStr


def runcmd_single_c_cpp(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    return os.path.abspath(opjoin(buildDir, '%s'%projName))

def runcwd_single_c_cpp(srcRootDir, projName):
    # run output executable from srcRootDir
    return srcRootDir

    # run output executable from buildDir
    # buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    # return buildDir

def runcmd_cmake(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    execName = projName
    with open(opjoin(srcRootDir,'CMakeLists.txt'), 'r') as f:
        tokens = re.split(' |\n|\(|\)', f.read())
        for i in range(len(tokens)):
            if tokens[i].lower()=='add_executable' and i < len(tokens)-1:
                execName = tokens[i+1]
    return os.path.abspath(opjoin(buildDir, execName))

def runcmd_vcxproj(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    vcxprojNames = glob.glob(opjoin(srcRootDir, '*.vcxproj'))
    vcxprojNames.extend(glob.glob(opjoin(srcRootDir, '*.vcxproj')))
    execName = os.path.splitext(os.path.basename(vcxprojNames[0]))[0]
    return os.path.abspath(opjoin(buildDir, execName))

def runcmd_single_dummy(srcRootDir, projName):
    return ''
def runcwd_single_dummy(srcRootDir, projName):
    return ''


def onTimeOut(proc):
    proc.kill()

# def kill_windows(proc):
    # # http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
    # subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=proc.pid))


############################################
# project type detection

def detectSubmissionType(submissionPath):
    if os.path.isdir(opjoin(gArgs.assignment_dir, submissionTitle)):
        # print 'dir'
        for submissionType in range(BEGIN_SUBMISSION_TYPE+1, END_SUBMISSION_TYPE):
            for pattern in gSubmissionPatterns[submissionType]:
                if len(glob.glob(opjoin(submissionPath, pattern))) > 0:
                    return submissionType
        return SOURCE_FILES
    else:
        # print 'file'
        return SINGLE_SOURCE_FILE

def decodeDestDirPathRecursive(destDir, deco2unicoMap):
    for root, dirs, files in os.walk(destDir, topdown=False):
        for name in dirs:
            decoName = unico2decoPath(unicode(name), deco2unicoMap)
            os.rename(opjoin(root, name), opjoin(root, decoName))
        for name in files:
            decoName = unico2decoPath(unicode(name), deco2unicoMap)
            os.rename(opjoin(root, name), opjoin(root, decoName))

def getUserInputsFromUserDict(userDict, projName):
    userInputs = None
    for key in userDict:
        if projName.endswith(key):
            userInputs = userDict[key] 
            break
    if userInputs == None:
        userInputs = []
        for key in userDict:
            userInputs.extend(userDict[key])
    return userInputs

if __name__=='__main__':
    ############################################
    # pre-defined

    opjoin = os.path.join
    gLogPrefix = '# '
    gBuildDirPrefix = 'pacers-build-'

    gOSEnv = {'nt':{}, 'posix':{}}
    gOSEnv['nt']['cmake-cmd'] = lambda cmakeLocationFromBuildDir: 'vcvars32.bat && cmake %s -G "NMake Makefiles" && nmake'%cmakeLocationFromBuildDir
    gOSEnv['posix']['cmake-cmd'] = lambda cmakeLocationFromBuildDir: 'cmake %s && make'%cmakeLocationFromBuildDir

    gSourceExt = {'.c':{}, '.cpp':{}, '.txt':{}}

    gSourceExt['.c']['build-single-source-func'] = build_single_c_cpp
    gSourceExt['.c']['runcmd-single-source-func'] = runcmd_single_c_cpp
    gSourceExt['.c']['runcwd-single-source-func'] = runcwd_single_c_cpp

    gSourceExt['.cpp']['build-single-source-func'] = build_single_c_cpp
    gSourceExt['.cpp']['runcmd-single-source-func'] = runcmd_single_c_cpp
    gSourceExt['.cpp']['runcwd-single-source-func'] = runcwd_single_c_cpp

    gSourceExt['.txt']['build-single-source-func'] = build_single_dummy
    gSourceExt['.txt']['runcmd-single-source-func'] = runcmd_single_dummy
    gSourceExt['.txt']['runcwd-single-source-func'] = runcwd_single_dummy

    # submission type
    BEGIN_SUBMISSION_TYPE = 0
    CMAKE_PROJECT         = 1
    VISUAL_CPP_PROJECT    = 2
    SOURCE_FILES          = 3
    SINGLE_SOURCE_FILE    = 4
    END_SUBMISSION_TYPE   = 5

    gSubmissionDescrption                        = {}
    gSubmissionDescrption[CMAKE_PROJECT]         = 'CMAKE_PROJECT - the submission has CMakeLists.txt.'
    gSubmissionDescrption[VISUAL_CPP_PROJECT] = 'VISUAL_CPP_PROJECT - the submission has .vcxproj or .vcproj.'
    gSubmissionDescrption[SOURCE_FILES]          = 'SOURCE_FILES - the submission has source or resource files without any project files.'
    gSubmissionDescrption[SINGLE_SOURCE_FILE]    = 'SINGLE_SOURCE_FILE - the submission has a single source or resource file.'

    gSubmissionPatterns                        = {}
    gSubmissionPatterns[CMAKE_PROJECT]         = ['CMakeLists.txt']
    gSubmissionPatterns[VISUAL_CPP_PROJECT]    = ['*.vcxproj', '*.vcproj']
    gSubmissionPatterns[SOURCE_FILES]          = ['*']
    gSubmissionPatterns[SINGLE_SOURCE_FILE]    = ['*']


    ############################################
    # argparse

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
    parser.add_argument('--build-only', action='store_true',
                        help='''When specified, build each target program without running.''')
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

    gArgs = parser.parse_args()

    # print gArgs
    # exit()

    if not gArgs.assignment_alias:
        gArgs.assignment_alias = os.path.basename(os.path.abspath(gArgs.assignment_dir))

    ############################################
    # main routine

    submittedFileNames = []
    srcFileLists = []
    buildRetCodes = []
    buildLogs = []
    exitTypeLists = []
    stdoutStrLists = []
    userInputLists = []

    # preprocess --user-dict
    if gArgs.user_dict!=None:
        gArgs.user_dict = eval(gArgs.user_dict)

    # check assignment_dir
    if not os.path.isdir(gArgs.assignment_dir):  
        print 'PACERs: Unable to access \'%s\'. Please check the assignment_dir again.'%gArgs.assignment_dir
        exit()

    # unzip in .zip files in assignment_dir
    unzipDirNames = unzipInAssignDir(gArgs.assignment_dir)

    # copy assignment_dir to destDir(output_dir/assignment_alias)
    deco2unicoMap = {'':''}
    decodeAlias = unico2decoPath(unicode(gArgs.assignment_alias), deco2unicoMap)
    destDir = opjoin(gArgs.output_dir, decodeAlias)

    if not gArgs.run_only:
        print '%s'%gLogPrefix
        print '%sCopying all submissions from \'%s\' to \'%s\'...'%(gLogPrefix, gArgs.assignment_dir, destDir)
        # delete exsting one
        if os.path.exists(destDir):
            shutil.rmtree(destDir)
            time.sleep(.01)
        # copy tree
        shutil.copytree(gArgs.assignment_dir, destDir)
    else:
        # delete report file only
        try:
            os.remove(getReportFilePath(gArgs))
        except OSError:
            pass

    # get submission titles
    submissionTitles = [name for name in os.listdir(gArgs.assignment_dir) if os.path.splitext(name)[1].lower()!='.zip']

    # process each submission
    for i in range(len(submissionTitles)):
        submissionTitle = submissionTitles[i]
        print
        print '%s'%gLogPrefix
        print '%sSubmission %d / %d: %s'%(gLogPrefix, i+1, len(submissionTitles), submissionTitle)

        submissionType = detectSubmissionType(opjoin(gArgs.assignment_dir, submissionTitle))
        print '%sSubmission type: %s'%(gLogPrefix, gSubmissionDescrption[submissionType])


        # set submissionDir, projNames, projSrcFileNames for each project
        # ex)
        # projNames : ['proj1', 'proj2']
        # projSrcFileNames: [['proj1.c','proj1.h'], ['proj2.c','proj2.h']]
        if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
            decodeDestDirPathRecursive(destDir, deco2unicoMap)

            if submissionType==SINGLE_SOURCE_FILE:
                submissionDir = destDir
                projSrcFileNames = [[unico2decoPath(unicode(submissionTitle), deco2unicoMap)]]

            elif submissionType==SOURCE_FILES:
                submissionDir = opjoin(destDir, unico2decoPath(unicode(submissionTitle), deco2unicoMap))
                projSrcFileNames = [[fileName] for fileName in os.listdir(submissionDir) if gBuildDirPrefix not in name]

            projNames = [os.path.splitext(srcFileNamesInProj[0])[0] for srcFileNamesInProj in projSrcFileNames]

        elif submissionType==CMAKE_PROJECT or submissionType==VISUAL_CPP_PROJECT:
            # cmake does not allow hangul characters in source file paths,
            # and visual cpp allow hangul chracters in source file paths,
            # so both do not need unidecoding file paths.
            submissionDir = opjoin(destDir, submissionTitle)
            projNames = [submissionTitle]

            projSrcFileNames = [[]]
            for root, dirs, files in os.walk(submissionDir):
                if gBuildDirPrefix not in root:
                    for name in files:
                        projSrcFileNames[0].append(opjoin(root, name).replace(submissionDir+os.sep, ''))

        else:
            print '%sSubmission type %s is not supported.'%(gLogPrefix, gSubmissionDescrption[submissionType])
            continue

        # build & run each project in one submission
        for i in range(len(projNames)):
            print '%s'%gLogPrefix
            print '%sProject %d / %d: %s'%(gLogPrefix, i+1, len(projNames), projNames[i])

            # build
            if not gArgs.run_only:
                print '%sBuilding...'%gLogPrefix

                if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
                    buildRetCode, buildLog = build_single_source(submissionDir, projNames[i], projSrcFileNames[i][0])
                elif submissionType==CMAKE_PROJECT:
                    buildRetCode, buildLog = build_cmake(submissionDir, projNames[i])
                elif submissionType==VISUAL_CPP_PROJECT:
                    buildRetCode, buildLog = build_vcxproj(submissionDir, projNames[i])

            else:
                buildRetCode = 0
                buildLog = ''

            # set userInputs
            if gArgs.user_dict!=None:
                userInputs = getUserInputsFromUserDict(gArgs.user_dict, projNames[i])
            else:
                userInputs = gArgs.user_input

            # run
            if not gArgs.build_only:
                exitTypeList = []
                stdoutStrList = []
                userInputList = userInputs
                if buildRetCode!=0:
                    print '%sBuild error. Go on to the next file.'%gLogPrefix
                else:
                    print '%sRunning...'%gLogPrefix
                    for userInput in userInputs:

                        if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
                            exitType, stdoutStr = run_single_source(submissionDir, projNames[i], projSrcFileNames[i][0], userInput, gArgs.timeout)
                        elif submissionType==CMAKE_PROJECT:
                            exitType, stdoutStr = run_cmake(submissionDir, projNames[i], userInput, gArgs.timeout)
                        elif submissionType==VISUAL_CPP_PROJECT:
                            exitType, stdoutStr = run_vcxproj(submissionDir, projNames[i], userInput, gArgs.timeout)

                        exitTypeList.append(exitType)
                        stdoutStrList.append(stdoutStr)
                    print '%sDone.'%gLogPrefix
            else:
                exitTypeList = [3]
                stdoutStrList = ['']
                userInputList = ['']

            # add report data
            submittedFileNames.append(submissionTitle)

            # full path -> \hagsaeng01\munje2\munje2.c
            projOrigSrcFilePathsAfterAssignDir = []
            for srcFileName in projSrcFileNames[i]:
                destSrcFilePath = opjoin(submissionDir, srcFileName)
                destSrcFilePathAfterDestDir = destSrcFilePath.replace(destDir+os.sep, '')
                if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
                    origSrcFilePathAfterAssignDir = deco2unicoPath(destSrcFilePathAfterDestDir, deco2unicoMap)
                else:
                    origSrcFilePathAfterAssignDir = destSrcFilePathAfterDestDir
                projOrigSrcFilePathsAfterAssignDir.append(opjoin(gArgs.assignment_dir, origSrcFilePathAfterAssignDir))

            srcFileLists.append(projOrigSrcFilePathsAfterAssignDir)
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

    removeUnzipDirsInAssignDir(gArgs.assignment_dir, unzipDirNames)
    print '%sDone.'%gLogPrefix


