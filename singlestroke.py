import subprocess
import Image, ImageFont, ImageDraw
from xml.dom import minidom
from shapely.geometry import LineString
from collections import OrderedDict
import math


def rotatePoint(point, center, angle):
	angle = angle*0.0174532925
	s = math.sin(angle)
	c = math.cos(angle)

	point = (point[0] - center[0], point[1]-center[1])
	point = [point[0]*c - point[1]*s, point[0]*s + point[1]*c]
	point = [point[0] + center[0], point[1] + center[1]]
	point = [int(point[0]), int(point[1])]
	return point

def rotateLine(line, center, angle):
	line[0] = rotatePoint(line[0], center, angle)
	line[1] = rotatePoint(line[1], center, angle)
	return line



def intersection(lineA, lineB):
	line1 = LineString(lineA)
	line2 = LineString(lineB)
	if line1.intersects(line2):
		i = line1.intersection(line2)

		return i
	return -1

def findHorizLines(w,h,pix):
	horiz_lines = []
	hstart = -1
	for j in range(h):
		for i in range(w):
			if pix[i,j] == (0,0,0) and hstart == -1:
				hstart = i
			elif pix [i,j] != (0,0,0) and hstart != -1:
				horiz_lines.append([(hstart, j), (i,j)])
				hstart = -1
			elif pix[i,j] == (0,0,0) and i == w-1:
				horiz_lines.append([(hstart, j), (i,j)])
				hstart = -1
	horiz_lines = filter(lambda line: line[1][0]-line[0][0] > 100, horiz_lines)
	return horiz_lines


def continuous(horiz_lines):
	c = False
	if len(horiz_lines) > 0:
		c = True
		y1= horiz_lines[0][0][1]-1
		for line in horiz_lines:
			y2 = line[0][1]
			if y2 != y1 + 1:
				c = False
			y1 = y2
	return c

# use a truetype font
font = ImageFont.truetype("MardianDemo.ttf", 1000)
im = Image.new("RGBA", (100, 100))
draw = ImageDraw.Draw(im)


#for code in range(ord('a'), ord('z') + 1):
for code in range(ord('t'), ord('t') + 1):

	w, h = draw.textsize(chr(code), font=font)
	center = (w/2, h/2)
	xoffset = font.font.getabc(chr(code))[0]*-1
	yoffset = font.font.getabc(chr(code))[1]
	yoffset = -50

	orig_im = Image.new("RGBA", (w, h))
	draw = ImageDraw.Draw(orig_im)
	draw.text((xoffset, yoffset), chr(code), font=font, fill="#000000")
	lines = {}
	for deg in range(-89, 90, 5):
		im = orig_im.rotate(deg)

		background = Image.new("RGB", im.size, (255, 255, 255))
		background.paste(im, mask=im.split()[3]) # 3 is the alpha channel
		im = background
		pix = im.load()

		horiz_lines = findHorizLines(w,h,pix)

	
		if continuous(horiz_lines) and len(horiz_lines) > 7:
			horiz_lines = [horiz_lines[0], horiz_lines[-1]]


			for i in range(len(horiz_lines)):

				horiz_lines[i] = rotateLine(horiz_lines[i], center, deg)

			lines[deg] = horiz_lines



	lines = OrderedDict(sorted(lines.items()))
	for key in lines:
		im = orig_im


		background = Image.new("RGB", im.size, (255, 255, 255))
		background.paste(im, mask=im.split()[3]) # 3 is the alpha channel
		im = background
		pix = im.load()



		horiz_lines = lines[key]
		for line in horiz_lines:
			pix[line[0][0], line[0][1]] = (0,0,255)
			pix[line[1][0], line[1][1]] = (0,0,255)

		
		#im.show()


	for key1 in lines:
		for key2 in lines:
			if key1 > key2:
				intersections = []
				for line1 in lines[key1]:
					for line2 in lines[key2]:
						i = intersection(line1, line2)
						if i != -1:
							intersections.append(intersection(line1, line2))
				if len(intersections) == 4:
					i = intersections
					i = ["cat",i[0],i[1],i[3],i[2]]
					print i
					area = (i[1].x*i[2].y - i[2].x*i[1].y) + (i[2].x*i[3].y - i[3].x*i[2].y) + (i[3].x*i[4].y - i[4].x*i[3].y) + (i[4].x*i[1].y - i[1].x*i[4].y)

					#area = (i[0][0]*i[1][1] - i[1][0]*i[0][1]) + (i[1][0]*i[2][1] - i[2][0]*i[1][1]) + (i[2][0]*i[3][1] - i[3][0]*i[2][1]) + (i[3][0]*i[0][1] - i[0][0]*i[3][1])
					print area
					for i in intersections:
						pix[int(i.x),int(i.y)] = (255,0,0)


	#im.show()

	


	im.save(chr(code) + '.bmp', 'BMP', quality=80)

	proc = subprocess.Popen(['/usr/local/bin/autotrace', chr(code) + ".bmp", "-output-format", "svg", "-centerline"], stdout=subprocess.PIPE)
	output = proc.stdout.read()
	#output = "<svg width='252' height='1000'>\n<path style='stroke:#000000; fill:none;' d='M188 296C211.594 315.578 199.217 353.591 185.934 375C181.083 382.819 164.313 398.575 171.408 408.999C177.043 417.278 183.507 415.425 192 415.039C208.38 414.296 224.576 410.339 241 410M57 442L110 428.089L124 427.693L136 433.031L168 408M133 435C126.928 461.247 102.881 483.375 87.4275 505C58.2828 545.783 27.6688 590.555 15.8989 640C12.7415 653.264 14.7806 672.949 23.1744 683.996C26.9428 688.956 33.0762 695.356 40 692.955C53.8128 688.166 67.061 672.899 78 663.579C104.848 640.705 138.348 618.728 159 590'/>\n</svg>"

	xmldoc= minidom.parseString(output)

	svg=xmldoc.getElementsByTagName("svg")[0]
	children = list(svg.childNodes)
	for child in children:
		if child.nodeName == "path" and child.getAttribute("style") != "stroke:#000000; fill:none;":
			svg.removeChild(child.nextSibling)
			svg.removeChild(child)
	output = svg.toxml()
	"""
	pathElement = filter(lambda child: child.nodeName == "path", svg.childNodes)[0]
	path = str(pathElement.getAttribute("d"))
	paths = filter(lambda x: x != "", path.split("M"))
	"""

	f = open(chr(code) + '.svg', 'w')
	f.write(output)

