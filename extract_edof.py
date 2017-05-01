#!/usr/bin/python3
#encoding=utf-8

# Author João Paulo Barraca <jpbarraca@gmail.com>

import sys
import binascii
from PIL import Image

show_image = False
save_image = False

def extract_edof(fin, fname):
	data = fin.read(2) # Skip

	data = fin.read(4)
	if data != b'edof':
		print("ERROR: Frame is not EDOF")
		return False
	
	print("Found EDOF Header")
	data = fin.read(68)

	columns = int.from_bytes(data[16:18], byteorder='little')
	rows = int.from_bytes(data[18:20], byteorder='little')
	print("\t * dimensions=%d x %d" % (columns, rows))

	data = fin.read(columns * rows)

	img = Image.frombuffer('L', (columns, rows), data, 'raw', 'L', 0, 0)
	img = img.transpose(Image.FLIP_LEFT_RIGHT)
	if show_image:
		img.show()

	if save_image:
		outfname = (''.join(fname.split('.')[:-1])) + '-EDOF.JPG'
		print("\t * saving to %s" % outfname)
		img.save(outfname)

	return True

def find_eoi(fin, fname):
	data = fin.read(2)

	while data != b'\xff\xd9':
		c = fin.read(1)
		if c == '':
			print("ERROR: Could not find EOI header")
			return False

		data = data[1:] + c
	return True

def find_edof(fin, fname):
	data = fin.read(2)
	if data == b'\x56\xe9':
		return extract_edof(fin, fname)
		
	if data[:1] != b"\xff":
		print("ERROR: Could not find EDOF header")
		return False

	if data[1:2] == b'\xe0':		
		pass
	elif data[1:2] == b'\xd8':
		find_edof(fin, fname)
		return
	elif data[1:2] == b'\xda':
		if find_eoi(fin, fname):
			return find_edof(fin, fname)
		return False

	data = fin.read(6)
	length = int.from_bytes(data[:1], byteorder='big') * 256 + (int.from_bytes(data[1:2], byteorder='big') - 2)
	fin.seek(length - 4, 1)
	
	find_edof(fin, fname)


def print_usage():
	print("Usage: %s [options] img1 img2 img3... " % sys.argv[0])
	print("Options: ")
	print("\t-s: Save the EDOF as an image to the same directory")
	print("\t-v: View the EDOF image")

def main(fname):
	print("Processing: %s" % fname)
	fin = None

	try:
		fin = open(fname, "rb")
	except FileNotFoundError:
		print("ERROR: Could not open %s" % fname)
		return False

	data = fin.read(3)

	if data != b'\xff\xd8\xff':
		print("No JPEG header found")
		return False

	print ("\t * scanning file")

	if find_eoi(fin, fname):
		find_edof(fin, fname)

if __name__ == "__main__":
	print("Huawei Dual Camera EDOF Extractor\n")

	if len(sys.argv) < 2:
		print_usage()
		sys.exit(-1)
	else:
		for o in sys.argv[1:]:
			if o == '-s':
				save_image = True
			elif o == '-v':
				show_image = True
			elif o[0] == '-':
				print("Unknown Option: %s" % o)
				print_usage()
				sys.exit(-1)
			else:
				main(o)