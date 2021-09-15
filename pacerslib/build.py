################################################################################
# build.py

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
import os, subprocess, glob, shutil
from global_const import *
from unicode import *

def buildOneProj(projInfo):
    submissionType = projInfo['submissionType']
    projName = projInfo['projName']
    submissionDir = projInfo['submissionDir']
    filesInProj = projInfo['filesInProj']

    buildRetCode, buildLog, buildVersion = buildProj(submissionType, submissionDir, projName, filesInProj)

    return buildRetCode, buildLog, buildVersion

############################################
# build functions
# return buildRetCode, buildLog, buildVersion
# buildRetCode:
#   -1 - build failed due to internal error, not because build error (not supported extension, etc)
#   0 - build succeeded
#   else - build failed due to build error
# buildVersion:
#   cmake-version
#   visual-cpp-version

def buildProj(submissionType, submissionDir, projName, projSrcFileNames):
    if submissionType==SINGLE_SOURCE_FILE or submissionType==SOURCE_FILES:
        buildRetCode, buildLog, buildVersion = build_single_source(submissionDir, projName, projSrcFileNames[0])
    elif submissionType==CMAKE_PROJECT:
        buildRetCode, buildLog, buildVersion = build_cmake(submissionDir, projName)
    elif submissionType==MAKE_PROJECT:
        buildRetCode, buildLog, buildVersion = build_make(submissionDir, projName)
    elif submissionType==VISUAL_CPP_PROJECT:
        buildRetCode, buildLog, buildVersion = build_vcxproj(submissionDir, projName)
    return buildRetCode, buildLog, buildVersion

####
# build_single functions
def build_single_source(srcRootDir, projName, singleSrcFileName):
    extension = os.path.splitext(singleSrcFileName)[1].lower()
    if extension in gSourceExt:
        build_single_func = eval(gSourceExt[extension]['build-single-source-func'])
    else:
        build_single_func = build_single_else
    return build_single_func(srcRootDir, projName, singleSrcFileName)

def build_single_c_cpp(srcRootDir, projName, singleSrcFileName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    try:
        os.makedirs(buildDir)
    except Exception as e:
        return -1, toUnicode(str(e)), 'cmake-version'

    makeCMakeLists_single_c_cpp(projName, singleSrcFileName, buildDir)

    return __build_cmake(buildDir, './')

def build_single_py(srcRootDir, projName, singleSrcFileName):
    return 0, '', 'python-version'

def build_single_else(srcRootDir, projName, singleSrcFileName):
    extension = os.path.splitext(singleSrcFileName)[1].lower()
    errorMsg = u'Building %s is not supported.'%extension
    return -1, errorMsg, 'no-build-version'

####
# build_cmake functions
def build_cmake(srcRootDir, projName):
    #############
    # delete CMake intermediate output files if submitted
    file_CMakeCache = opjoin(srcRootDir, 'CMakeCache.txt')
    file_cmake_install = opjoin(srcRootDir, 'cmake_install.cmake')
    file_Makefile = opjoin(srcRootDir, 'Makefile')
    intermediate_files = [file_CMakeCache, file_cmake_install, file_Makefile]
    for fpath in intermediate_files:
        if os.path.isfile(fpath):
            os.remove(fpath)

    dir_CMakeFiles = opjoin(srcRootDir, 'CMakeFiles')
    if os.path.isdir(dir_CMakeFiles):
        shutil.rmtree(dir_CMakeFiles)
    #############

    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    try:
        os.makedirs(buildDir)
    except Exception as e:
        return -1, toUnicode(str(e)), 'cmake-version'
    return __build_cmake(buildDir, '../')

def __build_cmake(buildDir, cmakeLocationFromBuildDir):
    try:
        if os.name=='posix':
            buildLog = toUnicode(subprocess.check_output('cd "%s" && %s'%(toString(buildDir), toString(gOSEnv[os.name]['cmake-cmd'](cmakeLocationFromBuildDir))), stderr=subprocess.STDOUT, shell=True))
        else:
            buildLog = toUnicode(subprocess.check_output('pushd "%s" && %s && popd'%(toString(buildDir), toString(gOSEnv[os.name]['cmake-cmd'](cmakeLocationFromBuildDir))), stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e:
        return e.returncode, toUnicode(e.output), 'cmake-version'
    else:
        return 0, buildLog, 'cmake-version'

####
# build_make functions
def build_make(srcRootDir, projName):
    buildDir = opjoin(srcRootDir, gBuildDirPrefix+projName)
    try:
        # copy all copied files in output source dir(output/assigndir) to output build dir(output/assigndir/pacers-assigndir)
        # because there is no way to set the output destination for a Makefile, unlike CMake.
        shutil.copytree(srcRootDir, buildDir)
    except Exception as e:
        return -1, toUnicode(str(e)), 'make-version'
    return __build_make(buildDir, '../')

def __build_make(buildDir, makeLocationFromBuildDir):
    try:
        if os.name=='posix':
            buildLog = toUnicode(subprocess.check_output('cd "%s" && %s'%(toString(buildDir), 'make'), stderr=subprocess.STDOUT, shell=True))
        else:
            return -1, 'MAKE_PROJECT is not supported on Windows', 'make-version'
    except subprocess.CalledProcessError as e:
        return e.returncode, toUnicode(e.output), 'make-version'
    else:
        return 0, buildLog, 'make-version'

# return CMakeLists.txt code
def makeCMakeLists_single_c_cpp(projName, singleSrcFileName, buildDir):
    code = u''
    code += 'cmake_minimum_required(VERSION 2.6)\n'
    code += 'project(%s)\n'%projName
    code += 'add_executable(%s '%projName
    code += '../%s'%singleSrcFileName
    code += ')\n'

    with open(opjoin(buildDir,'CMakeLists.txt'), 'w') as f:
        f.write(toString(code))

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
        errorMsg = u'Cannot find .vcxproj or .vcproj file.'
        return -1, errorMsg 

    try:
        # print 'vcvars32.bat && msbuild.exe "%s" /property:OutDir="%s/";IntDir="%s/"'\
                # %(vcxprojNames[0], gBuildDirPrefix+projName, gBuildDirPrefix+projName)
        buildLog = toUnicode(subprocess.check_output('vcvars32.bat && msbuild.exe "%s" /property:OutDir="%s/";IntDir="%s/"'
                %(toString(vcxprojNames[0]), toString(gBuildDirPrefix+projName), toString(gBuildDirPrefix+projName)),
                stderr=subprocess.STDOUT, shell=True))
    except subprocess.CalledProcessError as e:
        return e.returncode, toUnicode(e.output), 'visual-cpp-version'
    else:
        return 0, buildLog, 'visual-cpp-version'


