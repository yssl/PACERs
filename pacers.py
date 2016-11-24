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
                 [--timeout TIMEOUT] [--run-only] [--build-only]
                 [--run-serial] [--build-serial] [--run-only-serial]
                 [--num-cores NUM_CORES] [--no-report]
                 [--exclude-patterns EXCLUDE_PATTERNS [EXCLUDE_PATTERNS ...]]
                 [--assignment-alias ASSIGNMENT_ALIAS]
                 [--output-dir OUTPUT_DIR]
                 assignment_dir

Programming Assignments Compiling, Executing, and Reporting system

positional arguments:
  assignment_dir        A direcory that has submissions.
                        The type of each submission is auto-detected by PACERs.

                        | Submission types   | Meaning                                              |
                        |--------------------|------------------------------------------------------|
                        | SINGLE_SOURCE_FILE | The submission has a single source or resource file. |
                        | SOURCE_FILES       | The submission has source or resource files without any project files.|
                        | CMAKE_PROJECT      | The submission has CMakeLists.txt.                   |
                        | VISUAL_CPP_PROJECT | The submission has *.vcxproj or *.vcproj.            |

                        Each submission can have only one source file, or a zip file
                        or a directory including many files.

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

  --timeout TIMEOUT     Each target program is killed when TIMEOUT(seconds)
                        is reached. Useful for infinite loop cases.
                        Setting zero seconds(--timeout 0) means unlimited execution time
                        for each target program, which can be useful for GUI applications.
                        default: 2.0
  --run-only            When specified, run each target program without build.
                        You may use it when you want change USER_INPUT without
                        build. if the programming language of source files
                        does not require build process, PACERs
                        automatically skips the build process without
                        specifying this option.
  --build-only          When specified, build each target program without running.
  --run-serial          When specified, run each target program in serial.
                        PACERs runs programs in parallel by default.
  --build-serial        When specified, build each target program in serial.
                        PACERs builds programs in parallel by default.
  --run-only-serial     Shortcut for --run-only --run-serial.
  --num-cores NUM_CORES
                        Specify number of cpu cores used in building and running process.
                        default: number of cpu cores in your machine.
  --no-report           When specified, the final report is not generated.
  --exclude-patterns EXCLUDE_PATTERNS [EXCLUDE_PATTERNS ...]
                        Files containing EXCLUDE_PATTERNS in their relative path
                        from each submission directory are excluded from the final report.
                        (Submission dir: 'student01' in 'test-assignments/c-assignment-4')
                        For example, use "--exclude-pattern *.txt foo/*"
                        to exclude all txt files and all files in foo directory
                        in each submission directory from the final report.
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
import multiprocessing as mp

if os.name=='nt':
    reload(sys)
    sys.setdefaultencoding('cp949')
elif os.name=='posix':
    reload(sys)
    sys.setdefaultencoding('utf-8')

############################################
# build functions
# return buildRetCode, buildLog
# buildRetCode:
#   -1 - build failed due to internal error, not because build error (not supported extension, etc)
#   0 - build succeeded
#   else - build failed due to build error

def buildProj(submissionType, submissionDir, projName, projSrcFileNames):
    if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
        buildRetCode, buildLog = build_single_source(submissionDir, projName, projSrcFileNames[0])
    elif submissionType==CMAKE_PROJECT:
        buildRetCode, buildLog = build_cmake(submissionDir, projName)
    elif submissionType==VISUAL_CPP_PROJECT:
        buildRetCode, buildLog = build_vcxproj(submissionDir, projName)
    return buildRetCode, buildLog

####
# build_single functions
def build_single_source(srcRootDir, projName, singleSrcFileName):
    extension = os.path.splitext(singleSrcFileName)[1].lower()
    if extension in gSourceExt:
        return gSourceExt[extension]['build-single-source-func'](srcRootDir, projName, singleSrcFileName)
    else:
        return build_single_else(extension)

def build_single_c_cpp(srcRootDir, projName, singleSrcFileName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    os.makedirs(buildDir)

    makeCMakeLists_single_c_cpp(projName, singleSrcFileName, buildDir)

    return __build_cmake(buildDir, './')

# def build_single_dummy(srcRootDir, projName, srcFileNames):
    # return 0, ''

def build_single_else(extension):
    errorMsg = 'Building %s is not supported.'%extension
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
def makeCMakeLists_single_c_cpp(projName, singleSrcFileName, buildDir):
    code = ''
    code += 'cmake_minimum_required(VERSION 2.6)\n'
    code += 'project(%s)\n'%projName
    code += 'add_executable(%s '%projName
    code += '../%s'%singleSrcFileName
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
    vcxprojNames.extend(glob.glob(opjoin(srcRootDir, '*.vcproj')))
    for i in range(len(vcxprojNames)-1, -1, -1):
        if os.path.isdir(vcxprojNames[i]):
            del vcxprojNames[i]

    if len(vcxprojNames)==0:
        errorMsg = 'Cannot find .vcxproj or .vcproj file.'
        return -1, errorMsg 

    try:
        # print 'vcvars32.bat && msbuild.exe "%s" /property:OutDir="%s/";IntDir="%s/"'\
                # %(vcxprojNames[0], gBuildDirPrefix+projName, gBuildDirPrefix+projName)
        buildLog = subprocess.check_output('vcvars32.bat && msbuild.exe "%s" /property:OutDir="%s/";IntDir="%s/"'
                %(vcxprojNames[0], gBuildDirPrefix+projName, gBuildDirPrefix+projName), stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output
    else:
        return 0, buildLog

############################################
# run functions

# return exitType, output(stdout) of target program
# exitType:
#   -1 - execution failed due to internal error (not supported extension, not built yet)
#   0 - normal exit
#   1 - forced kill due to timeout

def runProj(submissionType, submissionDir, projName, projSrcFileNames, userInputs, timeOut):
    exitTypeList = []
    stdoutStrList = []

    for userInput in userInputs:

        if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
            exitType, stdoutStr = run_single_source(submissionDir, projName, projSrcFileNames[0], userInput, timeOut)
        elif submissionType==CMAKE_PROJECT:
            exitType, stdoutStr = run_cmake(submissionDir, projName, userInput, timeOut)
        elif submissionType==VISUAL_CPP_PROJECT:
            exitType, stdoutStr = run_vcxproj(submissionDir, projName, userInput, timeOut)

        exitTypeList.append(exitType)
        stdoutStrList.append(stdoutStr)

    return exitTypeList, stdoutStrList

def run_single_source(srcRootDir, projName, singleSrcFileName, userInput, timeOut):
    extension = os.path.splitext(singleSrcFileName)[1].lower()
    if extension in gSourceExt:
        runcmd = gSourceExt[extension]['runcmd-single-source-func'](srcRootDir, projName)
        runcwd = gSourceExt[extension]['runcwd-single-source-func'](srcRootDir, projName)
        return __run(runcmd, runcwd, userInput, timeOut)
    else:
        return run_single_else(extension)

def run_single_else(extension):
    errorMsg = 'Running %s is not supported.'%extension
    return -1, errorMsg 

def run_cmake(srcRootDir, projName, userInput, timeOut):
    runcmd = runcmd_cmake(srcRootDir, projName)
    runcwd = runcwd_single_c_cpp(srcRootDir, projName)
    return __run(runcmd, runcwd, userInput, timeOut)

def run_vcxproj(srcRootDir, projName, userInput, timeOut):
    runcmd = runcmd_vcxproj(srcRootDir, projName)
    runcwd = runcwd_single_c_cpp(srcRootDir, projName)
    return __run(runcmd, runcwd, userInput, timeOut)

def __run(runcmd, runcwd, userInput, timeOut):
    # if runcmd == '':
        # return 3, ''

    try:
        proc = subprocess.Popen([runcmd], cwd=runcwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    except OSError:
        # return 2, runcmd
        return -1, 'Cannot find %s (May not be built yet).'%os.path.basename(runcmd)

    if timeOut != 0:
        # call onTimeOut() after timeOut seconds
        timer = threading.Timer(timeOut, onTimeOut, [proc])
        timer.start()

        # block until proc is finished
        stdoutStr, stderrStr = proc.communicate(userInput)

        if timer.is_alive():    # if proc has finished without calling onTimeOut()
            timer.cancel()
            return 0, stdoutStr
        else:
            return 1, stdoutStr # 1 means 'forced kill due to timeout'
    else:
        # block until proc is finished
        stdoutStr, stderrStr = proc.communicate(userInput)
        return 0, stdoutStr

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

# def runcmd_single_dummy(srcRootDir, projName):
    # return ''
# def runcwd_single_dummy(srcRootDir, projName):
    # return ''


def onTimeOut(proc):
    proc.kill()

# def kill_windows(proc):
    # # http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
    # subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=proc.pid))


############################################
# pre-defined

# submission type
BEGIN_SUBMISSION_TYPE = 0
CMAKE_PROJECT         = 1
VISUAL_CPP_PROJECT    = 2
SOURCE_FILES          = 3
SINGLE_SOURCE_FILE    = 4
END_SUBMISSION_TYPE   = 5

opjoin = os.path.join
gLogPrefix = '# '
gBuildDirPrefix = 'pacers-build-'

gOSEnv = {'nt':{}, 'posix':{}}
gOSEnv['nt']['cmake-cmd'] = lambda cmakeLocationFromBuildDir: 'vcvars32.bat && cmake %s -G "NMake Makefiles" && nmake'%cmakeLocationFromBuildDir
gOSEnv['posix']['cmake-cmd'] = lambda cmakeLocationFromBuildDir: 'cmake %s && make'%cmakeLocationFromBuildDir

# gSourceExt = {'.c':{}, '.cpp':{}, '.txt':{}}
gSourceExt = {'.c':{}, '.cpp':{}}

gSourceExt['.c']['build-single-source-func'] = build_single_c_cpp
gSourceExt['.c']['runcmd-single-source-func'] = runcmd_single_c_cpp
gSourceExt['.c']['runcwd-single-source-func'] = runcwd_single_c_cpp

gSourceExt['.cpp']['build-single-source-func'] = build_single_c_cpp
gSourceExt['.cpp']['runcmd-single-source-func'] = runcmd_single_c_cpp
gSourceExt['.cpp']['runcwd-single-source-func'] = runcwd_single_c_cpp

# gSourceExt['.txt']['build-single-source-func'] = build_single_dummy
# gSourceExt['.txt']['runcmd-single-source-func'] = runcmd_single_dummy
# gSourceExt['.txt']['runcwd-single-source-func'] = runcwd_single_dummy

gSubmissionTypeDescrption                        = {}
gSubmissionTypeDescrption[CMAKE_PROJECT]         = 'CMAKE_PROJECT - the submission has CMakeLists.txt.'
gSubmissionTypeDescrption[VISUAL_CPP_PROJECT]    = 'VISUAL_CPP_PROJECT - the submission has .vcxproj or .vcproj.'
gSubmissionTypeDescrption[SOURCE_FILES]          = 'SOURCE_FILES - the submission has source or resource files without any project files.'
gSubmissionTypeDescrption[SINGLE_SOURCE_FILE]    = 'SINGLE_SOURCE_FILE - the submission has a single source or resource file.'

gSubmissionTypeName                        = {}
gSubmissionTypeName[CMAKE_PROJECT]         = 'CMAKE_PROJECT'
gSubmissionTypeName[VISUAL_CPP_PROJECT]    = 'VISUAL_CPP_PROJECT'
gSubmissionTypeName[SOURCE_FILES]          = 'SOURCE_FILES'
gSubmissionTypeName[SINGLE_SOURCE_FILE]    = 'SINGLE_SOURCE_FILE'

gSubmissionPatterns                        = {}
gSubmissionPatterns[CMAKE_PROJECT]         = ['CMakeLists.txt']
gSubmissionPatterns[VISUAL_CPP_PROJECT]    = ['*.vcxproj', '*.vcproj']
gSubmissionPatterns[SOURCE_FILES]          = ['*']
gSubmissionPatterns[SINGLE_SOURCE_FILE]    = ['*']

############################################
# utility functions
def unico2decoPath(unicoPath, deco2unicoMap):
    unicoTokens = os.path.normpath(unicoPath).split(os.sep)

    decoTokens = []
    for unicoToken in unicoTokens:
        hasExt = '.' in unicoToken
        if hasExt:
            name, ext = os.path.splitext(unicoToken)
            unicoToken = name

        decoToken = unidecode(unicoToken)
        decoToken = decoToken.replace(' ', '_')
        decoToken = decoToken.replace('(', '_')
        decoToken = decoToken.replace(')', '_')
        if decoToken not in deco2unicoMap:
            deco2unicoMap[decoToken] = unicoToken

        if hasExt:
            decoToken += ext

        decoTokens.append(decoToken)

    decoPath = reduce(os.path.join, decoTokens)
    return decoPath

def deco2unicoPath(decoPath, deco2unicoMap):
    decoTokens = os.path.normpath(decoPath).split(os.sep)

    unicoTokens = []
    for decoToken in decoTokens:
        hasExt = '.' in decoToken
        if hasExt:
            name, ext = os.path.splitext(decoToken)
            decoToken = name

        unicoToken = deco2unicoMap[decoToken]

        if hasExt:
            unicoToken += ext

        unicoTokens.append(unicoToken)

    unicoPath = reduce(os.path.join, unicoTokens)
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
    renderedSrcPaths = []
    renderedSource = []
    failedMsgSrcPathMap = {}

    for srcPath in srcPaths:
        success, text = getRenderedSource(srcPath)
        if success:
            renderedSrcPaths.append(srcPath)
            renderedSource.append(text)
        else:
            if text not in failedMsgSrcPathMap:
                failedMsgSrcPathMap[text] = []
            failedMsgSrcPathMap[text].append(srcPath)

    htmlCode = ''

    # add rendered source file text
    for i in range(len(renderedSrcPaths)):
        htmlCode += '<b>%s</b>'%renderedSrcPaths[i].replace(gArgs.assignment_dir, '')
        htmlCode += '%s'%renderedSource[i]

    # add failed source file paths
    for errorMsg in failedMsgSrcPathMap:
        htmlCode += '<b>%s</b><br></br>'%errorMsg
        for failedSrcPath in failedMsgSrcPathMap[errorMsg]:
            htmlCode += '%s<br></br>'%failedSrcPath.replace(gArgs.assignment_dir, '')

    return htmlCode 

def getRenderedSource(srcPath):
    with open(srcPath, 'r') as f:
        sourceCode = f.read()
        success, unistr = getUnicodeStr(sourceCode)
        if success:
            try:
                lexer = guess_lexer_for_filename(srcPath, unistr)
            except pygments.util.ClassNotFound as e:
                # return '<p></p>'+'<pre>'+format(e)+'</pre>'
                return False, 'No lexer found for:'
            return True, highlight(unistr, lexer, HtmlFormatter())
        else:
            return False, '<p></p>'+'<pre>'+unistr+'</pre>'

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
            elif exitType == -1:
                s += stdoutStr
            elif exitType == 1:   # time out
                s += '(user input: %s)\n'%userInput
                s += 'Timeout'
            s += '\n'
    return s
 
def getUnicodeStr(str):
    success = True
    encodingStrs = ['utf-8', sys.getfilesystemencoding(), '(chardet)']
    try:
        detected = chardet.detect(str)
    except ValueError as e:
        retstr = format(e)
        success = False
        return success, retstr

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
# main functions
def collectAllProjInfosInAllSubmissions(submissionTitles, assignmentDir, destDir, deco2unicoMap):
    allProjInfos = []

    # process each submission
    for j in range(len(submissionTitles)):
        submissionTitle = submissionTitles[j]
        submissionType = detectSubmissionType(opjoin(assignmentDir, submissionTitle))

        # set submissionDir, projNames, projSrcFileNames for each project
        # ex)
        # projNames : ['proj1', 'proj2']
        # projSrcFileNames: [['proj1.c','proj1.h'], ['proj2.c','proj2.h']]
        if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
            # unidecode destSubmissionDir
            decodeDestSubmissionDirPathRecursive(destDir, submissionTitle, deco2unicoMap)

            if submissionType==SINGLE_SOURCE_FILE:
                submissionDir = destDir
                projSrcFileNames = [[unico2decoPath(unicode(submissionTitle), deco2unicoMap)]]

            elif submissionType==SOURCE_FILES:
                submissionDir = opjoin(destDir, unico2decoPath(unicode(submissionTitle), deco2unicoMap))

                # projSrcFileNames = [[fileName] for fileName in os.listdir(submissionDir) if gBuildDirPrefix not in name]
                projSrcFileNames = []
                for root, dirs, files in os.walk(submissionDir):
                    if gBuildDirPrefix not in root:
                        for name in files:
                            projSrcFileNames.append([opjoin(root, name).replace(submissionDir+os.sep, '')])

            projNames = [os.path.splitext(srcFileNamesInProj[0])[0] for srcFileNamesInProj in projSrcFileNames]

        elif submissionType==CMAKE_PROJECT or submissionType==VISUAL_CPP_PROJECT:
            # No need of decodeDestSubmissionDirPathRecursive(), 
            # because CMAKE_PROJECT should not include multibyte characters in its file paths already (due to cmake restriction)
            # and VISUAL_CPP_PROJECT can include multibyte characters as MSVC compiler supports it.
            submissionDir = opjoin(destDir, submissionTitle)
            projNames = [submissionTitle]

            projSrcFileNames = [[]]
            for root, dirs, files in os.walk(submissionDir):
                if gBuildDirPrefix not in root:
                    for name in files:
                        fileName = opjoin(root, name).replace(submissionDir+os.sep, '')

                        isSrcFile = True
                        for pattern in gArgs.exclude_patterns:
                            if fnmatch.fnmatch(fileName, pattern):
                                isSrcFile = False
                                break

                        if isSrcFile:
                            projSrcFileNames[0].append(fileName)

        else:
            print '%s%s: Submission type %s is not supported.'%(gLogPrefix, submissionTitle, gSubmissionTypeName[submissionType])
            continue

        # collect info
        for i in range(len(projNames)):
            projInfo = {}
            projInfo['submissionIndex'] = j
            projInfo['submissionTitle'] = submissionTitle
            projInfo['submissionType'] = submissionType
            projInfo['numSubmission'] = len(submissionTitles)
            projInfo['projIndex'] = i
            projInfo['numProjInSubmission'] = len(projNames)
            projInfo['projName'] = projNames[i]
            projInfo['submissionDir'] = submissionDir
            projInfo['filesInProj'] = projSrcFileNames[i]

            # set userInputs
            if gArgs.user_dict!=None:
                userInputs = getUserInputsFromUserDict(gArgs.user_dict, projNames[i])
            else:
                userInputs = gArgs.user_input
            projInfo['userInputs'] = userInputs

            allProjInfos.append(projInfo)

    return allProjInfos

def generateReportDataForAllProjs(allProjInfos, buildResults, runResults):
    submittedFileNames = []
    srcFileLists = []
    buildRetCodes = []
    buildLogs = []
    exitTypeLists = []
    stdoutStrLists = []
    userInputLists = []

    for i in range(len(allProjInfos)):
        projInfo = allProjInfos[i]
        submissionTitle = projInfo['submissionTitle']
        submissionDir = projInfo['submissionDir']
        filesInProj = projInfo['filesInProj']
        submissionType = projInfo['submissionType']

        buildRetCode, buildLog = buildResults[i]

        exitTypeList, stdoutStrList, userInputList = runResults[i]

        # add report data
        submittedFileNames.append(submissionTitle)

        # full path -> \hagsaeng01\munje2\munje2.c
        projOrigSrcFilePathsAfterAssignDir = []
        for srcFileName in filesInProj:
            destSrcFilePath = opjoin(submissionDir, srcFileName)
            destSrcFilePathAfterDestDir = destSrcFilePath.replace(destDir+os.sep, '')

            if gArgs.run_only:
                projOrigSrcFilePathsAfterAssignDir.append(opjoin(destDir, destSrcFilePathAfterDestDir))
            else:
                if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
                    # deco2unico src file paths to properly display in the report
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

    return submittedFileNames, srcFileLists, buildRetCodes, buildLogs, exitTypeLists, stdoutStrLists, userInputLists

def buildOneProj(projInfo):
    submissionType = projInfo['submissionType']
    projName = projInfo['projName']
    submissionDir = projInfo['submissionDir']
    filesInProj = projInfo['filesInProj']

    buildRetCode, buildLog = buildProj(submissionType, submissionDir, projName, filesInProj)

    return buildRetCode, buildLog

def runOneProj(projInfo, timeOut):
    submissionType = projInfo['submissionType']
    projName = projInfo['projName']
    submissionDir = projInfo['submissionDir']
    filesInProj = projInfo['filesInProj']
    userInputs = projInfo['userInputs']

    exitTypeList = []
    stdoutStrList = []
    userInputList = userInputs
    exitTypeList, stdoutStrList = runProj(submissionType, submissionDir, projName, filesInProj, userInputs, timeOut)

    return exitTypeList, stdoutStrList, userInputList

############################################
# project type detection

def detectSubmissionType(submissionPath):
    if os.path.isdir(submissionPath):
        # print 'dir'
        for submissionType in range(BEGIN_SUBMISSION_TYPE+1, END_SUBMISSION_TYPE):
            for pattern in gSubmissionPatterns[submissionType]:
                if len(glob.glob(opjoin(submissionPath, pattern))) > 0:
                    return submissionType
        return SOURCE_FILES
    else:
        # print 'file'
        return SINGLE_SOURCE_FILE

def decodeDestSubmissionDirPathRecursive(destDir, submissionTitle, deco2unicoMap):
    origSubDir = opjoin(destDir, submissionTitle)
    newSubDir = opjoin(destDir, unico2decoPath(unicode(submissionTitle), deco2unicoMap))

    # if --run-only mode, os.rename() will throw an exception, which is expected behavior.
    try:
        os.rename(origSubDir, newSubDir)
    except:
        pass

    for root, dirs, files in os.walk(newSubDir, topdown=False):
        for name in dirs:
            decoName = unico2decoPath(unicode(name), deco2unicoMap)
            try:
                os.rename(opjoin(root, name), opjoin(root, decoName))
            except:
                pass
        for name in files:
            decoName = unico2decoPath(unicode(name), deco2unicoMap)
            try:
                os.rename(opjoin(root, name), opjoin(root, decoName))
            except:
                pass

def decodeDestDirPathRecursive(destDir, submissionTitle, deco2unicoMap):
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

############################################
# multi processing worker functions
def worker_build(params):
    numAllProjs, i, projInfo, q = params
    buildRetCode, buildLog = buildOneProj(projInfo)
    q.put([i, buildRetCode, buildLog])
    printBuildResult(q.qsize(), numAllProjs, projInfo, buildRetCode, buildLog)

def worker_run(params):
    numAllProjs, i, projInfo, timeOut, q = params
    exitTypeList, stdoutStrList, userInputList = runOneProj(projInfo, timeOut)
    q.put([i, exitTypeList, stdoutStrList, userInputList])
    printRunResult(q.qsize(), numAllProjs, projInfo, exitTypeList, stdoutStrList)

############################################
# log print functions
def printLogPrefixDescription():
    print
    print '%s[ProcessedCount/NumAllProjs SubmissionTitle SubmissionType (ProjName)]'%gLogPrefix

def getProjLogPrefix(processedCount, numAllProjs, submissionIndex, submissionTitle, submissionType, projIndex, projName, numProjInSubmission):
    if numProjInSubmission > 1:
        # return '%s[%d/%d [%d]%s %s ([%d]%s)]'%(gLogPrefix, processedCount, numAllProjs, submissionIndex, submissionTitle, gSubmissionTypeName[submissionType], projIndex, projName)

        return '%s[%d/%d %s %s (%s)]'%(gLogPrefix, processedCount, numAllProjs, submissionTitle, gSubmissionTypeName[submissionType], projName)
    else:
        # return '%s[%d/%d [%d]%s %s]'%(gLogPrefix, processedCount, numAllProjs, submissionIndex, submissionTitle, gSubmissionTypeName[submissionType])
        return '%s[%d/%d %s %s]'%(gLogPrefix, processedCount, numAllProjs, submissionTitle, gSubmissionTypeName[submissionType])

def printBuildResult(processedCount, numAllProjs, projInfo, buildRetCode, buildLog):
    submissionIndex = projInfo['submissionIndex']
    submissionTitle = projInfo['submissionTitle']
    submissionType = projInfo['submissionType']
    numSubmission = projInfo['numSubmission']
    projIndex = projInfo['projIndex']
    numProjInSubmission = projInfo['numProjInSubmission']
    projName = projInfo['projName']
    submissionDir = projInfo['submissionDir']
    filesInProj = projInfo['filesInProj']
    userInputs = projInfo['userInputs']

    logPrefix = getProjLogPrefix(processedCount, numAllProjs, submissionIndex, submissionTitle, submissionType, projIndex, projName, numProjInSubmission)

    if buildRetCode==0:
        print '%s Build succeeded.'%logPrefix
    elif buildRetCode==-1:
        print '%s Build failed. %s'%(logPrefix, buildLog)
    else:
        print '%s Build failed. A build error occurred.'%logPrefix

def printRunResult(processedCount, numAllProjs, projInfo, exitTypeList, stdoutStrList):
    submissionIndex = projInfo['submissionIndex']
    submissionTitle = projInfo['submissionTitle']
    submissionType = projInfo['submissionType']
    numSubmission = projInfo['numSubmission']
    projIndex = projInfo['projIndex']
    numProjInSubmission = projInfo['numProjInSubmission']
    projName = projInfo['projName']
    submissionDir = projInfo['submissionDir']
    filesInProj = projInfo['filesInProj']
    userInputs = projInfo['userInputs']

    logPrefix = getProjLogPrefix(processedCount, numAllProjs, submissionIndex, submissionTitle, submissionType, projIndex, projName, numProjInSubmission)

    if exitTypeList[0]==0:
        print '%s Execution terminated.'%logPrefix
    elif exitTypeList[0]==-1:
        print '%s Execution failed. %s'%(logPrefix, stdoutStrList[0])
    elif exitTypeList[0]==1:
        print '%s Execution was stopped due to timeout.'%logPrefix
    else:
        raise NotImplementedError

if __name__=='__main__':

    ############################################
    # argparse

    parser = argparse.ArgumentParser(prog='pacers.py', description='Programming Assignments Compiling, Executing, and Reporting system', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('assignment_dir',
                        help='''A direcory that has submissions.
The type of each submission is auto-detected by PACERs.

| Submission types   | Meaning                                              |
|--------------------|------------------------------------------------------|
| SINGLE_SOURCE_FILE | The submission has a single source or resource file. |
| SOURCE_FILES       | The submission has source or resource files without any project files.|
| CMAKE_PROJECT      | The submission has CMakeLists.txt.                   |
| VISUAL_CPP_PROJECT | The submission has *.vcxproj or *.vcproj.            |

Each submission can have only one source file, or a zip file
or a directory including many files.''')
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
    # parser.add_argument('--file-layout', default=0, type=int,
                        # help='''indicates file layout in the assignment_dir. \ndefault: 0
    # 0 - one source file runs one program. 
    # each submission might have only one source file or a 
    # zip file or a directory including multiple source files.''')
    parser.add_argument('--timeout', default=2., type=float,
                        help='''Each target program is killed when TIMEOUT(seconds)
is reached. Useful for infinite loop cases.
Setting zero seconds(--timeout 0) means unlimited execution time
for each target program, which can be useful for GUI applications.
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
    parser.add_argument('--run-serial', action='store_true',
                        help='''When specified, run each target program in serial.
PACERs runs programs in parallel by default. ''')
    parser.add_argument('--build-serial', action='store_true',
                        help='''When specified, build each target program in serial.
PACERs builds programs in parallel by default. ''')
    parser.add_argument('--run-only-serial', action='store_true',
                        help='''Shortcut for --run-only --run-serial.''')
    parser.add_argument('--num-cores', default=mp.cpu_count(), type=int,
                        help='''Specify number of cpu cores used in building and running process.
default: number of cpu cores in your machine.''')
    parser.add_argument('--no-report', action='store_true',
                        help='''When specified, the final report is not generated.''')
    parser.add_argument('--exclude-patterns', nargs='+', default=[''],
                        help='''Files containing EXCLUDE_PATTERNS in their relative path
from each submission directory are excluded from the final report.
(Submission dir: 'student01' in 'test-assignments/c-assignment-4')
For example, use "--exclude-pattern *.txt foo/*"
to exclude all txt files and all files in foo directory
in each submission directory from the final report.''')
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
    # parser.add_argument('--user-dict', default=None,
                    # help='''An alternative option to specify user input
# which can be helpful for SOURCE_FILES submission type. 
# Specify USER_DICT to be sent to the stdin of target
# programs. Argument should be python dictionary 
# representation. Each 'key' of the dictionary item
# is 'suffix' that should match with the last parts of 
# each source file name. 'value' is user input for 
# those matched source files.
# If both --user-input and --user-dict are specified,
# only --user-dict is used.

# Example:
# --user-dict {'1':['1','2'], '2':['2,'5','7']}

# runs a source file whose name ends with '1'   
# (e.g. prob1.c) 2 times (with '10', '20')     
# and run a source file whose name ends with   
# '2' (e.g. prob2.c) 3 times (with '2','5','7').
# ''')

    gArgs = parser.parse_args()

    if gArgs.run_only_serial:
        gArgs.run_only = True 
        gArgs.run_serial = True

    # print gArgs
    # print gArgs.exclude_patterns
    # exit()

    if not gArgs.assignment_alias:
        gArgs.assignment_alias = os.path.basename(os.path.abspath(gArgs.assignment_dir))

    ############################################
    # main routine

    print
    print '%sStarting PACERs...'%gLogPrefix

    # preprocess --user-dict
    gArgs.user_dict = None
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
    submissionTitles = []
    for name in os.listdir(gArgs.assignment_dir):
        # to exclude .zip files - submissionTitle will be from unzipDirNames by unzipInAssignDir() in assignment_dir
        if not os.path.isdir(opjoin(gArgs.assignment_dir, name)) and os.path.splitext(name)[1].lower()=='.zip':
            continue
        submissionTitles.append(name)

    # collect all project info
    allProjInfos = collectAllProjInfosInAllSubmissions(submissionTitles, gArgs.assignment_dir, destDir, deco2unicoMap)

    printLogPrefixDescription()

    # build projects one by one
    buildResults = [None]*len(allProjInfos)
    if not gArgs.run_only:
        if not gArgs.build_serial:
            print 
            print '%sBuilding projects in parallel with %d cores...'%(gLogPrefix, gArgs.num_cores)
            print
            p = mp.Pool(gArgs.num_cores)
            q = mp.Manager().Queue()
            p.map(worker_build, [(len(allProjInfos), i, allProjInfos[i], q) for i in range(len(allProjInfos))])
            while not q.empty():
                i, buildRetCode, buildLog = q.get()
                buildResults[i] = [buildRetCode, buildLog]
        else:
            print 
            print '%sBuilding projects in serial...'%gLogPrefix
            print
            for i in range(len(allProjInfos)):
                buildRetCode, buildLog = buildOneProj(allProjInfos[i])
                buildResults[i] = [buildRetCode, buildLog]
                printBuildResult(i+1, len(allProjInfos), allProjInfos[i], buildRetCode, buildLog)
    else:
        for i in range(len(allProjInfos)):
            buildResults[i] = [0, '']

    # run projects one by one
    runResults = [None]*len(allProjInfos)
    if not gArgs.build_only:
        if not gArgs.run_serial:
            print 
            print '%sRunning projects in parallel with %d cores...'%(gLogPrefix, gArgs.num_cores)
            print
            p = mp.Pool(gArgs.num_cores)
            q = mp.Manager().Queue()
            p.map(worker_run, [(len(allProjInfos), i, allProjInfos[i], gArgs.timeout, q) for i in range(len(allProjInfos))])
            while not q.empty():
                i, exitTypeList, stdoutStrList, userInputList = q.get()
                runResults[i] = [exitTypeList, stdoutStrList, userInputList]
        else:
            print 
            print '%sRunning projects in serial...'%gLogPrefix
            print
            for i in range(len(allProjInfos)):
                exitTypeList, stdoutStrList, userInputList = runOneProj(allProjInfos[i], gArgs.timeout)
                runResults[i] = [exitTypeList, stdoutStrList, userInputList]
                printRunResult(i+1, len(allProjInfos), allProjInfos[i], exitTypeList, stdoutStrList)
    else:
        for i in range(len(allProjInfos)):
            runResults[i] = [[-1], [''], ['']]

    # generate report data
    submittedFileNames, srcFileLists, buildRetCodes, buildLogs, exitTypeLists, stdoutStrLists, userInputLists = \
            generateReportDataForAllProjs(allProjInfos, buildResults, runResults)

    print

    if not gArgs.no_report:
        print '%sGenerating Report for %s...'%(gLogPrefix, gArgs.assignment_alias)
        generateReport(gArgs, submittedFileNames, \
                        srcFileLists, buildRetCodes, buildLogs, exitTypeLists, stdoutStrLists, userInputLists)

    removeUnzipDirsInAssignDir(gArgs.assignment_dir, unzipDirNames)
    print '%sDone.'%gLogPrefix
