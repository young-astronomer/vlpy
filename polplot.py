#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 16:28:22 2020

This program is use to plot polarization map from vlbi fits image.
You should specify the input fits images by -i or --infile,
	output file by -o or --output,
	contour levs by -l or --levs
	contour base by -c or --cmul
	polarization parameters by -p or --pol: "icut pcut inc scale"
	plot window by -w or --win
	restore beam position by -b or --bpos
	figsize by -f or --figsize

Installation:
1. copy file
	chmod a+x contour.py
	cp coutour.py ~/myapp
2. set envioment parameters
	Add the following line to ~/.bashrc
	export PATH=$PATH:/home/usename/myapp
	source ~/.bashrc

Running like this:
	polplot.py -c <cmul> -w <win> -p <pol-params> <i.fits> <q.fits> <u.fits>
	polplot.py -c <cmul> -w <win> -p <pol-params> <i.fits> <q.fits> <u.fits> <out.pdf>
	polplot.py i <input file list> -o <out.pdf> -c <cmul> -w <win> -p <pol>

Examples:
	1. polplot.py -i 'c.fits q.fits u.fits' -o 'pol-zoom.pdf' -c 1.6e-4 -w '5 -5 -5 5' -f '6.8 6' -p '1.28e-3 1.6e-4 3 0.05'
	2. polplot.py -i 'c.fits q.fits u.fits' -o 'pol.pdf' -c 1.6e-4 -w '10 -5 -25 5' -f '4.0 6' -p '1.28e-3 1.6e-4 3 0.05'

@author: Li, Xiaofeng
Shanghai Astronomical Observatory, Chinese Academy of Sciences
E-mail: lixf@shao.ac.cn; 1650152531@qq.com
"""

import sys
import getopt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Ellipse
from astropy.io import fits
from astropy.table import Table

def world2pix(w, h):
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

def pix2world(W, h):
	if W == None:
		W = [0, h['naxis1'], 0, h['naxis2']]
	X0, X1, Y0, Y1 = W
	x0 = h['cdelt1']*3.6E6 * (X0-h['crpix1'])
	y0 = h['cdelt2']*3.6E6 * (Y0-h['crpix2'])
	x1 = h['cdelt1']*3.6E6 * (X1-h['crpix1'])
	y1 = h['cdelt2']*3.6E6 * (Y1-h['crpix2'])
	w = [x0, x1, y0, y1]
	return w

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

def cut_cmap(cmap, ncut=0):
#	cmap = mcolors.Colormap(cmap)
	cmap = plt.get_cmap(cmap)
	x = np.arange(ncut, 256) / 256.0
	color_index = cmap(x)
	cmap = mcolors.ListedColormap(color_index)
	return cmap

def get_normalize(args, vmin=0.0, vmax=1.0):
	if args == '':
		norm = mcolors.Normalize(vmin, vmax)
	args = args.split(' ')
	name = args[0]
	if name == 'linear':
		if len(args)==3:
			vmin, vmax = np.array(args[1:], dtype='f4')
		norm = mcolors.Normalize(vmin, vmax, True)
	elif name == 'power':
		if len(args)==1:
			gamma = 0.5
		if len(args)==2:
			gamma = float(args[1])
		elif len(args)==4:
			gamma, vmin, vmax = np.array(args[1:], dtype='f4')
		if gamma < 1.0 and vmin < 0.0:
			vmin = 0.0
		norm = mcolors.PowerNorm(gamma, vmin, vmax, True)
	elif name == 'log':
		if len(args)==3:
			vmin, vmax = np.array(args[1:], dtype='f4')
		norm = mcolors.LogNorm(vmin, vmax)
	elif name == 'symlog':
		if len(args)==2:
			linthresh = float(args[1])
			linscale = 1.0
		elif len(args)==3:
			linthresh, linscale = np.array(args[1:], dtype='f4')
		elif len(args)==5:
			linthresh, linscale, vmin, vmax = np.array(args[1:], dtype='f4')
		norm = mcolors.SymLogNorm(linthresh, linscale, vmin, vmax)
	elif name == 'twoslope':
		if len(args)==2:
			vcenter = float(args[1])
		elif len(args)==4:
			vcenter, vmin, vmax = np.array(args[1:], dtype='f4')
		norm = mcolors.TwoSlopeNorm(vcenter, vmin, vmax)
	return norm

def add_annotation(ax, infile=''):
	if infile == '':
		return

	with open(infile, 'r') as f:
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
				e = Ellipse((x,y), majax, minax, angle=pa, lw=0.5, fc='none', ec='blue')
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

def savefig(outfile, dpi=300):
	if outfile.lower().endswith('.pdf') :
		plt.savefig(outfile)
	elif outfile.lower().endswith('.jpg') or outfile.lower().endswith('.jpeg'):
		plt.savefig(outfile, dpi=dpi)
	elif outfile.lower().endswith('.png'):
		plt.savefig(outfile, dpi=dpi)

def polplot(ifile, qfile, ufile, outfile, cmul, icut, pcut, inc=3, scale=30.0,
			levs=None, win=None, bpos=None, figsize=None, dpi=100, annotationfile='', 
			cmap='', ncut=0, norm=''):
	if levs==None:
		levs = [-1] + np.logspace(0, 10, 10, base=2).tolist()
		levs = cmul * np.array(levs)
	if figsize == None :
		figsize = (6, 6)

	hdul = fits.open(ifile)
	h = hdul[0].header
	if win == None:
		win = pix2world(None, h)
		W = world2pix(None, h)
	else:
		W = world2pix(win, h)
	I = hdul[0].data[0, 0, W[2]:(W[3]+1), W[0]:(W[1]+1)]
	hdul = fits.open(qfile)
	Q = hdul[0].data[0, 0, W[2]:(W[3]+1), W[0]:(W[1]+1)]
	hdul = fits.open(ufile)
	U = hdul[0].data[0, 0, W[2]:(W[3]+1), W[0]:(W[1]+1)]
	P = np.sqrt(Q**2+U**2)
	fp = np.divide(P, I)
	mask = np.logical_or(I<icut, P<pcut)
	Q[mask] = np.nan
	U[mask] = np.nan
	P[mask] = np.nan
	fp[mask] = np.nan
	
	
	if cmap == '':
		cmap = 'rainbow'
	cmap = cut_cmap(cmap, ncut)
	vmin, vmax = np.nanmin(fp), np.nanmax(fp)
	if norm == '':
		norm = 'linear %.3f %.3f' % (vmin, vmax)
	norm = get_normalize(norm, vmin, vmax)

	fig, ax = plt.subplots()
	fig.set_size_inches(figsize)
	set_axis(ax, win)
	add_beam(ax, win, h, bpos=bpos)
#	add_annotate(ax, h)
	add_annotation(ax, annotationfile)
	ax.contour(I, levs, extent=win, 	linewidths=0.5, colors='k')

	pcm = ax.imshow(fp, extent=win, cmap=cmap, norm=norm, origin='lower', 
				 interpolation='none')
	cbar = fig.colorbar(pcm, ax=ax, fraction=0.05)
#	cbar.ax.minorticks_off()
	cbar.ax.tick_params('both',direction='in',right=True,top=True,which='both')
	cbar.ax.tick_params(axis='y', labelrotation=90)
	x, y = np.meshgrid(np.arange(win[0], win[1], -0.1), 
					np.arange(win[2],win[3], 0.1))
	chi = 0.5 * np.arctan2(U, Q)
	u = P * (-np.sin(chi))
	v = P * np.cos(chi)
	ax.quiver(x[::inc,::inc], y[::inc,::inc], u[::inc,::inc], v[::inc,::inc], 
		   scale=scale, width=0.003, headlength=0, 
		   headaxislength=0, headwidth=0, pivot='middle', lw=0.1)

	fig.tight_layout(pad=0.5)
	if outfile != '':
		savefig(outfile, dpi)
	hdul.close()

def myhelp():
	print('Error: polplot.py -c <1.2e-3> -w  "<10 -5 -25 5>" -p "<1.28e-3 1.6e-4 3 0.05>" <i.fits> <q.fits> <u.fits>')
	print('  or: polplot.py -c <1.2e-3> -w  "<10 -5 -25 5>" -p "<1.28e-3 1.6e-4 3 0.05>" <i.fits> <q.fits> <u.fits> <out.pdf>')
	print('  or: polplot.py -i "<i.fits q.fits u.fits>" -o "<out.pdf>" -c <1.2e-3> -w <10 -5 -25 5> -p "<1.28e-3 1.6e-4 3 0.05>"')
	
def main(argv):
	ifile = ''
	qfile = ''
	ufile = ''
	outfile = ''
	figsize = (6, 6)
	dpi = 100
	win = None
	bpos = None
	cmul = 0.0
	levs = None
	icut = 0.0
	pcut = 0.0
	inc = 3
	scale = 30.0
	annotationfile = ''
	colormap = ''
	ncut = 0
	norm = ''

	try:
		opts, args = getopt.getopt(argv, "hi:o:f:d:w:b:l:c:l:p:a:n:N:", 
							 ['help', 'infile=', 'outfile=', 'figsize=', 'dpi=', 'win=', 
		 'bpos=', 'cmul=', 'levs=', 'pol=', 'annotatefile=', 'colormap=', 
		 'ncut=', 'norm='])
	except getopt.GetoptError:
		myhelp()
		sys.exit(2)

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			myhelp()
			sys.exit(0)
		elif opt in ('-i', '--ifile'):
			ifile, qfile, ufile = arg.split()
		elif opt in ('-o', '--outfile'):
			outfile = arg
		elif opt in ('-f', '--figsize'):
			figsize = np.array(arg.split(), dtype=np.float64).tolist()
		elif opt in ('-d', '--dpi'):
			dpi = int(arg)
		elif opt in ('-w', '--win'):
			win = np.array(arg.split(), dtype=np.float64).tolist()
		elif opt in ('-b', '--bpos'):
			bpos = np.array(arg.split(), dtype=np.float64).tolist()
		elif opt in ('-c', '--cmul'):
			cmul = float(arg)
		elif opt in ('-l', '--levs'):
			levs = np.array(arg.split(), dtype=np.float64).tolist()
		elif opt in ('-p', '--pol'):
			icut, pcut, inc, scale = np.array(arg.split(), dtype=np.float64).tolist()
			inc = int(inc)
		elif opt in ('-a', '--annotatefile'):
			annotationfile = arg
		elif opt in ('--colormap'):
			colormap = arg
		elif opt in ('-N', '--ncut'):
			ncut = int(arg)
		elif opt in ('-n', '--norm'):
			norm = arg

	if ifile=='' and len(args)==3:
		ifile, qfile, ufile = args.split()
	if ifile=='' and outfile=='' and len(args)==4:
		ifile, qfile, ufile = args.split()
	if outfile == '' :
		outfile == 'out.pdf'

	polplot(ifile, qfile, ufile, outfile, cmul, icut, pcut, inc=inc, 
		 scale=scale, levs=levs, win=win, bpos=bpos, figsize=figsize, dpi=dpi,
		 annotationfile=annotationfile, cmap=colormap, ncut=ncut, 
		 norm=norm)

if __name__ == '__main__' :
	main(sys.argv[1:])