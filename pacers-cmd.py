#!/usr/bin/env python

################################################################################
# pacers-cmd.py

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
pacers-cmd.py
    : PACERs script for capturing shell command output executed in each submission dir as a txt file

Usage example:
    ./pacers-cmd.py test-assignments/zip-assignment-1 --external-cmds "ls" "ls -al"
'''

import os, shutil, argparse, glob

from pacerslib.unicode import *
from pacerslib.file import *

def getOutputDir(args):
    return opjoin(args.output_dir, args.assignment_alias)

# pacers-cmd.py test-assignments\zip-assignment-1 --external-cmds "ls" "ls -al"

if __name__=='__main__':
    parser = argparse.ArgumentParser(prog='pacers-cmd.py',
            description='pacers to capture shell command output in each submission dir as txt file', 
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('assignment_dir')
    parser.add_argument('--assignment-alias',
                        help='''Specify ASSIGNMENT_ALIAS for each assignment_dir. 
ASSIGNMENT_ALIAS is used when making a sub-directory 
in OUTPUT_DIR and the final report file. 
default: "basename" of assignment_dir (bar if 
assignment_dir is /foo/bar/).''')
    parser.add_argument('--output-dir', default=opjoin('.', 'output-cmd'),
                        help='''Specify OUTPUT_DIR in which the final report file 
and build output files to be generated. 
Avoid including hangul characters in its full path.
default: %s'''%opjoin('.', 'output'))

    parser.add_argument('--external-cmds', nargs='+', default=[''],
                        help='''external cmds''')

    gArgs = parser.parse_args()

    # print gArgs.external_cmds
    # exit()

    if not gArgs.assignment_alias:
        gArgs.assignment_alias = os.path.basename(os.path.abspath(gArgs.assignment_dir))

    # unzip in .zip files in assignment_dir
    unzipDirNames = unzipInAssignDir(gArgs.assignment_dir)

    # get submission titles
    submissionTitles = []
    for name in os.listdir(gArgs.assignment_dir):
        # to exclude .zip files - submissionTitle will be from unzipDirNames by unzipInAssignDir() in assignment_dir
        if not os.path.isdir(opjoin(gArgs.assignment_dir, name)) and os.path.splitext(name)[1].lower()=='.zip':
            continue
        submissionTitles.append(name)

    # tidy submission dir up if submission dir has only one subdir and no files
    # ex)
    # submissionTitle/
    #   - dir1
    #     - file1
    #     - file2
    # =>
    # submissionTitle/
    #   - file1
    #   - file2
    for i in range(len(submissionTitles)):
        submissionPath = opjoin(gArgs.assignment_dir, submissionTitles[i])
        if os.path.isdir(submissionPath):
            ls = os.listdir(submissionPath)
            if len(ls)==1 and os.path.isdir(opjoin(submissionPath, ls[0])):
                copytree2(opjoin(submissionPath, ls[0]), submissionPath)
                shutil.rmtree(opjoin(submissionPath, ls[0]))

    # run external cmds and write stdout to a file
    outputDir = getOutputDir(gArgs)
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    for i in range(len(submissionTitles)):
        print 'Processing '+submissionTitles[i]+'...'
        submissionPath = opjoin(gArgs.assignment_dir, submissionTitles[i])
        resultStr = ''

        for cmd in gArgs.external_cmds:
            resultStr += '===================================\n'
            resultStr += '(cmd: '+cmd+')\n'
            try:
                # posix
                # stdoutStr = subprocess.check_output('cd "%s" && %s'%(toString(submissionPath), cmd), stderr=subprocess.STDOUT, shell=True)

                # window
                stdoutStr = subprocess.check_output('pushd "%s" && %s && popd'%(toString(submissionPath), cmd), stderr=subprocess.STDOUT, shell=True)

            except subprocess.CalledProcessError as e:
                resultStr += e.output
            else:
                resultStr += stdoutStr

        with open(opjoin(outputDir, submissionTitles[i]+'.txt'), 'w') as f:
            f.write(resultStr)
    
    removeUnzipDirsInAssignDir(gArgs.assignment_dir, unzipDirNames)
