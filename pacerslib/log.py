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
    userInputs = projInfo['userInputs']

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
    userInputs = projInfo['userInputs']

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
    userInputs = projInfo['userInputs']

    logPrefix = getProjLogPrefix(processedCount, numAllProjs, submissionIndex, submissionTitle, submissionType, projIndex, projName, numProjInSubmission)

    print '%s Starting execution...'%logPrefix


