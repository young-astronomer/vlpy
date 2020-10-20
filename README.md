# vlpy
Some python programs for VLBI data analysis and visualization
## contour.py
This program is used to plot contour map from fits image.
### Runnig program
	1. contour.py <input.fits> <cmul>
	2. contour.py <input.fits> <output.pdf> <cmul>
	3. contour.py <input.fits> <output.jpg> <cmul> <win>
	4. contour.py -i <input.fits> -o <output.png> -c <0.001> -w "<15 -15 -25 5>"
### Examples
	contour.py -c 1.8e-3 -w '18 -8 -20 6' -n cta102-note.txt -i cta102.fits -o cta102.png
![CTA 102 contour image](cta102.png)

## cc2note.py
This program is used to create cta102-note.txt file which is input file of contour.py. The cta102-note.txt file contain some annotations parameters.
	1. text, x, y, some text
	2. ellipse, x, y, major axis, minor axis, posiation angle
	3. annotation, x1, y1, x2, y2, some text

	cc2note.py 2230+114m.fits cta102-note.txt

## polplot.py
This program is use to plot polarization map from vlbi fits image.
You should specify the input fits images by -i or --infile,
	output file by -o or --output,
	contour levs by -l or --levs
	contour base by -c or --cmul
	polarization parameters by -p or --pol: "icut pcut inc scale"
	plot window by -w or --win
	restore beam position by -b or --bpos
	figsize by -f or --figsize

### Installation:
1. copy file
	chmod a+x contour.py
	cp coutour.py ~/myapp
2. set envioment parameters
	Add the following line to ~/.bashrc
	export PATH=$PATH:/home/usename/myapp
	source ~/.bashrc

### Running like this:
	polplot.py -c <cmul> -w <win> -p <pol-params> <i.fits> <q.fits> <u.fits>
	polplot.py -c <cmul> -w <win> -p <pol-params> <i.fits> <q.fits> <u.fits> <out.pdf>
	polplot.py i <input file list> -o <out.pdf> -c <cmul> -w <win> -p <pol>

### Examples:
	1. polplot.py -i 'c.fits q.fits u.fits' -o 'pol-zoom.pdf' -c 1.6e-4 -w '5 -5 -5 5' -f '6.8 6' -p '1.28e-3 1.6e-4 3 0.05'
	2. polplot.py -i 'c.fits q.fits u.fits' -o 'pol.pdf' -c 1.6e-4 -w '10 -5 -25 5' -f '4.0 6' -p '1.28e-3 1.6e-4 3 0.05'
