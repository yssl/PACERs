from version import *

############################################
# submission type
BEGIN_SUBMISSION_TYPE = 0
CMAKE_PROJECT         = 1
VISUAL_CPP_PROJECT    = 2
SOURCE_FILES          = 3
SINGLE_SOURCE_FILE    = 4
END_SUBMISSION_TYPE   = 5

gLogPrefix = '# '
gBuildDirPrefix = 'pacers-build-'

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

gVersionDescription                        = {}
gVersionDescription['cmake-version']       = 'CMake & C/C++ compiler'
gVersionDescription['visual-cpp-version']  = 'Visual C/C++ compiler'

############################################
# gSourceExt
gSourceExt = {'.c':{}, '.cpp':{}}

gSourceExt['.c']['build-single-source-func'] = 'build_single_c_cpp'
gSourceExt['.c']['runcmd-single-source-func'] = 'runcmd_single_c_cpp'
gSourceExt['.c']['runcwd-single-source-func'] = 'runcwd_single_c_cpp'

gSourceExt['.cpp']['build-single-source-func'] = 'build_single_c_cpp'
gSourceExt['.cpp']['runcmd-single-source-func'] = 'runcmd_single_c_cpp'
gSourceExt['.cpp']['runcwd-single-source-func'] = 'runcwd_single_c_cpp'

############################################
# gOSEnv
gOSEnv = {'nt':{}, 'posix':{}}

gOSEnv['nt']['cmake-cmd'] = lambda cmakeLocationFromBuildDir: 'vcvars32.bat && cmake %s -G "NMake Makefiles" && nmake'%cmakeLocationFromBuildDir
gOSEnv['posix']['cmake-cmd'] = lambda cmakeLocationFromBuildDir: 'cmake %s && make'%cmakeLocationFromBuildDir

gOSEnv['nt']['cmake-version'] = 'getCMakeVersionWindows'
gOSEnv['posix']['cmake-version'] = 'getCMakeVersionPosix'
gOSEnv['nt']['visual-cpp-version'] = 'getVisulCppVersionWindows'
gOSEnv['posix']['visual-cpp-version'] = '''lambda: ['No Visual C/C++ compiler available in this platform.']'''


