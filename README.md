# PACERs
Programming Assignments Compiling, Executing, and Reporting system

## An example workflow

*1. Collect submitted source files.*
```
<CWD>/test-assignments/c-assignment-2/
    |-student 01.c
    |-student 02.c
    |-student 03.c
```
![example-source](https://cloud.githubusercontent.com/assets/5915359/15735192/82744a64-28d1-11e6-85e6-fa958f96e758.png)

*2. Run PACERs.*  
- On Windows: ```pacers.py test-assignments\c-assignment-2 --user-input "1 2" "3 4"```
- On Linux: ```./pacers.py test-assignments/c-assignment-2 --user-input "1 2" "3 4"```

*3. Open the generated HTML report: ```<CWD>/output/c-assignment-2/report-c-assignment-2.html```*  

Open the generated report with your favorite browser.  

![example-result](https://cloud.githubusercontent.com/assets/5915359/23886079/4e0da5b6-08bb-11e7-8ec2-15ec263a0ff4.png)
You can open the report in MS Word or MS Excel to edit it(to grade each submission).  

## Requirements
- Python 2.x
- CMake
- Pygments  
    Install in Windows - ```pip install pygments```  
    Install in Linux - ```sudo pip install pygments```
- Unidecode  
    Install in Windows - ```pip install unidecode```  
    Install in Linux - ```sudo pip install unidecode```
- Chardet  
    Install in Windows - ```pip install chardet```  
    Install in Linux - ```sudo pip install chardet```

## Required environment setting
- On MS Windows, please add the following paths to the system path. XX.X means your Visual Studio version.  
```
C:\Program Files (x86)\Microsoft Visual Studio XX.X\VC\bin  
C:\Program Files (x86)\Microsoft Visual Studio XX.X\Common7\IDE
```

## Quick start
1) Run: ```git clone https://github.com/yssl/PACERs.git```  
   or Releases > Latest release > Download source code, extract it, and ```cd``` to the extracted directory..

2) On Linux, run: ```./pacers.py test-assignments/c-assignment-1```  
   On Windows, run: ```pacers.py test-assignments\c-assignment-1```

3) Open ```./output/c-assignment-1/report-c-assignment-1.html``` in any web browser.  
The generated html file is written in unicode (utf-8), so if your browser shows broken characters, please change the text encoding option for the page to unicode or utf-8.

## Supported submission types & languages
The type of each submission is auto-detected by PACERs.

| Submission types | Meaning      |
|--------------------------|-------------------------|
| SINGLE_SOURCE_FILE        | Each submission has a single source or resource file and represents a single project (and a program).	 |
| SOURCE_FILES              | Each submission has source or resource files without any kind of project files. A single source file in each submission represents a single project (program).|
| CMAKE_PROJECT             | Each submission has CMakeLists.txt and represents a single project (and a program). |
| VISUAL_CPP_PROJECT        | Each submission has *.vcxproj or *.vcproj and	represents a single project (and a program). |

The tested envirionments for each submission type are shown in the table.

| Submission types | Language | Tested environment      |
|-------------------------|--------------------------|-------------------------|
| SINGLE_SOURCE_FILE or SOURCE_FILES  | C & C++                      | Microsoft Visual Studio 2010 - Windows 10 (Kor)<br> Microsoft Visual C++ 2010 Express - Windows 8.1 with Bing (Eng)<br> gcc 4.8.4 - Ubuntu 14.04 (Kor) |
| SINGLE_SOURCE_FILE or SOURCE_FILES | text file                     | N/A (just showing the text) |    
| CMAKE_PROJECT | C & C++                     | Microsoft Visual Studio 2010 - Windows 10 (Kor) |    
| VISUAL_CPP_PROJECT | C & C++                     | Microsoft Visual Studio 2010 - Windows 10 (Kor) |    

## Try other test-assignments
- C source file
```
./pacers.py test-assignments/c-assignment-1
./pacers.py test-assignments/c-assignment-2 --user-input "3 5"
./pacers.py test-assignments/c-assignment-2 --user-input "1 2" "3 4"
./pacers.py test-assignments/c-assignment-3 --user-input "2 5" "10 20"
./pacers.py test-assignments/c-assignment-4 --user-input "2 5" "10 20"
```
- text file
```
./pacers.py test-assignments/txt-assignment-1
```
- CMake project
```
./pacers.py test-assignments/cmake-assignment-1
```
- Visual C++ project (Windows only)
```
./pacers.py test-assignments/vcxproj-assignment-1
```
- Visual C++ GUI project (Windows only)
```
./pacers.py test-assignments/vcxproj-GUI-assignment-1 --timeout 0 --exclude-patterns SDL2-2.0.4/*
```
You can run all test-assignments at once by the run-test-assignments script.
- On Windows: ```run-test-assignments.bat```
- On Linux: ```./run-test-assignments.sh```

<!--
If you checked all the test-assignments are working correctly in your PC, please let me know your tested language, compiler, and OS by submitting an issues on this project so that I could update the "Tested language, compiler(or interpreter), OS" section in this page :).
-->

## Usage
```
usage: pacers.py [-h] [--user-input USER_INPUT [USER_INPUT ...]]
                 [--timeout TIMEOUT] [--run-only] [--build-only]
                 [--run-serial] [--build-serial] [--run-only-serial]
                 [--num-cores NUM_CORES] [--no-report]
                 [--exclude-patterns EXCLUDE_PATTERNS [EXCLUDE_PATTERNS ...]]
                 [--assignment-alias ASSIGNMENT_ALIAS]
                 [--output-dir OUTPUT_DIR]
                 assignment_dir

Programming Assignments Compiling, Executing, and Reporting system

positional arguments:
  assignment_dir        A direcory that has submissions.
                        The type of each submission is auto-detected by PACERs.

                        | Submission types   | Meaning                                               |
                        |--------------------|-------------------------------------------------------|
                        | SINGLE_SOURCE_FILE | Each submission has a single source or resource file  |
                        |                    | and represents a single project (and a program).      |
                        |--------------------|-------------------------------------------------------|
                        | SOURCE_FILES       | Each submission has source or resource files without  |
                        |                    | any kind of project files. A single source file in    |
                        |                    | each submission represents a single project (program).|
                        |--------------------|-------------------------------------------------------|
                        | CMAKE_PROJECT      | Each submission has CMakeLists.txt and represents     |
                        |                    | a single project (and a program).                     |
                        |--------------------|-------------------------------------------------------|
                        | VISUAL_CPP_PROJECT | Each submission has *.vcxproj or *.vcproj and         |
                        |                    | represents a single project (and a program).          |

                        Each submission can have only one source file, or a zip file
                        or a directory including many files.

optional arguments:
  -h, --help            show this help message and exit
  --user-input USER_INPUT [USER_INPUT ...]
                        Specify USER_INPUT to be sent to the stdin of target
                        programs. This option should be located after
                        assignment_dir if no other optional arguments are
                        given. Two types of user input are available.
                        default is an empty string.

                        | Type     | Example                  | Example's meaning                          |
                        |----------|--------------------------|--------------------------------------------|
                        | Single   | --user-input 15          | run each program with input 15             |
                        | value    | --user-input "hello"     | run each program with input "hello"        |
                        |          | --user-input "1 2"       | run each program with input "1 2"          |
                        |----------|--------------------------|--------------------------------------------|
                        | Multiple | --user-input 1 2 3       | run each program 3 times: with 1, 2, 3     |
                        | values   | --user-input "1 2" "3 4" | run each program 2 times: with "1 2", "3 4"|

  --timeout TIMEOUT     Each target program is killed when TIMEOUT(seconds)
                        is reached. Useful for infinite loop cases.
                        Setting zero seconds(--timeout 0) means unlimited execution time
                        for each target program, which can be useful for GUI applications.
                        default: 2.0
  --run-only            When specified, run each target program without build.
                        You may use it when you want change USER_INPUT without
                        build. if the programming language of source files
                        does not require build process, PACERs
                        automatically skips the build process without
                        specifying this option.
  --build-only          When specified, build each target program without running.
  --run-serial          When specified, run each target program in serial.
                        PACERs runs programs in parallel by default.
  --build-serial        When specified, build each target program in serial.
                        PACERs builds programs in parallel by default.
  --run-only-serial     Shortcut for --run-only --run-serial.
  --num-cores NUM_CORES
                        Specify number of cpu cores used in building and running process.
                        default: number of cpu cores in your machine.
  --no-report           When specified, the final report is not generated.
  --exclude-patterns EXCLUDE_PATTERNS [EXCLUDE_PATTERNS ...]
                        Files containing EXCLUDE_PATTERNS in their relative path
                        from each submission directory are excluded from the final report.
                        (Submission dir: 'student01' in 'test-assignments/c-assignment-4')
                        For example, use "--exclude-pattern *.txt foo/*"
                        to exclude all txt files and all files in foo directory
                        in each submission directory from the final report.
  --assignment-alias ASSIGNMENT_ALIAS
                        Specify ASSIGNMENT_ALIAS for each assignment_dir.
                        ASSIGNMENT_ALIAS is used when making a sub-directory
                        in OUTPUT_DIR and the final report file.
                        default: "basename" of assignment_dir (bar if
                        assignment_dir is /foo/bar/).
  --output-dir OUTPUT_DIR
                        Specify OUTPUT_DIR in which the final report file
                        and build output files to be generated.
                        Avoid including hangul characters in its full path.
                        default: .\output
```
