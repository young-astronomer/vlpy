#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 21:13:42 2020

This program is use to read AIPS-CC table from fits file, 
and output a model file to be read by difmap.

Installation:
1. copy file
	chmod a+x cc2mod.py
	cp cc2mod.py ~/myapp
2. set envioment parameters
	Add the following line to ~/.bashrc
	export PATH=$PATH:/home/usename/myapp
	source ~/.bashrc

Running like this:
	cc2mod.py <input.fits> <output.mod>
	cc2mod.py <input.fits>

@author: Li, Xiaofeng
Shanghai Astronomical Observatory, Chinese Academy of Sciences
E-mail: lixf@shao.ac.cn; 1650152531@qq.com
"""

import sys
import numpy as np
from astropy.table import Table

def main(argv):
	infile = ''
	outfile = ''
	if len(argv) == 1:
		infile = argv[0]
		outfile = '%s-py.mod' % infile.split('.')[0]
	elif len(argv) == 2:
		infile, outfile = argv
	else:
		print('cc2mod.py <input.fits> <output.mod>')
		print('or : cc2mod.py <input.fits>')
		sys.exit(2)
		
	cc2mod(infile, outfile)
   
def cc2mod(infile, outfile=''):
	cc = Table.read(infile, format='fits', hdu=1)
	type_obj = np.unique(cc['TYPE OBJ'])
	if type_obj.size == 1 and type_obj[0]==0 :
#		print('cc mode')
		names = ('flux', 'r', 'theta')
		x, y = cc['DELTAX']*3.6E6, cc['DELTAY']*3.6E6
		r = np.sqrt(x**2+y**2)
		theta = np.arctan2(x, y)
		theta = np.degrees(theta)
		t = Table([cc['FLUX'], r, theta], names=names)
	elif type_obj.size == 1 and type_obj[0]== 1:
#		print('Gaussian mod')
		names = ('flux', 'r', 'theta', 'maj', 'ratio', 'pa', 'type')
		x, y = cc['DELTAX']*3.6E6, cc['DELTAY']*3.6E6
		r = np.sqrt(x**2+y**2)
		theta = np.arctan2(x, y)
		theta = np.degrees(theta)
		maj = cc['MAJOR AX'] * 3.6e6
		ratio = cc['MINOR AX'] * 3.6e6 / maj
		t = Table([cc['FLUX'], r, theta, maj, ratio, cc['POSANGLE'], cc['TYPE OBJ']], names=names)
	else:
#		print('cc+gaussian mod')
		names = ('flux', 'r', 'theta', 'maj', 'ratio', 'pa', 'type')
		x, y = cc['DELTAX']*3.6E6, cc['DELTAY']*3.6E6
		r = np.sqrt(x**2+y**2)
		theta = np.arctan2(x, y)
		theta = np.degrees(theta)
		maj = cc['MAJOR AX'] * 3.6e6
		ratio = cc['MINOR AX'] * 3.6e6 / maj
		t = Table([cc['FLUX'], r, theta, maj, ratio, cc['POSANGLE'], cc['TYPE OBJ']], names=names)
		for i in range(len(t)) :
			if t['type'][i] == 0.0 :
				t['maj'][i] = 0.0
				t['ratio'][i] = 0.0
				t['pa'][i] = 0.0
	if len(outfile) == 0 :
		print(t)
	else:
		t.write(outfile, format='ascii.no_header', overwrite=True)
	
if __name__ == '__main__' :
	main(sys.argv[1:])
	