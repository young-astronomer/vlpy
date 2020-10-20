#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 23:25:01 2020

@author: f90
"""

import os, sys, getopt
import wget, gzip
import re

def freq_to_band(nu):	
	nu = nu / 1.0e9
	if nu>=0.003 and nu<0.03:
		band='HF'
	elif nu>=0.03 and nu<0.3:
		band = 'UHF'
	elif nu>=0.3 and nu<1.0:
		band = 'UHF'
	elif nu>=1.0 and nu<2.0:
		band = 'L'
	elif nu>=2.0 and nu<4.0:
		band = 'S'
	elif nu>=4.0 and nu<8.0:
		band = 'C'
	elif nu>=8.0 and nu<12.0:
		band = 'X'
	elif nu>=12.0 and nu<18.0:
		band = 'U'
	elif nu>=18.0 and nu<27.0:
		band = 'K'
	elif nu>=27.0 and nu<40.0:
		band = 'Ka'
	elif nu>=40.0 and nu<75.0:
		band = 'Q'
	elif nu>=75.0 and nu<110.0:
		band = 'W'
	elif nu>=110.0 and nu<300.0:
		band = 'G'
	else:
		band = ''
	return band

def unzip(fgzip, fout):
	with gzip.GzipFile(fgzip, "rb") as f_in:
		with open(fout, "wb") as f_out:
			f_out.write(f_in.read())

def mojave_download(source, path=''):
	if path != '' :
		os.chdir(path)
		
	www = 'http://www.physics.purdue.edu/astro/MOJAVE/sourcepages/%s.shtml' % source
	webpage = os.path.basename(www)
	if os.path.exists(webpage):
		os.remove(webpage)
	wget.download(www)
	
	with open(webpage, 'rb') as f:
		text = f.read()
		text = text.decode('iso-8859-1')
		
		pattern = 'href="([^"]+sepvstime.png)"'
		link = re.compile(pattern).findall(text)[0]
		link = www[:43]+link[3:]
		if not os.path.exists(os.path.basename(link)):
			wget.download(link)
			
		pattern= 'href="(http[^"]+\.uvf)"'
		links = re.compile(pattern).findall(text)
		for link in links:
#			print(link, end='   ')
			fname = os.path.basename(link)
			dirname = fname[11:21].replace('_','-') + fname[9]
			print(dirname, fname)
			if not os.path.exists(dirname) :
				os.mkdir(dirname)
			os.chdir(dirname)
			if not os.path.exists(fname) :
				wget.download(link)
				
			if fname[9] != 'u' :
				os.chdir('..')
				continue
			png = fname.replace('.uvf', '.icn_color.png')		
			if not os.path.exists(png) :
				wget.download(link.replace('.uvf', '.icn_color.png'))
			fits = fname.replace('.uvf', '.icn.fits')
			if not os.path.exists(fits) :
				wget.download(link.replace('.uvf', '.icn.fits.gz'))
				unzip(fits+'.gz', fits)
			os.chdir('..')

def myhelp():
	print('Error: coutour.py <test.fits> <cmul>')
	print('  or: coutour.py <test.fits> <out.pdf> <cmul>')
	print('  or: coutour.py <test.fits> <out.pdf> <cmul> <win>')
	print('  or: coutour.py -i <test.fits> -o <out.pdf> -c <0.002> -w "left right bottom top"')

def main(argv):
	source = ''
	path = ''
	
	try:
		opts, args = getopt.getopt(argv, "hs:p:", 
							 ['help', 'source', 'path'])
	except getopt.GetoptError:
		myhelp()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			myhelp()
		elif opt in ('-s', '--source'):
			source = arg
		elif opt in ('-p', '--path'):
			path = arg
	if source=='' and len(args)==1:
		source = args[0]
	if source=='' and len(args)==2:
		source, path = args
	if path == '':
		path = '.'
	if source == '':
		myhelp()
		sys.exit(1)
	mojave_download(source, path)
			
if __name__ == '__main__':
	main(sys.argv[1:])