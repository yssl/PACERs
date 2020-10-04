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
    : PACERs script for capturing shell command output for each submission as a text file

Usage example:
    ./pacers-cmd.py test-assignments/zip-assignment-1 --cmds "ls" "ls -al"

Please see https://github.com/yssl/PACERs for more information.
'''

import os, shutil, argparse, glob

from pacerslib.unicode import *
from pacerslib.file import *
from pacerslib.submission import *

def getOutputDir(args):
    return opjoin(args.output_dir, args.assignment_alias)

if __name__=='__main__':
    parser = argparse.ArgumentParser(prog='pacers-cmd.py', formatter_class=argparse.RawTextHelpFormatter,
            description='''pacers-cmd.py
    : PACERs script for capturing shell command output for each submission as a text file''')
    parser.add_argument('assignment_dir',
                        help='''A direcory that has submissions.''')
    parser.add_argument('--cmds', nargs='+', default=[''],
                        help='''Shell commands to be executed for each submission directory.''')
    parser.add_argument('--output-dir', default=opjoin('.', 'output-cmd'),
                        help='''Specify OUTPUT_DIR in which the captured text files to be generated. 
default: %s'''%'./output-cmd')


    gArgs = parser.parse_args()

    # print gArgs.cmds
    # exit()

    unzipDirNames = unzipInAssignDir(gArgs.assignment_dir)

    submissionTitles, submissionPaths = getSubmissionTitlesAndPaths(gArgs.assignment_dir)

    TidyUpSingleSubdirSubmissionDirs(submissionPaths)

    # run external cmds and write stdout to a file
    outputDir = getOutputDir(gArgs)
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    for i in range(len(submissionTitles)):
        print 'Processing '+submissionTitles[i]+'...'
        submissionPath = submissionPaths[i]
        resultStr = ''

        for cmd in gArgs.cmds:
            resultStr += '===================================\n'
            resultStr += '(cmd: '+cmd+')\n'
            try:
                if os.name=='posix':
                    stdoutStr = subprocess.check_output('cd "%s" && %s'%(toString(submissionPath), cmd), stderr=subprocess.STDOUT, shell=True)
                else:
                    stdoutStr = subprocess.check_output('pushd "%s" && %s && popd'%(toString(submissionPath), cmd), stderr=subprocess.STDOUT, shell=True)
            except subprocess.CalledProcessError as e:
                resultStr += e.output
            else:
                resultStr += stdoutStr

        with open(opjoin(outputDir, submissionTitles[i]+'.txt'), 'w') as f:
            f.write(resultStr)
    
    removeUnzipDirsInAssignDir(gArgs.assignment_dir, unzipDirNames)
    print 'Done.'
