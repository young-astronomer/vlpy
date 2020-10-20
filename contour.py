#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 16:24:25 2020

This program is use to plot contour map from vlbi fits image.
You can specify the input fits image by -i or --infile,
	output file by -o or --output,
	contour levs by -l or --levs
	contour base by -c or --cmul
	plot window by -w or --win
	restore beam position by -b or --bpos

Installation:
1. copy file
	chmod a+x contour.py
	cp coutour.py ~/myapp
2. set envioment parameters
	Add the following line to ~/.bashrc
	export PATH=$PATH:/home/usename/myapp
	source ~/.bashrc

Running like this:
	contour.py <input.fits> <cmul>
	contour.py <input.fits> <output.pdf> <cmul>
	contour.py <input.fits> <output.jpg> <cmul> <win>
	contour.py -i <input.fits> -o <output.png> -c <0.001> -w "15 -15 -25 5"

@author: Li, Xiaofeng
Shanghai Astronomical Observatory, Chinese Academy of Sciences
E-mail: lixf@shao.ac.cn; 1650152531@qq.com
"""
import sys
import getopt
from astropy.io import fits
from astropy.table import Table
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

def add_beam(ax, win, h, bpos=None, pad=2.0):
	if bpos==None :
		x = win[0] - pad * h['bmaj']*3.6E6
		y = win[2] + pad * h['bmaj']*3.6E6
		bpos = (x, y)
	bmaj = h['bmaj'] * 3.6E6
	bmin = h['bmin'] * 3.6E6
	bpa = 90 - h['bpa']
	e = Ellipse(bpos, bmaj, bmin, angle=bpa, ec='k', facecolor='gray')
	ax.add_artist(e)
	
def annotate(ax, notefile=''):
	if notefile != '':
		tab = Table.read(notefile, format='csv')
		for t in tab:
			ax.text(t['x'], t['y'], t['text'])
#	ax.annotate('%s' % h['object'], xy=(0.125,0.91), xycoords='figure fraction')
#	ax.annotate('%.1f GHz' % (h['crval3']/1.0E9), xy=(0.83, 0.91), xycoords='figure fraction')

def add_annotation(ax, notefile=''):
	if notefile == '':
		return
	
	with open(notefile, 'r') as f:
		for line in f.readlines():
			row = line.split(',')
			row = [col.strip() for col in row]
			typ = row[0]
			args = row[1:]
			if typ == 'text':
				x, y, text = args
				x, y = float(x), float(y)
				ax.text(x, y, text)
			elif typ == 'arrow':
				x1, y1, x2, y2 = np.array(args, dtype='f4')
				ax.annotate("", xy=(x1, y1), xytext=(x2, y2), 
				arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
			elif typ == 'annotation':
				x1, y1, x2, y2 = np.array(args[:-1], dtype='f4')
				text = args[-1]
				ax.annotate(text, xy=(x1, y1), xytext=(x2, y2),
				 arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
			elif typ == 'ellipse':
				x, y, majax, minax, pa = np.array(args, dtype='f4')
				e = Ellipse((x,y), majax, minax, angle=pa, lw=0.5, ec='k', facecolor='none')
				ax.add_artist(e)

def set_axis(ax, w):
	ax.set_aspect('equal')
	ax.set_xlabel('Relative R.A. (mas)')
	ax.set_ylabel('Relative Dec. (mas)')
	ax.set_xlim(w[0],w[1])
	ax.set_ylim(w[2],w[3])
	ax.tick_params(which='both', direction='in', length=6, right=True, top=True)
	ax.tick_params(which='minor',length=4)
	ax.minorticks_on()

def word2pix(w, h):
	if w == None:
		W = [0, h['naxis1'], 0, h['naxis2']]
	else:
		x0, x1, y0, y1 = w
		X0 = h['crpix1'] + x0/(h['cdelt1']*3.6E6)
		Y0 = h['crpix2'] + y0/(h['cdelt2']*3.6E6)
		X1 = h['crpix1'] + x1/(h['cdelt1']*3.6E6)
		Y1 = h['crpix2'] + y1/(h['cdelt2']*3.6E6)
		W = [int(X0), int(X1), int(Y0), int(Y1)]
	return W

def pix2word(W, h):
	if W == None:
		W = [0, h['naxis1'], 0, h['naxis2']]
	X0, X1, Y0, Y1 = W
	x0 = h['cdelt1']*3.6E6 * (X0-h['crpix1'])
	y0 = h['cdelt2']*3.6E6 * (Y0-h['crpix2'])
	x1 = h['cdelt1']*3.6E6 * (X1-h['crpix1'])
	y1 = h['cdelt2']*3.6E6 * (Y1-h['crpix2'])
	w = [x0, x1, y0, y1]
	return w

def savefig(outfile, dpi=300):
	if outfile.lower().endswith('.pdf') :
		plt.savefig(outfile)
	elif outfile.lower().endswith('.jpg') or outfile.lower().endswith('.jpeg'):
		plt.savefig(outfile, dpi=dpi)
	elif outfile.lower().endswith('.png'):
		plt.savefig(outfile, dpi=dpi)
	
def contour(infile, cmul, outfile='', win=None, levs=None, bpos=None, figsize=None, notefile=''):
	hdul = fits.open(infile)
	h = hdul[0].header
	img = hdul[0].data[0, 0, :, :]
	
	if levs==None:
		levs = cmul*np.array([-1,1,2,4,8,16,32,64,128,256,512,1024,2048,4096])
#	print(win)
	if figsize == None :
		figsize = (6, 6)
	if win == None:
		win = pix2word(None, h)
		W = word2pix(None, h)
	else:
		W = word2pix(win, h)
	
	fig, ax = plt.subplots()
	fig.set_size_inches(figsize)
	set_axis(ax, win)
	add_beam(ax, win, h, bpos=bpos)
	add_annotation(ax, notefile)
	ax.contour(img[W[2]:W[3], W[0]:W[1]], levs, extent=win, 
			linewidths=0.5, colors='k')
	fig.tight_layout(pad=0.5)
	if outfile != '':
		savefig(outfile)
	hdul.close()

def myhelp():
	print('Error: coutour.py <test.fits> <cmul>')
	print('  or: coutour.py <test.fits> <out.pdf> <cmul>')
	print('  or: coutour.py <test.fits> <out.pdf> <cmul> <win>')
	print('  or: coutour.py -i <test.fits> -o <out.pdf> -c <0.002> -w "left right bottom top"')

def main(argv):
#	infile = r'3c66a-calib/circe-beam.fits'
	infile = ''
	outfile = ''
	notefile = ''
	cmul = ''
	win = None
	levs = None
	bpos = None
	figsize = None

	try:
		opts, args = getopt.getopt(argv, "hi:c:o:w:l:b:f:n:", 
							 ['help', 'infile', 'cmul', 'outfile', 'win', 'bpos', 'figsize', 'note', 'levs'])
	except getopt.GetoptError:
		myhelp()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			myhelp()
		elif opt in ('-i', '--infile'):
			infile = arg
		elif opt in ('-c', '--cmul'):
			cmul = arg
		elif opt in ('-o', '--outfile'):
			outfile = arg
		elif opt in ('-w', '--win'):
			win = arg
		elif opt in ('-l', '--levs'):
			levs = np.array(arg.split(), dtype=np.float64).tolist()
		elif opt in ('-b', '--bpos'):
			bpos = np.array(arg.split(), dtype=np.float64).tolist()
		elif opt in ('-f', '--figsize'):
			figsize = np.array(arg.split(), dtype=np.float64).tolist()
		elif opt in ('-n', '--note'):
			notefile = arg
	if infile=='' and len(args)==2:
		infile, cmul = args
	if infile=='' and outfile=='' and len(args)==3:
		infile, outfile, cmul = args
	if infile=='' and outfile=='' and len(args)==4:
		infile, outfile, cmul, win = args
	cmul = float(cmul)
	if type(win) == str:
		win = np.array(win.split(), dtype=np.float64).tolist()
	contour(infile, cmul, outfile=outfile, win=win, levs=levs, bpos=bpos, figsize=figsize, notefile=notefile)

if __name__ == '__main__' :
	main(sys.argv[1:])