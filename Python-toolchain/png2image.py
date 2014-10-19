#!/usr/bin/python

"""
For license, see gpl-3.0.txt
"""
from PIL import Image
import argparse
import math


def chunks(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i + n]


def color_to_plane_bits(color, depth):
	"""returns the bits for a given pixel in a list, lowest to highest plane"""
	result = [0] * depth
	for bit in range(depth):
		if color & (1 << bit) != 0:
			result[bit] = 1
	return result


def color_to_RGB4(rgb_color_triplet):
	final_color = 0
	final_color += rgb_color_triplet[2] / 16
	final_color += ((rgb_color_triplet[1] / 16) << 4)
	final_color += ((rgb_color_triplet[0] / 16) << 8)
	return final_color


def write_amiga_image(image, destfile):
	destfile = destfile.replace('.c', '')
	destfile = destfile.replace('.C', '')
	destfile = destfile.replace('.h', '')
	destfile = destfile.replace('.H', '')

	imdata = im.getdata()
	width, height = im.size
	colors = [i for i in chunks(map(ord, im.palette.tostring()), 3)]
	colors_amount = 2 * int(len(colors) / 2)
	if colors_amount < len(colors):
		colors_amount = len(colors) + 1
	depth = int(math.log(colors_amount, 2))
	print("width, height, colors, depth = %d, %d, %d, %d." % (width, height, len(colors), depth))

	map_words_per_row = width / 16
	if width % 16 > 0:
		map_words_per_row += 1

	# create the converted planar data
	planes = [[0] * (map_words_per_row * height) for _ in range(depth)]
	for y in range(height):
		x = 0
		while x < width:
			# build a word for each plane
			for i in range(min(16, width - x)):
				# get the palette index for pixel (x + i, y)
				color = imdata[y * width + x + i]  # color index
				planebits = color_to_plane_bits(color, depth)
				# now we need to "or" the bits into the words in their respective planes
				wordidx = (x + i) / 16  # word number in current row
				pos = y * map_words_per_row + wordidx  # list index in the plane
				for planeidx in range(depth):
					if planebits[planeidx]:
						planes[planeidx][pos] |= (1 << (15 - (x + i) % 16)) # 1 << ((x + i) % 16)
			x += 16

	##  Header file
	with open(destfile + '.h', 'w') as outfile:
		outfile.write('#include <intuition/intuition.h>\n\n')
		outfile.write('extern UWORD paldataRGB4[%d];\n' % (len(colors)))
		outfile.write('extern UWORD imdata[%d];\n' % (depth * map_words_per_row * height))

	##  C file
	with open(destfile + '.c', 'w') as outfile:
		outfile.write('#include <intuition/intuition.h>\n\n')

		##  Palettes
		outfile.write("/* Image palette, RGB4 format (OCS/ECS machines) */\n");
		outfile.write('UWORD paldataRGB4[] = {\n')
		outfile.write('\t')
		tpal = im.palette.tostring()
		tpal = map(ord, tpal)
		tpal = chunks(tpal, 3)
		for color_rgb in chunks(map(ord, im.palette.tostring()), 3):
			outfile.write(str(hex(color_to_RGB4(color_rgb))) + ',')
		outfile.write('\n')
		outfile.write('};\n\n')

		##  Bitplanes
		outfile.write("/* Ensure that this data is within chip memory or you'll see nothing !!! */\n");
		outfile.write('UWORD imdata[] = {\n')
		plane_idx = 0
		for plane in planes:
			outfile.write("\t/* Bitplane #%d */\n" % (plane_idx));
			for chunk in chunks(plane, map_words_per_row):
				outfile.write('\t')
				outfile.write(','.join(map(str, map(hex, chunk))))
				outfile.write(',\n')
			outfile.write('\n')
			plane_idx += 1
		outfile.write('};\n\n')

		planepick = 2 ** depth - 1  # currently we always use all of the planes
		outfile.write('struct Image image = {\n')
		outfile.write('\t0, 0, %d, %d, %d, imdata,\n' % (width, height, depth));
		outfile.write('\t%d, 0, NULL\n' % planepick)  # PlanePick, PlaneOnOff
		outfile.write('};\n')


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Amiga Image converter')
	parser.add_argument('--pngfile', required=True)
	parser.add_argument('--destfile', required=True)

	args = parser.parse_args()
	im = Image.open(args.pngfile)
	write_amiga_image(im, args.destfile)
	# im = Image.open('ilkke_font.png') ##args.pngfile)
	# write_amiga_image(im, 'test2.h') ##args.destfile)

