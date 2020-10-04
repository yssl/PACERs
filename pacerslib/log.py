################################################################################
# log.py

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
from global_const import *

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
    stdInputs = projInfo['stdInputs']

    logPrefix = getProjLogPrefix(processedCount, numAllProjs, submissionIndex, submissionTitle, submissionType, projIndex, projName, numProjInSubmission)

    if buildRetCode==0:
        print '%s Build succeeded.'%logPrefix
    elif buildRetCode==-1:
        print '%s Build failed. %s'%(logPrefix, buildLog)
    else:
        print '%s Build failed. A build error occurred.'%logPrefix

def printBuildStart(processedCount, numAllProjs, projInfo):
    submissionIndex = projInfo['submissionIndex']
    submissionTitle = projInfo['submissionTitle']
    submissionType = projInfo['submissionType']
    numSubmission = projInfo['numSubmission']
    projIndex = projInfo['projIndex']
    numProjInSubmission = projInfo['numProjInSubmission']
    projName = projInfo['projName']
    submissionDir = projInfo['submissionDir']
    filesInProj = projInfo['filesInProj']
    stdInputs = projInfo['stdInputs']

    logPrefix = getProjLogPrefix(processedCount, numAllProjs, submissionIndex, submissionTitle, submissionType, projIndex, projName, numProjInSubmission)

    print '%s Starting build...'%logPrefix

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
    stdInputs = projInfo['stdInputs']

    logPrefix = getProjLogPrefix(processedCount, numAllProjs, submissionIndex, submissionTitle, submissionType, projIndex, projName, numProjInSubmission)

    if exitTypeList[0]==0:
        print '%s Execution terminated.'%logPrefix
    elif exitTypeList[0]==-1:
        print '%s Execution failed. %s'%(logPrefix, stdoutStrList[0])
    elif exitTypeList[0]==1:
        print '%s Execution was stopped due to timeout.'%logPrefix
    else:
        raise NotImplementedError

def printRunStart(processedCount, numAllProjs, projInfo):
    submissionIndex = projInfo['submissionIndex']
    submissionTitle = projInfo['submissionTitle']
    submissionType = projInfo['submissionType']
    numSubmission = projInfo['numSubmission']
    projIndex = projInfo['projIndex']
    numProjInSubmission = projInfo['numProjInSubmission']
    projName = projInfo['projName']
    submissionDir = projInfo['submissionDir']
    filesInProj = projInfo['filesInProj']
    stdInputs = projInfo['stdInputs']

    logPrefix = getProjLogPrefix(processedCount, numAllProjs, submissionIndex, submissionTitle, submissionType, projIndex, projName, numProjInSubmission)

    print '%s Starting execution...'%logPrefix


