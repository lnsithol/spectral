#########################################################################
#
#   Envi.py - This file is part of the Spectral Python (SPy) package.
#
#   Copyright (C) 2001 Thomas Boggs
#
#   Spectral Python is free software; you can redistribute it and/
#   or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   Spectral Python is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#     
#   You should have received a copy of the GNU General Public License
#   along with this software; if not, write to
#
#               Free Software Foundation, Inc.
#               59 Temple Place, Suite 330
#               Boston, MA 02111-1307
#               USA
#
#########################################################################
#
# Send comments to:
# Thomas Boggs, tboggs@users.sourceforge.net
#

'''
Code for creating SpyFile objects from ENVI headers.
'''

def ReadEnviHdr(file):
    '''
    USAGE: hdr = ReadEnviHeader(file)

    Reads a standard ENVI image file header and returns the parameters in
    a dictionary as strings.
    '''

    from string import find, split, strip
    from exceptions import IOError
    
    f = open(file, 'r')
    
    if find(f.readline(), "ENVI") == -1:
        f.close()
        raise IOError, "Not an ENVI header."

    lines = f.readlines()
    f.close()

    dict = {}
    i = 1
    try:
        while i < len(lines):
            if find(lines[i], '=') == -1:
                i += 1
                continue
            (key, val) = split(lines[i], '=')
            key = strip(key)
            val = strip(val[:-1])
            if val[0] == '{':
                str = val
                while str[-1] != '}':
                    i += 1
                    str += strip(lines[i][:-1])
                
                if key == 'description':
                    dict[key] = str[1:-1]
                else:
                    vals = split(str[1:-1], ',')
                    for j in range(len(vals)):
                        vals[j] = strip(vals[j])
                    dict[key] = vals
            else:
                dict[key] = val
            i += 1
        return dict
    except:
        raise IOError, "Error while reading ENVI file header."


def EnviHdr(file, image = ''):
    '''Creates a SpyFile object from an ENVI HDR file.'''

    import os
    from exceptions import IOError, TypeError

    h = ReadEnviHdr(file)
    h["header file"] = file

    class Params: pass
    p = Params()
    p.nBands = int(h["bands"])
    p.nRows = int(h["lines"])
    p.nCols = int(h["samples"])
    p.offset = int(h["header offset"])
    p.byteOrder = int(h["byte order"])

    #  Validate image file name
    if image == '':
        #  Try to determine the name of the image file
        if file[-4:] == '.hdr' or file[-4:] == '.HDR.':
            #  Try header name without extension or with (.img)
            if os.access(file[:-4], os.F_OK):
                image = file[:-4]
            elif os.access(file[:-4] + '.img', os.F_OK):
                image = file[:-4] + '.img'
            elif os.access(file[:-4] + '.IMG', os.F_OK):
                image = file[:-4] + '.IMG'
        if image == '':
            raise IOError, 'Unable to determine image file name.'
    if not os.access(image, os.F_OK):
        raise IOError, 'File ' + image + ' not found.'
    if not os.access(image, os.R_OK):
        raise IOError, 'No read access for file ' + image + '.'
    p.fileName = image

    #  Determine numeric data type
    if h["data type"] == '2':
        #  Int16
        p.format = 'h'
        p.typecode = 's'
    elif h["data type"] == '1':
        #  char
        p.format = 'b'
        p.typecode = '1'
    else:
        #  Don't recognize this type code
        raise TypeError, 'Unrecognized data type code in header ' + \
              'file.  If you believe the header to be correct, please' + \
              'submit a bug report to have the type coded added.'

    #  Return the appropriate object type for the interleave format.
    inter = h["interleave"]
    if inter == 'bil' or inter == 'BIL':
        from Spectral.Io.BilFile import BilFile
        return BilFile(p, h)
    elif inter == 'bip' or inter == 'BIP':
        from Spectral.Io.BipFile import BipFile
        return BipFile(p, h)
    else:
        raise TypeError, 'Looks like I forgot to include BSQ format' + \
              ' for ENVI HDR files.  Send me a bug report and I\'ll' + \
              ' fix it ASAP.'

