import os, platform, urllib, shutil
import pygments
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter
from pygments.lexers.special import TextLexer
from global_const import *

############################################
# report functions
def generateReport(args, submittedFileNames, srcFileLists, buildRetCodes, buildLogs, exitTypeLists, stdoutStrLists, userInputLists, submissionTypes, buildVersionSet):

    cssCode = HtmlFormatter().get_style_defs()

    cssCode += u'''
pre {
    white-space: pre-wrap;       /* Since CSS 2.1 */
    white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
    white-space: -pre-wrap;      /* Opera 4-6 */
    white-space: -o-pre-wrap;    /* Opera 7 */
    word-wrap: break-word;       /* Internet Explorer 5.5+ */
}

table.type08 {
    border-collapse: collapse;
    text-align: left;
    line-height: 1.5;
    border-left: 1px solid #ccc;
    margin: 20px 10px;
}

table.type08 thead th {
    padding: 10px;
    font-weight: bold;
    border-top: 1px solid #ccc;
    border-right: 1px solid #ccc;
    border-bottom: 2px solid #c00;
    background: #dcdcd1;
}
table.type08 tbody th {
    /*width: 150px;*/
    padding: 10px;
    font-weight: bold;
    vertical-align: top;
    border-right: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
    background: #ececec;
}
table.type08 td {
    /*width: 350px;*/
    padding: 10px;
    vertical-align: top;
    border-right: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
}

table.type04 {
    border-collapse: collapse;
    /*border-collapse: separate;*/
    /*border-spacing: 1px;*/
    text-align: left;
    line-height: 1.5;
    border-top: 1px solid #ccc;
  margin : 20px 10px;
}
table.type04 thead th {
    padding: 10px;
    font-weight: bold;
    border-top: 1px solid #ccc;
    border-right: 1px solid #ccc;
    border-bottom: 2px solid #c00;
    background: #dcdcd1;
}
table.type04 tbody th {
    padding: 10px;
    font-weight: bold;
    vertical-align: top;
    border-bottom: 1px solid #ccc;
}
table.type04 td {
    padding: 10px;
    vertical-align: top;
    border-bottom: 1px solid #ccc;
}
'''

    htmlCode = u''

    # header
    htmlCode += '''<html>
    <head>
    <title>%s - PACERs Assignment Report</title>
    <style type="text/css">
    %s
    </style>
    </head>
    <body>
    <h2>%s - PACERs Assignment Report</h2>'''%(args.assignment_alias, cssCode, args.assignment_alias)

    # system information
    htmlCode += '''<table class="type04">
    <thead>
    <tr><th colspan=2>System Information</th></tr>
    </thead>

    <tbody>
    <tr><th>Operating system</th> <td>%s</td></tr>'''%(platform.platform())

    for buildVersion in buildVersionSet:
        if buildVersion != 'no-build-version':
            htmlCode +='<tr><th>%s</th><td>'%gVersionDescription[buildVersion]
            for versionText in eval(gOSEnv[os.name][buildVersion])():
                htmlCode +='%s<br>'%versionText
            htmlCode +='</td></tr>'

    htmlCode += '''</tbody>
    </table>'''

    # pacers options
    htmlCode += '''<table class="type04">
    <thead>
    <tr><th colspan=2>PACERs Options</th></tr>
    </thead>

    <tbody>
    <tr><th>Assignment directory</th> <td>%s</td></tr>
    <tr><th>Output directory</th> <td>%s</td></tr>
    <tr><th>User input</th> <td>%s</td></tr>
    <!--<tr><th>User dict</th> <td>%s</td></tr>-->
    <tr><th>Timeout</th> <td>%f</td></tr>
    <tr><th>Run only</th> <td>%s</td></tr>
    <tr><th>Build only</th> <td>%s</td></tr>
    </tbody>
    </table>'''%(os.path.abspath(args.assignment_dir), opjoin(os.path.abspath(args.output_dir), unidecode(args.assignment_alias)), 
        args.user_input, args.user_dict, args.timeout, 'true' if args.run_only else 'false', 'true' if args.build_only else 'false')

    # main table
    htmlCode += '''
    <!--'Source Files' means the relative path of each source file from the assignment directory.-->
    <table class="type08">
    <thead>
    <tr>
    <th>Submission Title<br>(Submission Type)</th>
    <th>Source Files</th>
    <th>Output</th>
    <th>Score</th>
    <th>Comment</th>
    </tr>
    </thead>'''

    htmlCode += '<tbody>\n'

    for i in range(len(submittedFileNames)):
        htmlCode += '<tr>\n'
        htmlCode += '<th>%s<br>(%s)</th>\n'%(submittedFileNames[i], gSubmissionTypeName[submissionTypes[i]])
        htmlCode += '<td>%s</td>\n'%getSourcesTable(srcFileLists[i], args.assignment_dir, args.output_dir, args.assignment_alias)
        htmlCode += '<td>%s</td>\n'%getOutput(buildRetCodes[i], buildLogs[i], userInputLists[i], exitTypeLists[i], stdoutStrLists[i])
        htmlCode += '<td>%s</td>\n'%''
        htmlCode += '<td>%s</td>\n'%''
        htmlCode += '</tr>\n'

    htmlCode += '</tbody>\n'
    htmlCode += '</table>\n'

    # footer
    htmlCode += '''</body>
    </html>'''

    # write html
    with open(getReportFilePath(args), 'w') as f:
        f.write(htmlCode.encode('utf-8'))
        
def getReportFilePath(args):
    return opjoin(opjoin(args.output_dir, unidecode(args.assignment_alias)),'report-%s.html'%args.assignment_alias)

def getReportResourceDir(output_dir, assignment_alias):
    return opjoin(opjoin(output_dir, unidecode(assignment_alias)),'report-%s'%assignment_alias)

def getSourcesTable(srcPaths, assignment_dir, output_dir, assignment_alias):
    renderedSrcPaths = []
    renderedSource = []
    failedMsgSrcPathMap = {}

    for srcPath in srcPaths:
        success, text = getRenderedSource(srcPath, output_dir, assignment_alias)
        if success:
            renderedSrcPaths.append(srcPath)
            renderedSource.append(text)
        else:
            if text not in failedMsgSrcPathMap:
                failedMsgSrcPathMap[text] = []
            failedMsgSrcPathMap[text].append(srcPath)

    htmlCode = ''

    # add rendered source file text
    for i in range(len(renderedSrcPaths)):
        htmlCode += '<b>%s</b>'%renderedSrcPaths[i].replace(assignment_dir, '')
        htmlCode += '%s'%renderedSource[i]

    # add failed source file paths
    for errorMsg in failedMsgSrcPathMap:
        htmlCode += '<b>%s</b><br></br>'%errorMsg
        for failedSrcPath in failedMsgSrcPathMap[errorMsg]:
            htmlCode += '%s<br></br>'%failedSrcPath.replace(assignment_dir, '')

    return htmlCode 

def getRenderedSource(srcPath, output_dir, assignment_alias):
    IMG_EXTS = ['.jpg', '.jpeg', '.gif', '.png', '.bmp']
    if os.path.splitext(srcPath)[1].lower() in IMG_EXTS:
        resourceDir = getReportResourceDir(output_dir, assignment_alias)
        if not os.path.isdir(resourceDir):
            os.makedirs(resourceDir)
        shutil.copy(srcPath, resourceDir)
        newImgPath = opjoin(os.path.basename(resourceDir), os.path.basename(srcPath))
        newImgPath = urllib.pathname2url(newImgPath.encode('utf-8'))
        return True, u'<p></p><img src="%s">'%newImgPath
    else:
        with open(srcPath, 'r') as f:
            sourceCode = f.read()
            sourceCode = toUnicode(sourceCode)
            try:
                lexer = guess_lexer_for_filename(srcPath, sourceCode)
            except pygments.util.ClassNotFound as e:
                return False, 'No lexer found for:'
            return True, highlight(sourceCode, lexer, HtmlFormatter())

            # success, unistr = getUnicodeStr(sourceCode)
            # if success:
                # try:
                    # lexer = guess_lexer_for_filename(srcPath, unistr)
                # except pygments.util.ClassNotFound as e:
                    # # return '<p></p>'+'<pre>'+format(e)+'</pre>'
                    # return False, 'No lexer found for:'
                # return True, highlight(unistr, lexer, HtmlFormatter())
            # else:
                # return False, '<p></p>'+'<pre>'+unistr+'</pre>'

def getOutput(buildRetCode, buildLog, userInputList, exitTypeList, stdoutStrList):
    s = '<pre>\n'
    if buildRetCode!=0: # build error
        s += buildLog
    else:
        for i in range(len(userInputList)):
            userInput = userInputList[i]
            exitType = exitTypeList[i]
            stdoutStr = stdoutStrList[i]
            if exitType == 0:
                s += '(user input: %s)\n'%userInput
                # success, unistr = getUnicodeStr(stdoutStr)
                # s += highlight(unistr, TextLexer(), HtmlFormatter())
                s += highlight(stdoutStr, TextLexer(), HtmlFormatter())
            elif exitType == -1:
                s += highlight(stdoutStr, TextLexer(), HtmlFormatter())
            elif exitType == 1:   # time out
                s += '(user input: %s)\n'%userInput
                s += 'Timeout'
            s += '\n'
    return s
 
# def getUnicodeStr(str):
    # success = True
    # encodingStrs = ['utf-8', sys.getfilesystemencoding(), '(chardet)']
    # try:
        # detected = chardet.detect(str)
    # except ValueError as e:
        # retstr = format(e)
        # success = False
        # return success, retstr

    # for encodingStr in encodingStrs:
        # if encodingStr=='(chardet)':
            # encoding = detected['encoding']
        # else:
            # encoding = encodingStr

        # try:
            # retstr = unicode(str, encoding)
            # success = True
            # break
        # except UnicodeDecodeError as e:
            # retstr = format(e)+'\n(chardet detects %s with the confidence level of %f)'%(detected['encoding'], detected['confidence'])
            # success = False

    # return success, retstr
        

