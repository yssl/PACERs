import os, zipfile, shutil
from unicode import *

###########################################
# file manipulation functions
def copytree2(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = opjoin(src, item)
        d = opjoin(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def unzipInAssignDir(assignDir):
    unzipDirNames = []
    for name in os.listdir(assignDir):
        filePath = opjoin(assignDir, name)
        if zipfile.is_zipfile(filePath):
            if os.name=='posix':
                # Use unzip command instead of python zipfile module only for posix os (due to python bug?)
                try:
                    unzipDir = os.path.splitext(filePath)[0]
                    try:
                        shutil.rmtree(unzipDir)
                    except OSError:
                        pass
                    subprocess.check_output('unzip "%s" -d "%s"'%(filePath, unzipDir), stderr=subprocess.STDOUT, shell=True)
                except subprocess.CalledProcessError as e:
                    print e.output
                else:
                    unzipDirNames.append(unzipDir)
            else:
                # print filePath
                with zipfile.ZipFile(filePath, 'r') as z:
                    unzipDir = os.path.splitext(filePath)[0]
                    unzipDir = unzipDir.strip()
                    unzipDir = toString(unzipDir)
                    try:
                        z.extractall(unzipDir)
                    except Exception as e:
                        print '!!!Error when unzipping %s - %s'%(filePath, type(e))
                    unzipDirNames.append(unzipDir)
    return unzipDirNames

def removeUnzipDirsInAssignDir(assignDir, unzipDirNames):
    for d in unzipDirNames:
        try:
            shutil.rmtree(d)
        except:
            pass


