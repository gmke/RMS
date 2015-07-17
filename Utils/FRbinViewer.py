# RPi Meteor Station
# Copyright (C) 2015  Dario Zubovic
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cv2
import numpy as np
import sys, os

# FFbin handling stolen from FF_bin_suite.py from CMN_binViewer by Denis Vida

class ff_struct:
    """ Default structure for a FF*.bin file.
    """
    def __init__(self):
        self.nrows = 0
        self.ncols = 0
        self.nbits = 0
        self.first = 0
        self.camno = 0
        self.maxpixel = 0
        self.maxframe = 0
        self.avepixel = 0
        self.stdpixel = 0
        
def readFF(filename):
    """Function for reading FF bin files.
    Returns a structure that allows access to individual parameters of the image
    e.g. print readFF("FF300_20140802_205545_600_0090624.bin").nrows to print out the number of rows
    e.g. print readFF("FF300_20140802_205545_600_0090624.bin").maxpixel to print out the array of nrows*ncols numbers which represent the image
    INPUTS:
        filename: file name from the file to be read
    """

    fid = open(filename, 'rb')
    ff = ff_struct()
    ff.nrows = np.fromfile(fid, dtype=np.uint32, count = 1)
    ff.ncols = np.fromfile(fid, dtype=np.uint32, count = 1)
    ff.nbits = np.fromfile(fid, dtype=np.uint32, count = 1)
    ff.first = np.fromfile(fid, dtype=np.uint32, count = 1)
    ff.camno = np.fromfile(fid, dtype=np.uint32, count = 1)

    N = ff.nrows * ff.ncols

    ff.maxpixel = np.reshape (np.fromfile(fid, dtype=np.uint8, count = N), (ff.nrows, ff.ncols))
    ff.maxframe = np.reshape (np.fromfile(fid, dtype=np.uint8, count = N), (ff.nrows, ff.ncols))
    ff.avepixel = np.reshape (np.fromfile(fid, dtype=np.uint8, count = N), (ff.nrows, ff.ncols))
    ff.stdpixel = np.reshape (np.fromfile(fid, dtype=np.uint8, count = N), (ff.nrows, ff.ncols))

    return ff

class fr_struct:
    """ Default structure for a FF*.bin file.
    """
    def __init__(self):
        self.lines = 0
        self.frameNum = []
        self.yc = []
        self.xc = []
        self.t = []
        self.size = []
        self.frames = []
        
def readFR(filename):
    fid = open(filename, 'rb')
    fr_strc = fr_struct()
    fr_strc.lines = np.fromfile(fid, dtype=np.uint32, count = 1)
    
    for i in range(fr_strc.lines):
        frameNum = np.fromfile(fid, dtype=np.uint32, count = 1)
        yc = []
        xc = []
        t = []
        size = []
        frames = []
        
        for z in range(frameNum):
            yc.append(np.fromfile(fid, dtype=np.uint32, count = 1))
            xc.append(np.fromfile(fid, dtype=np.uint32, count = 1))
            t.append(np.fromfile(fid, dtype=np.uint32, count = 1))
            size.append(np.fromfile(fid, dtype=np.uint32, count = 1))
            frames.append(np.reshape(np.fromfile(fid, dtype=np.uint8, count = size[-1]**2), (size[-1], size[-1])))
        
        fr_strc.frameNum.append(frameNum)
        fr_strc.yc.append(yc)
        fr_strc.xc.append(xc)
        fr_strc.t.append(t)
        fr_strc.size.append(size)
        fr_strc.frames.append(frames)

    return fr_strc

def view(ff, fr):
    if ff == None:
        background = np.zeros((576, 720), np.uint8)
    else:
        background = readFF(ff).maxpixel
    
    name = fr
    fr = readFR(fr)
    
    print "Number of lines:", fr.lines
    
    for i in range(fr.lines):
        for z in range(fr.frameNum[i]):
            yc = fr.yc[i][z]
            xc = fr.xc[i][z]
            t = fr.t[i][z]
            size = fr.size[i][z]
            
            print "Center coords:", yc, xc, t, "size:", size
            
            y2 = 0
            for y in range(yc - size/2, yc + size/2):
                x2 = 0
                for x in range(xc - size/2,  xc + size/2):
                    background[y, x] = fr.frames[i][z][y2, x2]
                    x2 += 1
                y2 += 1
            
            cv2.imshow(name, background)
            cv2.waitKey(200)
    
    cv2.destroyWindow(name)
            

if __name__ == "__main__":
    fr_list = [fr for fr in os.listdir(".") if fr[0:2]=="FR" and fr[-3:]=="bin"]
    if(len(fr_list) == None):
        print "No files found!"
        sys.exit()
    
    ff_list = [ff for ff in os.listdir(".") if ff[0:2]=="FF" and ff[-3:]=="bin"]
    
    for fr in fr_list:
        ffbin = None
        for ff in ff_list:
            if ff[2:] == fr[2:]:
                ffbin = ff
                break
        
        view(ffbin, fr)