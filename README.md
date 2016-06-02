# PACERs
Programming Assignments Compiling, Executing, and Reporting system

## An example workflow

*1. Collect submitted source files.*
```
<CWD>/test-assignments/C/assignment-2/
    |-student 01.c
    |-student 02.c
    |-student 03.c
```
![example-source](https://cloud.githubusercontent.com/assets/5915359/15735192/82744a64-28d1-11e6-85e6-fa958f96e758.png)

*2. Run PACERs.*
```
pacers.py test-assignments\C\assignment-2 --user-input "1 2" "3 4"
```

*3. Open the generated HTML report: ```<CWD>/output/assignment-2/report-assignment-2.html```*  
You can open the report in MS Word or MS Excel to grade each submission.  
![example-result](https://cloud.githubusercontent.com/assets/5915359/15764368/4ec64f70-2965-11e6-8815-ba521d3a2c0b.png)

## Requirements
- python 2.x
- cmake
- Pygments  
    Install in Windows - ```pip install pygments```  
    Install in Linux - ```sudo pip install pygments``` or ```sudo apt-get install python-pygments```
- Unidecode (install via pip install unidecode)  
    Install in Windows - ```pip install unidecode```  
    Install in Linux - ```sudo pip install unidecode``` or ```sudo apt-get install python-unidecode```

## Required environment setting
- On MS Windows, please add the following paths to the system path. XX.X means your Visual Studio version.  
```
C:\Program Files (x86)\Microsoft Visual Studio XX.X\VC\bin  
C:\Program Files (x86)\Microsoft Visual Studio XX.X\Common7\IDE
```

## Quick start
1) Run: ```git clone https://github.com/yssl/PACERs.git```

2) On Linux, run: ```./pacers.py test-assignments/C/assignment-1```  
   On Windows, run: ```pacers.py test-assignments\C\assignment-1```

3) Open ```./output/assignment-1/report-assignment-1.html``` in any web browser.  
The generated html file is written in unicode (utf-8), so if your browser shows broken characters, please try to change the text encoding option for the page to unicode or utf-8.
    
## Tested language, compiler(or interpreter), OS
- C - Microsoft Visual Studio 2010 - Windows 10 (Kor)
- C - Microsoft Visual C++ 2010 Express - Windows 8.1 with Bing (Eng)
- C - gcc 4.8.4 - Ubuntu 14.04 (Kor)

Currently, only C and C++ are supported.

## Try other test-assignment files
- C
```
pacers.py test-assignments/C/assignment-1
pacers.py test-assignments/C/assignment-2 --user-input "3 5"
pacers.py test-assignments/C/assignment-2 --user-input "1 2" "3 4"
pacers.py test-assignments/C/assignment-3 --user-dict "{'1':[''], '2':['2 5', '10 20']}"
pacers.py test-assignments/C/assignment-4 --user-dict "{'1':[''], '2':['2 5', '10 20']}"
```

If you checked all the test-assignments are working correctly in your PC, please let me know your tested language, compiler, and OS by submitting an issues on this project so that I could update the "Tested language, compiler(or interpreter), OS" section in this page :).

## Usage
```
usage: pacers.py [-h] [--user-input USER_INPUT [USER_INPUT ...]]
                 [--user-dict USER_DICT] [--timeout TIMEOUT] [--run-only]
                 [--assignment-alias ASSIGNMENT_ALIAS]
                 [--output-dir OUTPUT_DIR] [--source-encoding SOURCE_ENCODING]
                 assignment_dir

Programming Assignments Compiling, Executing, and Reporting system

positional arguments:
  assignment_dir        A direcory that has submitted files.
                        In assignment_dir, one source file runs one program.
                        Each submission might have only one source file or a
                        zip file or a directory including multiple source files

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
                        | Single   | --user-input 15          | run each source file with input 15         |
                        | value    | --user-input "hello"     | run each source file with input "hello"    |
                        |          | --user-input "1 2"       | run each source file with input "1 2"      |
                        |----------|--------------------------|--------------------------------------------|
                        | Multiple | --user-input 1 2 3       | run each source 3 times: with 1, 2, 3      |
                        | values   | --user-input "1 2" "3 4" | run each source 2 times: with "1 2", "3 4" |

  --user-dict USER_DICT
                        Specify USER_DICT to be sent to the stdin of target
                        programs. Argument should be python dictionary
                        representation. Each 'key' of the dictionary item
                        is 'suffix' that should match with the last parts of
                        each source file name. 'value' is user input for
                        those matched source files.
                        If both --user-input and --user-dict are specified,
                        only --user-dict is used.

                        Example:
                        --user-dict {'1':['1','2'], '2':['2,'5','7']}

                        runs a source file whose name ends with '1'
                        (e.g. prob1.c) 2 times (with '10', '20')
                        and run a source file whose name ends with
                        '2' (e.g. prob2.c) 3 times (with '2','5','7').

  --timeout TIMEOUT     Each target program is killed when TIMEOUT(seconds)
                        is reached. Useful for infinite loop cases.
                        default: 2.0
  --run-only            When specified, run each target program without build.
                        You may use it when you want change USER_INPUT without
                        build. if the programming language of source files
                        does not require build process, PACERs
                        automatically skips the build process without
                        specifying this option.
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
  --source-encoding SOURCE_ENCODING
                        Specify SOURCE_ENCODING in which source files
                        are encoded. You don't need to use this option if
                        source code only has english characters or
                        the platform where source code is written and
                        the platform PACERs is running is same.
                        If source files are written in another platform,
                        you might need to specify default encoding for
                        the platform to run PACERs correctly.
                        default: system default encoding
```
