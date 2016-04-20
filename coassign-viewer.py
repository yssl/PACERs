#-*- coding: utf-8 -*-
'''
coassign-viewer.py
    : Automatic building & launching & reporting system for a large number of programming assignment files

Requirements:
    python 2.x
    cmake
    Pygments (install via pip install Pygments)
    Unidecode (install via pip install unidecode)

Tested language & platform:
    C - Microsoft Visual Studio 2010 on Windows 10

* On MS Windows, please add these paths to the system path. XX.X means your version.
    C:\Program Files (x86)\Microsoft Visual Studio XX.X\VC\bin\IDE
    C:\Program Files (x86)\Microsoft Visual Studio XX.X\Common7\IDE

Usage:
    assignmentDir: 
        root directory of each assignments

    assignmentParams:
        subdir: 
            sub directory under assignmentDir for each specific assignment
            should not have hangul characters
        input:
            stdin of the program. [1,'hello world'] means 1 <enter> hello world <enter>.
        file-layout:
            0 - one source file (.c or .cpp) for each individual
            1 - multiple source files (zipped) for each individual, but one file per one program
            2 - multiple files (zipped) for each individual including .vcproj
        code-type (optional):
            representitive file extension of source files. if not specified, the extension of the first file is used.

    outputDir:
        its absolute path should not have hangul characters
'''

import os, sys, shutil, subprocess, threading, time
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter
from unidecode import unidecode

reload(sys)
sys.setdefaultencoding('cp949')

############################################
# user settings
assignmentDir = u'd:\\3-AssistantProf\\OneDrive\\Lecture\\2016-1\\C프로그래밍\\과제채점'
# assignmentDir = u'.\\test-assignment'

assignmentParams = [{'subdir':'7-01', 'user-input':'', 'file-layout':0}]
# assignmentParams = [{'subdir':'test-1', 'user-input':'', 'file-layout':0}]

runOnly = False

outputDir = '.\\output'

timeOut = 2.

############################################
# main functions

# return workDir
def prepare(origFilePath, outputDir, subdir, projName, fileName):
    # make workspace directory for projName
    workDir = opjoin(outputDir, opjoin(subdir, projName))
    try:
        os.makedirs(workDir)
    except OSError as e:
        pass

    # copy assignment file to build directory
    shutil.copy(origFilePath, workDir)

    return workDir

# return CMakeLists.txt code
def getCMakeListsFileContents(projName, fileNames):
    srcFileCount = 0
    code = ''
    code += 'cmake_minimum_required(VERSION 2.6)\n'
    code += 'project(%s)\n'%projName
    code += 'add_executable(%s '%projName
    for fileName in fileNames:
        ext = os.path.splitext(fileName)[1].lower()
        if ext=='.c' or ext=='.cpp':
            code += '%s '%fileName
            srcFileCount += 1
    code += ')\n'
    return code

# return errorCode, buildLog
def build(repSrcExt, buildDir, projName, fileNames):

    if repSrcExt in codeExt:
        return codeExt[repSrcExt]['build-func'](buildDir, projName, fileNames)
    else:
        print '%s%s is not a supported source file type. If extension is not correct, please add \'code-type\' to assignmentParam.'%(logPrefix, repSrcExt)
        return None, None 

def onTimeOut(proc):
    gKillFunc(proc)

# return exitType, output(stdout) of target program
# exitType:
#   0 - normal exit
#   1 - forced kill due to timeout
def run(repSrcExt, workDir, projName, userInput, timeOut):
    proc = subprocess.Popen([gRunPrefix + codeExt[repSrcExt]['runcmd-func'](projName)], cwd=workDir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    timer = threading.Timer(timeOut, onTimeOut, [proc])
    
    timer.start()
    stdoutStr = proc.communicate(userInput)[0]

    if timer.is_alive():
        timer.cancel()
        return 0, stdoutStr
    else:
        return 1, stdoutStr

def viewOneProgram():
    pass

def generateReport(outputDir, assignmentDir, assignmentParam, submittedFileNames,\
                srcFileLists, buildRetCodes, buildLogs, exitTypes, stdoutStrs):
    htmlCode = ''

    # header
    htmlCode += '''<html>
<head>
<title>Assignment %s Report</title>
<style type="text/css">
%s
</style>
</head>
<body>'''%(assignmentParam['subdir'], HtmlFormatter().get_style_defs())

    # beginning
    htmlCode += '''<pre>
    Assignment %s Report

    source code directory: %s
    assignmentParam: %s
</pre>'''%(assignmentParam['subdir'], opjoin(os.path.abspath(assignmentDir), assignmentParam['subdir']), assignmentParam)

    # main table
    htmlCode += '''<table border=1>
<tr>
<td>Submitted File</td>
<td>Source Files</td>
<td>Output</td>
<td>Score</td>
<td>Comment</td>
</tr>'''

    for i in range(len(submittedFileNames)):
        htmlCode += '<tr>\n'
        htmlCode += '<td>%s</td>\n'%submittedFileNames[i]
        htmlCode += '<td>%s</td>\n'%getSourcesTable(srcFileLists[i])
        htmlCode += '<td>%s</td>\n'%getOutput(buildRetCodes[i], buildLogs[i], exitTypes[i], stdoutStrs[i])
        htmlCode += '<td>%s</td>\n'%''
        htmlCode += '<td>%s</td>\n'%''
        htmlCode += '</tr>\n'

    htmlCode += '</table>\n'

    # footer
    htmlCode += '''</body>
</html>'''

    # write html
    with open(opjoin(opjoin(outputDir, assignmentParam['subdir']),'report-%s.html'%assignmentParam['subdir']), 'w') as f:
        f.write(htmlCode.encode('utf-8'))
        # try:
            # f.write(htmlCode)
        # except UnicodeEncodeError:
            # f.write(htmlCode.encode('utf-8'))
        
def getSourcesTable(srcPaths):
    htmlCode = ''
    for srcPath in srcPaths:
        htmlCode += '%s\n'%os.path.basename(srcPath)
        htmlCode += '%s\n'%getRenderedSource(srcPath)
    return htmlCode 

def getRenderedSource(srcPath):
    with open(srcPath, 'r') as f:
        sourceCode = f.read()
    return highlight(sourceCode, guess_lexer_for_filename(srcPath, sourceCode), HtmlFormatter())

def getOutput(buildRetCode, buildLog, exitType, stdoutStr):
    s = '<pre>\n'
    if buildRetCode!=0: # build error
        s += buildLog
    else:
        if exitType == 1:   # time out
            s += 'Timeout'
        else:
            s += stdoutStr
    return s
 
############################################
# functions for each source file extension

# return errorCode, buildLog
def build_c_cpp(buildDir, projName, fileNames):
    # make CMakeLists.txt
    cmakeCode = getCMakeListsFileContents(projName, fileNames)
    with open(opjoin(buildDir,'CMakeLists.txt'), 'w') as f:
        f.write(cmakeCode)

    # build
    try:
        buildLog = subprocess.check_output('cd %s && %s'%(buildDir, gBuildCmd), shell=True)
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output
    else:
        return 0, buildLog

def runcmd_c_cpp(projName):
    return '%s.exe'%projName

############################################
# functions for each platform

def kill_windows(proc):
    # http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
    subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=proc.pid))

def kill_linux(proc):
    # http://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
    proc.kill()


############################################
# pre-defined

env = {'nt':{}, 'posix':{}}
env['nt']['build-cmd'] = 'vcvars32.bat && cmake ./ -G "NMake Makefiles" && nmake'
env['nt']['kill-func'] = kill_windows
env['nt']['run-prefix'] = ''
env['posix']['build-cmd'] = 'cmake ./; make'
env['posix']['kill-func'] = kill_linux
env['posix']['run-prefix'] = 'exec '

gBuildCmd = env[os.name]['build-cmd']
gKillFunc = env[os.name]['kill-func']
gRunPrefix = env[os.name]['run-prefix']

codeExt = {'.c':{}, '.cpp':{}}
codeExt['.c']['build-func'] = build_c_cpp
codeExt['.c']['runcmd-func'] = runcmd_c_cpp
codeExt['.cpp']['build-func'] = build_c_cpp
codeExt['.cpp']['runcmd-func'] = runcmd_c_cpp

opjoin = os.path.join
logPrefix = '### '

############################################
# main routine

for assignmentParam in assignmentParams:
    submittedFileNames = []
    srcFileLists = []
    buildRetCodes = []
    buildLogs = []
    exitTypes = []
    stdoutStrs = []

    origSubDirPath = opjoin(assignmentDir, assignmentParam['subdir'])
    count = 0
    for origFileName in os.listdir(origSubDirPath):
        count += 1;
        # if count>2:
            # break

        origFilePath =  opjoin(origSubDirPath, origFileName)
        if os.path.isdir(origFilePath):
            continue

        if 'file-layout' in assignmentParam:
            fileLayout = assignmentParam['file-layout']
        else:
            fileLayout = 0

        fileName = unidecode(origFileName)
        projName, ext = os.path.splitext(os.path.basename(fileName))

        print
        print '%s'%logPrefix
        print '%sStart processing %s'%(logPrefix, fileName)

        if fileLayout==0:
            # 0 - one program per each student (one program can have multiple source files (1 zip file))

            # prepare workDir
            workDir = prepare(origFilePath, outputDir, assignmentParam['subdir'], projName, fileName)
            print '%sWork directory: %s'%(logPrefix, workDir)

            # get origSrcFileNames, repSrcExt
            if ext=='.zip':
                origSrcFileNames, srcExts = unzip(fileName)
            else:
                origSrcFileNames = [origFileName]
                srcExts = [ext]
            repSrcExt = assignmentParam['code-type'] if 'code-type' in assignmentParam else srcExts[0]

            # unidecode srcFiles
            srcFileNames = []
            for i in range(len(origSrcFileNames)):
                srcFileName = unidecode(origSrcFileNames[i]) 
                shutil.move(opjoin(workDir, origSrcFileNames[i]), opjoin(workDir, srcFileName))
                srcFileNames.append(srcFileName)

            # build
            print '%sStart build'%logPrefix
            buildRetCode, buildLog = build(repSrcExt, workDir, projName, srcFileNames)

            if buildRetCode!=0:
                print '%sBuild error. Go on a next file...'%logPrefix
            else:
                print '%sEnd build'%logPrefix
                print '%sStart running'%logPrefix
                exitType, stdoutStr = run(repSrcExt, workDir, projName, assignmentParam['user-input'], timeOut)
                print '%sEnd running'%logPrefix

            # add report data
            submittedFileNames.append(origFileName)
            srcFileLists.append([opjoin(origSubDirPath, origSrcFileName) for origSrcFileName in origSrcFileNames])
            buildRetCodes.append(buildRetCode)
            buildLogs.append(buildLog)
            if buildRetCode==0:
                exitTypes.append(exitType)
                stdoutStrs.append(stdoutStr)
            else:
                exitTypes.append(None)
                stdoutStrs.append(None)

        elif fileLayout==1:
            # 1 - multiple programs (zipped) per each student (one file per each program)
            infileNames = unzip(fileName)
            for infileName in infileNames:
                inprojName, ext = os.path.splitext(os.path.basename(infileName))
                projName += inprojName

        print '%sGenerating Report for %s...'%(logPrefix, assignmentParam['subdir'])
        generateReport(outputDir, assignmentDir, assignmentParam, submittedFileNames, \
                        srcFileLists, buildRetCodes, buildLogs, exitTypes, stdoutStrs)
        print 'Done.'
