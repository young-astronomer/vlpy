# vlpy
Some python programs for VLBI data analysis and visualization
1. contour.py
2. cc2note.py
3. cc2tex.py convert AIPS CC table to latex table
4. cc2mod.py AIPS CC table to Dimmap mod file
5. polplot.py plot polarization image
6. prtan.py Print AN table in uvfits file




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

## cc2tex.py

	cc2tex.py 2230+114m.fits out.tex
```latex
\begin{table}
\begin{tabular}{ccccccc}
comp & flux & x & y & r & pa & d \\
 & $\mathrm{mJy}$ & $\mathrm{mas}$ & $\mathrm{mas}$ & $\mathrm{mas}$ & $\mathrm{{}^{\circ}}$ & $\mathrm{mas}$ \\
C & 1535.744 & 0.000 & 0.000 & 0.000 & 0.0 & 0.137 \\
J7 & 272.613 & 0.704 & -0.649 & 0.957 & 132.6 & 0.483 \\
J6 & 292.153 & 1.095 & -1.665 & 1.993 & 156.2 & 0.829 \\
J5 & 76.768 & 1.291 & -3.991 & 4.195 & 155.6 & 1.386 \\
J4 & 143.056 & 2.449 & -5.552 & 6.068 & 146.7 & 0.879 \\
J3 & 121.199 & 2.569 & -7.550 & 7.975 & 161.2 & 1.837 \\
J2 & 167.977 & 5.296 & -11.681 & 12.825 & 162.1 & 3.704 \\
J1 & 138.498 & 9.685 & -13.834 & 16.887 & 145.0 & 3.418 \\
\end{tabular}
\end{table}
```

## cc2mod.py
cc2mod.py 2230+114m.fits out.mod
1.535744309425354 0.0483061708509922 -28.359661102294922 0.13652236759662628 1.0 105.94539642333984 1.0
0.2726133465766907 0.9117016196250916 131.66152954101562 0.482522577047348 1.0 -96.34020233154297 1.0
0.14305609464645386 6.019773483276367 156.23577880859375 0.8786846995353699 1.0 -122.73522186279297 1.0
0.1679767519235611 12.776947021484375 155.62477111816406 3.7039573192596436 1.0 96.7098388671875 1.0
0.29215338826179504 1.9444652795791626 146.54136657714844 0.8294569253921509 1.0 -145.30482482910156 1.0
0.1211988627910614 7.927224636077881 161.2664031982422 1.8366743326187134 1.0 -145.30482482910156 1.0
0.07676761597394943 4.147329807281494 162.20083618164062 1.3862905502319336 1.0 -160.34616088867188 1.0
0.13849778473377228 16.839195251464844 144.98582458496094 3.4181699752807617 1.0 -130.42608642578125 1.0

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
