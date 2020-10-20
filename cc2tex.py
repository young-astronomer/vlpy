#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 12:17:04 2020

@author: f90
"""
import os
import sys
import getopt
from astropy.coordinates import Angle
import astropy.units as u
import numpy as np
from astropy.table import Table

infile = '/home/f90/Documents/DATA/BA113A/3c66a-calib/m.fits'
outfile = '%s/out.tex' % os.path.dirname(infile)

def cc2tex(infile, outfile='', fmt=''):
	if fmt in ['l', 'latex']:
		fmt = 'ascii.latex'
	elif fmt in ['a', 'aas', 'aastex']:
		fmt = 'ascii.aastex'
	# Read AIPS CC table
	cc = Table.read(infile, hdu=1)
#	print(cc.columns)
	# Change units from degree to mas
	cc['DELTAX'] = cc['DELTAX'] * 3.6E6
	cc['DELTAY'] = cc['DELTAY'] * 3.6E6
	cc['MAJOR AX'] = cc['MAJOR AX'] * 3.6E6
	cc['MINOR AX'] = cc['MINOR AX'] * 3.6E6
	# change coordinate, make the first component as (0, 0) point
	cc['DELTAX'] = cc['DELTAX'] - cc['DELTAX'][0]
	cc['DELTAY'] = cc['DELTAY'] - cc['DELTAY'][0]
	
	cc['r'] = np.sqrt(cc['DELTAX']**2+cc['DELTAY']**2)
	pa = np.arctan2(cc['DELTAX'], cc['DELTAY'])
	pa = np.degrees(pa)
	pa = Angle(pa.data * u.deg)
	pa.wrap_at('360d', inplace=True)
	#print(pa)
	cc['pa'] = pa
	cc.sort(['r'])
	
	# creat new table
	t = Table()
	t['comp'] = ['J%d' % (len(cc)-i) for i in range(len(cc))]
	t['flux'] = cc['FLUX'].data * 1.0e3
	t['x'] = cc['DELTAX'].data
	t['y'] = cc['DELTAY'].data
	t['r'] = cc['r'].data
	t['pa'] = pa.degree
	t['d'] = cc['MAJOR AX'].data
	t['comp'][0] = 'C'
	# set formats
	t['flux'].info.format = '%.3f'
	t['x'].info.format = '%.3f'
	t['y'].info.format = '%.3f'
	t['r'].info.format = '%.3f'
	t['pa'].info.format = '%.1f'
	t['d'].info.format = '%.3f'
	# set units
	t['flux'].unit = 'mJy'
	t['x'].unit = 'mas'
	t['y'].unit = 'mas'
	t['r'].unit = 'mas'
	t['pa'].unit = 'deg'
	t['d'].unit = 'mas'
	#print(t)
	t.write(outfile, format=fmt)

def myhelp():
	print('Help on cc2tex.py')
	print('cc2tex.py <input.fits>')
	print('  or: cc2tex.py <input.fits> <out.tex>')
	print('  or: cc2tex.py -f latex -i <input.fits> -o <out.tex>')
	
def main(argv):
	infile = ''
	outfile = ''
	fmt = ''
	
	try:
		opts, args = getopt.getopt(argv, "hi:o:f:", ['help', 'infile', 'outfile', 'format'])
	except getopt.GetoptError:
		myhelp()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			myhelp()
			sys.exit(0)
		elif opt in ('-i', '--infile'):
			infile = arg
		elif opt in ('-o', '--outfile'):
			outfile = arg
		elif opt in ('-f', '--format'):
			fmt = arg
	if len(args) == 1:
		infile = args[0]
	if len(args) == 2:
		infile, outfile = args
	if outfile == '':
		outfile = infile.split('.')[0] + '.tex'
	if fmt == '':
		fmt = 'ascii.latex'
	cc2tex(infile, outfile, fmt)

if __name__ == '__main__':
	main(sys.argv[1:])