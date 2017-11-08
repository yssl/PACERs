################################################################################
# unicode.py

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
import os, sys, chardet
from unidecode import unidecode

############################################
# unicode functions
def opjoin(a, b):
    if os.name=='posix':
        # Convert paths for os.path.join to byte string only for posix os (due to python bug?)
        return toUnicode(os.path.join(toString(a), toString(b)))
    else:
        return os.path.join(a, b)

def toString(unistr):
    if isinstance(unistr, str):
        return unistr
    return unistr.encode(sys.getfilesystemencoding())

def toUnicode(string):
    if isinstance(string, unicode):
        return string
    try:
        retstr = unicode(string, sys.getfilesystemencoding())
    except UnicodeDecodeError as e:
        try:
            detectedEncoding = chardet.detect(string)['encoding']
            if detectedEncoding!=None:
                retstr = unicode(string, chardet.detect(string)['encoding'])
            else:
                retstr = 'chardet fails to detect encoding'
        except UnicodeDecodeError as e:
            return toUnicode(str(e))
        return retstr
    else:
        return retstr

############################################
# unidecode functions
def unico2decoPath(unicoPath, deco2unicoMap):
    unicoTokens = os.path.normpath(unicoPath).split(os.sep)

    decoTokens = []
    for unicoToken in unicoTokens:
        hasExt = '.' in unicoToken
        if hasExt:
            name, ext = os.path.splitext(unicoToken)
            unicoToken = name

        decoToken = unidecode(unicoToken)
        decoToken = decoToken.replace(' ', '_')
        decoToken = decoToken.replace('(', '_')
        decoToken = decoToken.replace(')', '_')
        if decoToken not in deco2unicoMap:
            deco2unicoMap[decoToken] = unicoToken

        if hasExt:
            decoToken += ext

        decoTokens.append(decoToken)

    decoPath = reduce(os.path.join, decoTokens)
    return decoPath

def deco2unicoPath(decoPath, deco2unicoMap):
    decoTokens = os.path.normpath(decoPath).split(os.sep)

    unicoTokens = []
    for decoToken in decoTokens:
        hasExt = '.' in decoToken
        if hasExt:
            name, ext = os.path.splitext(decoToken)
            decoToken = name

        unicoToken = deco2unicoMap[decoToken]

        if hasExt:
            unicoToken += ext

        unicoTokens.append(unicoToken)

    unicoPath = reduce(os.path.join, unicoTokens)
    return unicoPath


