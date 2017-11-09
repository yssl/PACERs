################################################################################
# submission.py

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
import glob
from global_const import *
from unicode import *

def getSubmissionTitlesAndPaths(assignment_dir):
    submissionTitles = []
    submissionPaths = []
    for name in os.listdir(assignment_dir):
        # to exclude .zip files - submissionTitle will be from unzipDirNames by unzipInAssignDir() in assignment_dir
        if not os.path.isdir(opjoin(assignment_dir, name)) and os.path.splitext(name)[1].lower()=='.zip':
            continue
        submissionTitles.append(name)
        submissionPaths.append(opjoin(assignment_dir, name))
    return submissionTitles, submissionPaths

def detectSubmissionType(submissionPath):
    if os.path.isdir(submissionPath):
        # print 'dir'
        for submissionType in range(BEGIN_SUBMISSION_TYPE+1, END_SUBMISSION_TYPE):
            for pattern in gSubmissionPatterns[submissionType]:
                # Convert paths for glob to byte string only for posix os (due to python bug?)
                if os.name=='posix':
                    if len(glob.glob(toString(opjoin(submissionPath, pattern)))) > 0:
                        return submissionType
                else:
                    if len(glob.glob(opjoin(submissionPath, pattern))) > 0:
                        return submissionType
        return SOURCE_FILES
    else:
        # print 'file'
        return SINGLE_SOURCE_FILE


