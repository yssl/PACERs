# CoassignViewer
Automatic building & launching & reporting system for a large number of coding assignment files.

## Requirements
- python 2.x
- cmake
- Pygments  
    Install in Windows - ```pip install pygments```  
    Install in Linux - ```sudo pip install pygments``` or ```sudo apt-get install python-pygments```
- Unidecode (install via pip install unidecode)  
    Install in Windows - ```pip install unidecode```  
    Install in Linux - ```sudo pip install unidecode``` or ```sudo apt-get install python-unidecode```

## Tested language, compiler(interpreter), platform
- C - Microsoft Visual Studio 2010 - Windows 10 (Kor)
- C - Microsoft Visual C++ 2010 Express - Windows 8.1 with Bing (Eng)
- C - gcc 4.8.4 - Ubuntu 14.04 (Kor)

## Required environment setting
- On MS Windows, please add following paths to the system path. XX.X means your Visual Studio version.  
```
C:\Program Files (x86)\Microsoft Visual Studio XX.X\VC\bin  
C:\Program Files (x86)\Microsoft Visual Studio XX.X\Common7\IDE
```

## Quick start
1) Run: ```git clone https://github.com/yssl/CoassignViewer.git```

2) On Linux, run: ```./coassign-viewer.py test-assignment-1```  
   On Windows, run: ```coassign-viewer.py test-assignment-1```

3) Open ./output/test-assignment-1/report-test-assignment-1.html in any web browser.  
The generated html file is written in unicode (utf-8), so if your browser shows broken characters, please try to change the text encoding option for the page to unicode or utf-8.
    
## Other examples
```
coassign-viewer.py --user-input "1 2" test-assignment-2
```

## Usage
```
usage: coassign-viewer.py [-h] [--user-input USER_INPUT]
                          [--file-layout FILE_LAYOUT] [--timeout TIMEOUT]
                          [--run-only] [--assignment-alias ASSIGNMENT_ALIAS]
                          [--output-dir OUTPUT_DIR]
                          [--source-encoding SOURCE_ENCODING]
                          assignment_dir

Automatic building & launching & reporting system for a large number of coding assignment files.

positional arguments:
  assignment_dir        a direcory that has submitted files. 

optional arguments:
  -h, --help            show this help message and exit
  --user-input USER_INPUT
                        specify USER_INPUT to be sent to the stdin of the 
                        target programs. 
                        default is an empty string.
  --file-layout FILE_LAYOUT
                        indicates file layout in the assignment_dir. 
                        default: 0
                        0 - one source file runs one program. 
                        each submission might have only one source file or a 
                        zip file or a directory including multiple source files.
  --timeout TIMEOUT     each target program is killed when TIMEOUT(seconds) 
                        is reached. useful for infinite loop cases. 
                        default: 2.0
  --run-only            when specified, run each target program without build. 
                        you may use it when you want change USER_INPUT without
                        build. if the programming language of source files 
                        does not require build process, CoassignViewer 
                        automatically skips the build process without 
                        specifying this option.
  --assignment-alias ASSIGNMENT_ALIAS
                        specify ASSIGNMENT_ALIAS for each assignment_dir. 
                        ASSIGNMENT_ALIAS is used when making a sub-directory 
                        in OUTPUT_DIR and the final report file. 
                        default: "basename" of assignment_dir (bar if 
                        assignment_dir is /foo/bar/).
  --output-dir OUTPUT_DIR
                        specify OUTPUT_DIR in which the final report file 
                        and build output files to be generated. 
                        avoid including hangul characters in its full path.
                        default: ./output
  --source-encoding SOURCE_ENCODING
                        specify SOURCE_ENCODING in which source files 
                        are encoded. You don't need to use this option if
                        source code only has english characters or 
                        the platform where source code is written and 
                        the platform CoassignViewer is running is same. 
                        If source files are written in another platform, 
                        you might need to specify default encoding for 
                        the platform to run CoassignViewer correctly. 
                        default: system default encoding
```
