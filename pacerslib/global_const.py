################################################################################
# global_const.py

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
from version import *

############################################
# submission type
BEGIN_SUBMISSION_TYPE = 0
CMAKE_PROJECT         = 1
VISUAL_CPP_PROJECT    = 2
MAKE_PROJECT          = 3
SOURCE_FILES          = 4
SINGLE_SOURCE_FILE    = 5
END_SUBMISSION_TYPE   = 6

gLogPrefix = '# '
gBuildDirPrefix = 'pacers-build-'

gSubmissionTypeDescrption                        = {}
gSubmissionTypeDescrption[CMAKE_PROJECT]         = 'CMAKE_PROJECT - the submission has CMakeLists.txt.'
gSubmissionTypeDescrption[MAKE_PROJECT]          = 'MAKE_PROJECT - the submission has Makefile.'
gSubmissionTypeDescrption[VISUAL_CPP_PROJECT]    = 'VISUAL_CPP_PROJECT - the submission has .vcxproj or .vcproj.'
gSubmissionTypeDescrption[SOURCE_FILES]          = 'SOURCE_FILES - the submission has source or resource files without any project files.'
gSubmissionTypeDescrption[SINGLE_SOURCE_FILE]    = 'SINGLE_SOURCE_FILE - the submission has a single source or resource file.'

gSubmissionTypeName                        = {}
gSubmissionTypeName[CMAKE_PROJECT]         = 'CMAKE_PROJECT'
gSubmissionTypeName[MAKE_PROJECT]          = 'MAKE_PROJECT'
gSubmissionTypeName[VISUAL_CPP_PROJECT]    = 'VISUAL_CPP_PROJECT'
gSubmissionTypeName[SOURCE_FILES]          = 'SOURCE_FILES'
gSubmissionTypeName[SINGLE_SOURCE_FILE]    = 'SINGLE_SOURCE_FILE'

gSubmissionPatterns                        = {}
gSubmissionPatterns[CMAKE_PROJECT]         = ['CMakeLists.txt']
gSubmissionPatterns[MAKE_PROJECT]          = ['Makefile', 'makefile']
gSubmissionPatterns[VISUAL_CPP_PROJECT]    = ['*.vcxproj', '*.vcproj']
gSubmissionPatterns[SOURCE_FILES]          = ['*']
gSubmissionPatterns[SINGLE_SOURCE_FILE]    = ['*']

gExcludePatterns                           = {}
gExcludePatterns[CMAKE_PROJECT]            = ['Makefile', 'CMakeCache.txt', 'cmake_install.cmake', 'CMakeFiles/*']
gExcludePatterns[MAKE_PROJECT]             = []
gExcludePatterns[VISUAL_CPP_PROJECT]       = []
gExcludePatterns[SOURCE_FILES]             = []
gExcludePatterns[SINGLE_SOURCE_FILE]       = []

gVersionDescription                        = {}
gVersionDescription['cmake-version']       = 'CMake & C/C++ compiler'
gVersionDescription['make-version']        = 'Make & C/C++ compiler'
gVersionDescription['visual-cpp-version']  = 'Visual C/C++ compiler'
gVersionDescription['python-version']      = 'Python'

############################################
# gSourceExt - used only for build & run single source
gSourceExt = {'.c':{}, '.cpp':{}, '.cc':{}, '.cxx':{}, '.c++':{}, '.py':{}}

gSourceExt['.c']['build-single-source-func'] = 'build_single_c_cpp'
gSourceExt['.c']['runcmd-single-source-func'] = 'runcmd_single_c_cpp'
gSourceExt['.c']['runcwd-single-source-func'] = 'runcwd_single_c_cpp'
gSourceExt['.c']['default-interpreter-cmd'] = ''
gSourceExt['.cpp'] = gSourceExt['.c']
gSourceExt['.cc'] = gSourceExt['.c']
gSourceExt['.cxx'] = gSourceExt['.c']
gSourceExt['.c++'] = gSourceExt['.c']

gSourceExt['.py']['build-single-source-func'] = 'build_single_py'
gSourceExt['.py']['runcmd-single-source-func'] = 'runcmd_single_py'
gSourceExt['.py']['runcwd-single-source-func'] = 'runcwd_single_py'
gSourceExt['.py']['default-interpreter-cmd'] = 'python'

############################################
# gOSEnv
gOSEnv = {'nt':{}, 'posix':{}}

gOSEnv['nt']['cmake-cmd'] = lambda cmakeLocationFromBuildDir: 'vcvars32.bat && cmake %s -G "NMake Makefiles" && nmake'%cmakeLocationFromBuildDir
gOSEnv['posix']['cmake-cmd'] = lambda cmakeLocationFromBuildDir: 'cmake %s && make'%cmakeLocationFromBuildDir

# # for debugging
# gOSEnv['posix']['cmake-cmd'] = lambda cmakeLocationFromBuildDir: 'cmake %s && make VERBOSE=1'%cmakeLocationFromBuildDir

gOSEnv['nt']['cmake-version'] = 'getCMakeVersionWindows'
gOSEnv['posix']['cmake-version'] = 'getCMakeVersionPosix'
gOSEnv['nt']['make-version'] = 'getMakeVersionWindows'
gOSEnv['posix']['make-version'] = 'getMakeVersionPosix'
gOSEnv['nt']['visual-cpp-version'] = 'getVisulCppVersionWindows'
gOSEnv['posix']['visual-cpp-version'] = '''lambda: ['No Visual C/C++ compiler available in this platform.']'''
gOSEnv['nt']['python-version'] = 'getPythonVersion'
gOSEnv['posix']['python-version'] = 'getPythonVersion'


