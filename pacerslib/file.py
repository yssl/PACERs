################################################################################
# file.py

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
import os, zipfile, shutil, subprocess
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


