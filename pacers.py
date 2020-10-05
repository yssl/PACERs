#!/usr/bin/env python

################################################################################
# pacers.py

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

'''
PACERs
    : Programming Assignments Compiling, Executing, and Reporting system

Please see https://github.com/yssl/PACERs for more information.
'''

import os, shutil, time, argparse, glob
import multiprocessing as mp

from pacerslib.global_const import *
from pacerslib.build import *
from pacerslib.file import *
from pacerslib.log import *
from pacerslib.report import *
from pacerslib.run import *
from pacerslib.unicode import *
from pacerslib.version import *
from pacerslib.process import *
from pacerslib.submission import *

############################################
# multi processing worker functions
def worker_build(params):
    numAllProjs, i, projInfo, q = params
    buildRetCode, buildLog, buildVersion = buildOneProj(projInfo)
    q.put([i, buildRetCode, buildLog, buildVersion])
    printBuildResult(q.qsize(), numAllProjs, projInfo, buildRetCode, buildLog)

def worker_run(params):
    buildRetCode, numAllProjs, i, projInfo, timeOut, interpreterCmd, preShellCmd, q = params
    if buildRetCode==0:
        exitTypeList, stdoutStrList, stdInputList, cmdArgsList = runOneProj(projInfo, timeOut, interpreterCmd, preShellCmd)
    else:
        exitTypeList = [-1]
        stdoutStrList = ['Due to the build error.']
        stdInputList = ['']
        cmdArgsList = ['']
    q.put([i, exitTypeList, stdoutStrList, stdInputList, cmdArgsList])
    printRunResult(q.qsize(), numAllProjs, projInfo, exitTypeList, stdoutStrList)



if __name__=='__main__':

    ############################################
    # argparse

    parser = argparse.ArgumentParser(prog='pacers.py', formatter_class=argparse.RawTextHelpFormatter, 
            description='''PACERs
    : Programming Assignments Compiling, Executing, and Reporting system''')
    parser.add_argument('assignment_dir',
                        help='''A direcory that has submissions.
The type of each submission is auto-detected by PACERs.

| Submission types   | Meaning                                               |
|--------------------|-------------------------------------------------------|
| SINGLE_SOURCE_FILE | Each submission has a single source or resource file  |
|                    | which constitutes a single project (program).         |
|--------------------|-------------------------------------------------------|
| SOURCE_FILES       | Each submission has source or resource files without  |
|                    | any kind of project files. A single source file in    |
|                    | a submission constitutes a single project (program).  |
|--------------------|-------------------------------------------------------|
| CMAKE_PROJECT      | Each submission has CMakeLists.txt and constitutes    |
|                    | a single project (program).                           |
|--------------------|-------------------------------------------------------|
| VISUAL_CPP_PROJECT | Each submission has *.vcxproj or *.vcproj and         |
|                    | constitutes a single project (program).               |
|--------------------|-------------------------------------------------------|
| MAKE_PROJECT       | Each submission has Makefile and constitutes          |
|                    | a single project (program).                           |

Each submission can have only one source file, or a zip file
or a directory including many files.''')
    parser.add_argument('--std-input', nargs='+', default=[''],
                        help='''Specify STD_INPUT to be sent to the stdin of target
programs. This option should be located after
assignment_dir if no other optional arguments are
given. Two types of STD_INPUT are available.
default is an empty string.

| Type     | Example                 | Meaning                                     |
|----------|-------------------------|---------------------------------------------|
| Single   | --std-input 15          | Run each program with input                 |
| value    |                         |   "15" (STD_INPUT[0])                       |
|          | --std-input hello       | Run each program with input                 |
|          |                         |   "hello" (STD_INPUT[0])                    |
|          | --std-input "1 2"       | Run each program with input                 |
|          |                         |   "1 2" (STD_INPUT[0])                      |
|----------|-------------------------|---------------------------------------------|
| Multiple | --std-input 1 2 3       | Run each program 3 times: with              |
| values   |                         |   "1" (STD_INPUT[0]), "2" (STD_INPUT[1]),   |
|          |                         |   "3" (STD_INPUT[2])                        |
|          | --std-input "1 2" "3 4" | Run each program 2 times: with              |
|          |                         |   "1 2" (STD_INPUT[0]), "3 4" (STD_INPUT[1])|

''')
    parser.add_argument('--cmd-args', nargs='+', default=[''],
                        help='''Specify CMD_ARGS to be used as the command line arguments
of target programs. This option should be located after
assignment_dir if no other optional arguments are
given. Two types of CMD_ARGS are available.
default is an empty string.

| Type     | Example                    | Meaning                                     |
|----------|----------------------------|---------------------------------------------|
| Single   | --cmd-args 15              | Run each program with                       |
| value    |                            |   argv[1]:"15" (CMD_ARGS[0])                |
|          | --cmd-args hello           | Run each program with                       |
|          |                            |   argv[1]:"hello" (CMD_ARGS[0])             |
|          | --cmd-args "1 2"           | Run each program with                       |
|          |                            |   argv[1]:"1", argv[2]:"2" (CMD_ARGS[0])    |
|          | --cmd-args "1 2 \\"ab cd\\"" | Run each program with                       |
|          |                            |   argv[1]:"1", argv[2]:"2", argv[3]:"ab cd" |
|          |                            |   (CMD_ARGS[0])                             |
|----------|----------------------------|---------------------------------------------|
| Multiple | --cmd-args 1 2 3           | Run each program 3 times: with              |
| values   |                            |   argv[1]:"1" (CMD_ARGS[0]),                |
|          |                            |   argv[1]:"2" (CMD_ARGS[1]),                |
|          |                            |   argv[1]:"3" (CMD_ARGS[2])                 |
|          | --cmd-args "1 2" "3 4"     | Run each program 2 times: with              |
|          |                            |   argv[1]:"1", argv[2]:"2" (CMD_ARGS[0]),   |
|          |                            |   argv[1]:"3", argv[2]:"4" (CMD_ARGS[1])    |

If both STD_INPUT and CMD_ARGS are specified, both elements 
at the same index (STD_INPUT[i] and CMD_ARGS[i]) are used 
together. If the number of elements in STD_INPUT and 
CMD_ARGS is different, the last element in the shorter side 
is used along with the remaining elements in the longer side.
For example,
--std-input 1 2 3 --cmd-args a b c
  : Run each program 3 times: (1, a), (2, b), (3, c)
--std-input 1 2 3 --cmd-args a b 
  : Run each program 3 times: (1, a), (2, b), (3, b)
--std-input 1 --cmd-args a b c
  : Run each program 3 times: (1, a), (1, b), (1, c)

''')
    parser.add_argument('--timeout', default=2., type=float,
                        help='''Each target program is killed when TIMEOUT(seconds)
is reached. Useful for infinite loop cases.
Setting zero seconds(--timeout 0) means unlimited execution time
for each target program, which can be useful for GUI applications.
default: 2.0''')
    parser.add_argument('--run-only', action='store_true',
                    help='''When specified, run each target program without build.
You may use it when you want change STD_INPUT without
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
    parser.add_argument('--output-dir', default=opjoin(u'.', u'output'),
                        help='''Specify OUTPUT_DIR in which the final report file 
and build output files to be generated. 
Avoid including hangul characters in its full path.
default: %s'''%'./output')
    parser.add_argument('--interpreter-cmd', default='',
                        help='''Specify INTERPRETER_CMD that executes an interpreter
for interpreted languages such as python.
default: \'python\' for python''')
    parser.add_argument('--pre-shell-cmd', default='',
                        help='''Specify PRE_SHELL_CMD that is executed before
INTERPRETER_CMD or a target executable in the same shell.
default: \'\' ''')
# parser.add_argument('--user-dict', default=None,
                    # help='''An alternative option to specify user input
# which can be helpful for SOURCE_FILES submission type. 
# Specify USER_DICT to be sent to the stdin of target
# programs. Argument should be python dictionary 
# representation. Each 'key' of the dictionary item
# is 'suffix' that should match with the last parts of 
# each source file name. 'value' is user input for 
# those matched source files.
# If both --std-input and --user-dict are specified,
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
    # exit()

    if not gArgs.assignment_alias:
        gArgs.assignment_alias = os.path.basename(os.path.abspath(gArgs.assignment_dir))

    ############################################
    # unicode arguments
    gArgs.assignment_dir = toUnicode(gArgs.assignment_dir)
    gArgs.assignment_alias = toUnicode(gArgs.assignment_alias)

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

    unzipDirNames = unzipInAssignDir(gArgs.assignment_dir)

    submissionTitles, submissionPaths = getSubmissionTitlesAndPaths(gArgs.assignment_dir)

    TidyUpSingleSubdirSubmissionDirs(submissionPaths)

    # copy assignment_dir to destDir(output_dir/assignment_alias)
    deco2unicoMap = {'':''}
    decodeAlias = unico2decoPath(gArgs.assignment_alias, deco2unicoMap)
    destDir = opjoin(gArgs.output_dir, decodeAlias)

    if not gArgs.run_only:
        print '%sCopying all submissions from \'%s\' to \'%s\'...'%(gLogPrefix, gArgs.assignment_dir, destDir)
        # delete exsting one
        if os.path.exists(destDir):
            # Convert paths for shutil to byte string only for posix os (due to python bug?)
            if os.name=='posix':
                shutil.rmtree(toString(destDir))
            else:
                shutil.rmtree(destDir)
            time.sleep(.01)
        # copy tree
        if os.name=='posix':
            # Convert paths for shutil to byte string only for posix os (due to python bug?)
            shutil.copytree(toString(gArgs.assignment_dir), toString(destDir))
        else:
            shutil.copytree(gArgs.assignment_dir, destDir)
    else:
        # delete report file only
        try:
            os.remove(getReportFilePath(gArgs))
        except OSError:
            pass

    # collect all project info
    allProjInfos = collectAllProjInfosInAllSubmissions(submissionTitles, gArgs.assignment_dir, gArgs.exclude_patterns, gArgs.std_input, gArgs.cmd_args, destDir, deco2unicoMap)

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
                i, buildRetCode, buildLog, buildVersion = q.get()
                buildResults[i] = [buildRetCode, buildLog, buildVersion]
        else:
            print 
            print '%sBuilding projects in serial...'%gLogPrefix
            print
            for i in range(len(allProjInfos)):
                printBuildStart(i+1, len(allProjInfos), allProjInfos[i])
                buildRetCode, buildLog, buildVersion = buildOneProj(allProjInfos[i])
                buildResults[i] = [buildRetCode, buildLog, buildVersion]
                printBuildResult(i+1, len(allProjInfos), allProjInfos[i], buildRetCode, buildLog)
    else:
        for i in range(len(allProjInfos)):
            buildResults[i] = [0, '', 'no-build-version']

    # run projects one by one
    runResults = [None]*len(allProjInfos)
    if not gArgs.build_only:
        if not gArgs.run_serial:
            print 
            print '%sRunning projects in parallel with %d cores...'%(gLogPrefix, gArgs.num_cores)
            print
            p = mp.Pool(gArgs.num_cores)
            q = mp.Manager().Queue()
            p.map(worker_run, [(buildResults[i][0], len(allProjInfos), i, allProjInfos[i], gArgs.timeout, gArgs.interpreter_cmd, gArgs.pre_shell_cmd, q) for i in range(len(allProjInfos))])
            while not q.empty():
                i, exitTypeList, stdoutStrList, stdInputList, cmdArgsList = q.get()
                runResults[i] = [exitTypeList, stdoutStrList, stdInputList, cmdArgsList]
        else:
            print 
            print '%sRunning projects in serial...'%gLogPrefix
            print
            for i in range(len(allProjInfos)):
                printRunStart(i+1, len(allProjInfos), allProjInfos[i])
                if buildResults[i][0]==0:
                    exitTypeList, stdoutStrList, stdInputList, cmdArgsList = runOneProj(allProjInfos[i], gArgs.timeout, gArgs.interpreter_cmd, gArgs.pre_shell_cmd)
                else:
                    exitTypeList = [-1]
                    stdoutStrList = ['Due to build error.']
                    stdInputList = ['']
                    cmdArgsList = ['']
                runResults[i] = [exitTypeList, stdoutStrList, stdInputList, cmdArgsList]
                printRunResult(i+1, len(allProjInfos), allProjInfos[i], exitTypeList, stdoutStrList)
    else:
        for i in range(len(allProjInfos)):
            runResults[i] = [[-1], [''], [''], ['']]

    # generate report data
    submittedFileNames, srcFileLists, buildRetCodes, buildLogs, exitTypeLists, stdoutStrLists, stdInputLists, cmdArgsLists, submissionTypes, buildVersionSet = \
            generateReportDataForAllProjs(allProjInfos, buildResults, runResults, destDir, gArgs, deco2unicoMap)

    print

    if not gArgs.no_report:
        print '%sGenerating Report for %s...'%(gLogPrefix, gArgs.assignment_alias)
        generateReport(gArgs, submittedFileNames, srcFileLists, buildRetCodes, buildLogs, exitTypeLists, stdoutStrLists,
                stdInputLists, cmdArgsLists, submissionTypes, buildVersionSet)

    removeUnzipDirsInAssignDir(gArgs.assignment_dir, unzipDirNames)
    print '%sDone.'%gLogPrefix
