#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 21:05:21 2020

This program is use to read AIPS-AN table from UV fits file, 
and output the D-term amp and phas on Term or a txt file. 
You can specify the AN table version by -v or --ver parameter.
If you don't specify the output file, the results will print on Term.

Installation:
1. copy file
	chmod a+x prtan.py
	cp prtan.py ~/myapp
2. set envioment parameters
	Add the following line to ~/.bashrc
	export PATH=$PATH:/home/usename/myapp
	source ~/.bashrc

Running like this:
	prtan.py <input.fits>
	prtan.py <input.fits> <output.txt>
	prtan.py -i <input.fits> -v <1> -o <output.txt>

@author: Li, Xiaofeng
Shanghai Astronomical Observatory, Chinese Academy of Sciences
E-mail: lixf@shao.ac.cn; 1650152531@qq.com
"""
import sys
import getopt
import numpy as np
from astropy.io import fits

def prtrow(anname, x):
	re, im = x[::2], x[1::2]
	amp = np.sqrt(re**2+im**2) * 100
	phas = np.arctan2(im, re)
	phas = np.degrees(phas)
	line = ''
	line += anname
	for i in range(amp.size):
		line += ' & %.2f, %.1f' % (amp[i],phas[i])
	line += ' \\\\\n'
	return line

def prtan(infile, outfile, ver=1):
	hdul = fits.open(infile)
	for hdu in hdul:
		if hdu.name == 'AIPS AN' and hdu.ver == ver:
			break

	if hdu.name != 'AIPS AN' or hdu.ver != ver:
		print("AN %d doesn't exist!!!")
		sys.exit(1)

	text = ''
	for an in hdu.data:
		text += prtrow(an['anname'], an['polcala'])
		text += prtrow('  ', an['polcalb'])

	if outfile != '':
		with open(outfile, 'w') as f:
			f.write(text)
	else:
		text = text.replace('\\','').replace('&', '|')
		print(text)

	hdul.close()

def myhelp():
	print('Error: prtan.py <test.fits>')
	print(' or: prtan.py <test.fits> <out.txt>')
	print(' or: prtan.py -i <test.fits> -v <1> -o <out.txt>')

def main(argv):
	infile = ''
	outfile = ''
	ver = 1
#	infile = 'LPCAL.UVF'
	try:
		opts, args = getopt.getopt(argv, "hi:v:o:", ['help', 'infile', 'ver', 'outfile'])
	except getopt.GetoptError:
		myhelp()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			myhelp()
		elif opt in ('-i', '--infile'):
			infile = arg
		elif opt in ('-v', '--ver'):
			ver = int(arg)
		elif opt in ('-o', '--outfile'):
			outfile = arg
	if infile=='' and len(args)==1:
		infile = args[0]
	if infile=='' and outfile=='' and len(args)==2:
		infile, outfile = args

	prtan(infile, outfile, ver)

if __name__ == '__main__' :
	main(sys.argv[1:])
