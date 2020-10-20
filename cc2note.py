#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 22:44:01 2020

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

def cc2tex(infile, outfile='', dx=4.0, dy=1.0, theta=45.0):
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

	theta = np.radians(theta)
	with open(outfile, 'w') as f:
		for r in t:
			comp, x, y, d = r['comp'], r['x'], r['y'], r['d']
			f.write('ellipse, %.3f, %.3f, %.3f, %.3f, %.1f\n' % (x, y, d, d, 0))
			x = x + d/2.0*np.sin(theta)
			y = y + d/2.0*np.cos(theta)
			f.write('annotation, %.3f, %.3f, %.3f, %.3f, %s\n' % (x, y, x+dx, y+dy, comp))

def myhelp():
	print('Help on cc2note.py')
	print('cc2note.py <input.fits>')
	print('  or: cc2note.py <input.fits> <out.tex>')
	print('  or: cc2note.py -i <input.fits> -o <out.tex>')
	
def main(argv):
	infile = ''
	outfile = ''
	dx, dy = 4.0, 1.0
	theta = 45.0
	
	try:
		opts, args = getopt.getopt(argv, "hi:o:x:y:t", ['help', 'infile', 'outfile', 'dx', 'dy', 'theta'])
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
		elif opt in ('-x', '--dx'):
			dx = float(arg)
		elif opt in ('-y', '--dy'):
			dy = float(arg)
		elif opt in ('-t', '--theta'):
			theta = float(arg)
	if len(args) == 1:
		infile = args[0]
	if len(args) == 2:
		infile, outfile = args
	if outfile == '':
		outfile = infile.split('.')[0] + '.tex'
	cc2tex(infile, outfile, dx, dy, theta)

if __name__ == '__main__':
	main(sys.argv[1:])