#!/usr/bin/python

"""
For license, see gpl-3.0.txt
"""
from PIL import Image
import os
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
	destfile = os.path.splitext(destfile)[0] 

	sprite_h = 28
	imdata = im.getdata()
	width, total_height = im.size
	colors = [i for i in chunks(map(ord, im.palette.tostring()), 3)]
	colors_amount = 2 * int(len(colors) / 2)
	if colors_amount < len(colors):
		colors_amount = len(colors) + 1
	depth = int(math.log(colors_amount, 2))
	print("width, height, colors, depth = %d, %d, %d, %d." % (width, total_height, len(colors), depth))

	map_words_per_row = width / 16
	if width % 16 > 0:
		map_words_per_row += 1

	sprite_table = []
	height = sprite_h
	sprite_n = total_height / height
	for sprite_idx in range(0, sprite_n):
		y_offset = sprite_idx * height
		# create the converted planar data
		planes = [[0] * (map_words_per_row * height) for _ in range(depth)]
		for y in range(height):
			x = 0
			while x < width:
				# build a word for each plane
				for i in range(min(16, width - x)):
					# get the palette index for pixel (x + i, y)
					color = imdata[(y + y_offset) * width + x + i]  # color index
					planebits = color_to_plane_bits(color, depth)
					# now we need to "or" the bits into the words in their respective planes
					wordidx = (x + i) / 16  # word number in current row
					pos = y * map_words_per_row + wordidx  # list index in the plane
					for planeidx in range(depth):
						if planebits[planeidx]:
							planes[planeidx][pos] |= (1 << (15 - (x + i) % 16)) # 1 << ((x + i) % 16)
				x += 16

		sprite_table.append(planes)

	##  Header file
	with open(destfile + '.h', 'w') as h_outfile:
		h_outfile.write('#include <intuition/intuition.h>\n\n')
		h_outfile.write('extern UWORD %s_palRGB4[%d];\n' % (destfile, len(colors)))
		h_outfile.write('extern UWORD %s_img[%d][%d];\n' % (destfile, sprite_n, (sprite_h + 2) * 2))
		h_outfile.write('\n')

	##  C file
	with open(destfile + '.c', 'w') as c_outfile:
		c_outfile.write('#include <intuition/intuition.h>\n\n')

		##  Palettes
		c_outfile.write("/* Image palette, RGB4 format (OCS/ECS machines) */\n");
		c_outfile.write('UWORD %s_palRGB4[%d] = {\n' % (destfile, len(colors)))
		c_outfile.write('\t')
		for color_rgb in chunks(map(ord, im.palette.tostring()), 3):
			c_outfile.write(str(hex(color_to_RGB4(color_rgb))) + ',')
		c_outfile.write('\n')
		c_outfile.write('};\n\n')

		##  Bitplanes
		c_outfile.write("/* Ensure that this data is within chip memory or you'll see nothing !!! */\n");
		c_outfile.write('UWORD chip %s_img[%d][%d]=\n{\n' % (destfile, sprite_n, (sprite_h + 2) * 2))

		sprite_idx = 0
		for planes in sprite_table:
			c_outfile.write('\t/* Sprite #%d */\n' % sprite_idx);
			c_outfile.write('\t{\n')

			c_outfile.write('\t\t' + str(hex(0)) + ',' + str(hex(0)) + ',\n')
			plane_idx = 0
			for i in range(0, height):
				c_outfile.write('\t\t' + str(hex(planes[0][i])) + ',' + str(hex(planes[1][i])) + ',\n')

			c_outfile.write('\t\t' + str(hex(0)) + ',' + str(hex(0)) + '\n')
			c_outfile.write('\t},\n')

			sprite_idx += 1

		c_outfile.write('};\n\n')


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Amiga Image converter')
	parser.add_argument('--pngfile', required=True)
	parser.add_argument('--destfile', required=True)

	args = parser.parse_args()
	im = Image.open(args.pngfile)
	write_amiga_image(im, args.destfile)
	# im = Image.open('ilkke_font.png') ##args.pngfile)
	# write_amiga_image(im, 'test2.h') ##args.destfile)

