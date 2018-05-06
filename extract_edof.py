#!/usr/bin/python3
#encoding=utf-8

# Author João Paulo Barraca <jpbarraca@gmail.com>

import sys
import os
import binascii
from PIL import Image

# Configuration defaults
show_edof = False
save_edof = False
save_original = False
save_processed = False
delete_file = False

def extract_edof(data, idx, fname):
	if data[idx + 4:idx + 8] != b'edof':
		print("ERROR: Frame is not EDOF")
		return False
	
	idx += 8
	columns = int.from_bytes(data[idx + 16: idx + 18], byteorder='little')
	rows = int.from_bytes(data[idx + 18: idx + 20], byteorder='little')
	print("\t* found EDOF at %d with geometry=%dx%d" % (idx, columns, rows))

	orientation = data[idx + 7]

	idx += 68
	img = Image.frombuffer('L', (columns, rows), data[idx:], 'raw', 'L', 0, 0)
	if orientation == 0x10:
		img = img.transpose(Image.FLIP_TOP_BOTTOM)
	elif orientation == 0x12:
		img = img.transpose(Image.FLIP_LEFT_RIGHT)
	elif orientation == 0x13:
		img = img.transpose(Image.TRANSPOSE)

	if show_edof:
		img.show()

	if save_edof:
		outfname = (''.join(fname.split('.')[:-1])) + '-EDOF.png'
		print("\t  * saving to %s" % outfname)
		img.save(outfname)

	return True


def scan_segment(data, idx, fname, segment_index):
	if data[idx:idx + 2] != b'\xff\xd8':
		return -1

	i = idx + 2
	while i < len(data):
		if data[i] == 0xff:
				if data[i + 1] == 0xd9 or data[i + 1] == 0xd8:
					i += 2
					continue

				if data[i + 1] == 0xda: # SOA
					j = i + 2
					while not (data[j] == 0xff and data[j + 1] == 0xd9):
						j += 1
					
					j += 1

					print("\t* found segment %d, range %d to %d, length %d" % (segment_index, idx, j, j - idx))

					if (save_original and segment_index == 1) or (save_processed and segment_index == 0):
						outfname = (''.join(fname.split('.')[:-1])) + ('-%d.JPG' % segment_index)
						print("\t * saving segment to %s" % outfname)
						f = open(outfname, "wb")
						f.write(data[idx: j + 1])
						f.close()
					
					return j 
				
				length = 256 * data[i+2] + data[i+3] + 2
				i += length

				continue
		i += 1

	return 0

def print_usage():
	print("Usage: %s [options] img1 img2 img3... " % sys.argv[0])
	print("Options: ")
	print("\t-p: Save the originaly processed image to the same directory")
	print("\t-o: Save the originaly unprocessed image to the same directory")
	print("\t-e: Save the EDOF as an image to the same directory")
	print("\t-v: View the EDOF image")
	print("\t-d: Delete file and only keep extracted (will enforce -o -e)")


def main(fname):
	print("Processing: %s" % fname)
	fin = None

	try:
		fin = open(fname, "rb")
	except FileNotFoundError:
		print("ERROR: Could not open %s" % fname)
		return False

	data = fin.read()

	if data[:3] != b'\xff\xd8\xff':
		print("No JPEG header found")
		return False

	print ("\t* scanning file")

	if  data.find(bytes([0x00, 0x65, 0x64, 0x6f, 0x66, 0x00])) < 0:
		print("No EDOF header found")
		return False

	idx = 0
	segment_index = 0
	while True:
		r = scan_segment(data, idx, fname, segment_index)
		if r == -1:
			if segment_index > 1:
				# No standard segment was found. Search for EDOF
				return extract_edof(data, idx, fname)
			else:
				return False

		segment_index += 1
		idx = r + 1

		if idx > len(data):
			return False

if __name__ == "__main__":
	print("Huawei Dual Camera EDOF Extractor\n")

	if sys.version_info[0] < 3:
		print("This script requires Python 3")
		sys.exit(-1)

	if len(sys.argv) < 2:
		print_usage()
		sys.exit(-1)
	else:
		for o in sys.argv[1:]:
			if o.startswith("-"):
				for c in o[1:]:
					if c == 'e':
						save_edof = True
					elif c == 'o':
						save_original = True
					elif c == 'p':
						save_processed = True
					elif c == 'v':
						show_edof = True
					elif c == 'd':
						save_original = True
						delete_file = True
					else:
						print("Unknown Option: %s" % c)
						print_usage()
						sys.exit(-1)
				
		for p in sys.argv[1:]:
			if p[0] != "-":
				if not os.path.exists(p):
					print("File not found: %s" % p)
					continue

				r = main(p)

				if r and delete_file:
					print("\t* Deleting file: %s" % p)
					os.unlink(p)