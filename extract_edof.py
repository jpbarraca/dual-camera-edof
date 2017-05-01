#!/usr/bin/python3
#encoding=utf-8

# Author João Paulo Barraca <jpbarraca@gmail.com>

import sys
import binascii
from PIL import Image

# Configuration defaults
show_edof = True
save_edof = False
save_original = False


def extract_edof(data, idx, fname):
	if data[idx + 4:idx + 8] != b'edof':
		print("ERROR: Frame is not EDOF")
		return False
	
	print("\t* found EDOF header")
	idx += 8
	columns = int.from_bytes(data[idx + 16: idx + 18], byteorder='little')
	rows = int.from_bytes(data[idx + 18: idx + 20], byteorder='little')
	print("\t  * dimensions=%d x %d" % (columns, rows))
	
	idx += 68
	img = Image.frombuffer('L', (columns, rows), data[idx:], 'raw', 'L', 0, 0)
	img = img.transpose(Image.FLIP_LEFT_RIGHT)

	if show_edof:
		img.show()

	if save_edof:
		outfname = (''.join(fname.split('.')[:-1])) + '-EDOF.JPG'
		print("\t  * saving to %s" % outfname)
		img.save(outfname)

	return True


def scan_segment(data, idx, fname, segment_index):
	if data[idx:idx + 2] != b'\xff\xd8':
		return 0
	
	i = idx + 2

	while i < len(data):
		if data[i] == 0xff:
				if data[i + 1] == 0xd9:
					i += 2
					continue
				if data[i + 1] == 0xda: # SOA
					if save_original:
						j = i + 2
						while not (data[j] == 0xff and data[j + 1] == 0xd9):
							j += 1
						
						j += 1

						print("\t* found segment %d, range %d to %d, length %d" % (segment_index, idx, j, j - idx))

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
	print("\t-o: Save the original image to the same directory")
	print("\t-e: Save the EDOF as an image to the same directory")
	print("\t-v: View the EDOF image")


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

	idx = 0
	segment_index = 0
	while True:
		r = scan_segment(data, idx, fname, segment_index)
		if r == 0:
			# No standard segment was found. Search for EDOF
			extract_edof(data, idx, fname)
			break

		segment_index += 1
		idx = r + 1


if __name__ == "__main__":
	print("Huawei Dual Camera EDOF Extractor\n")

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
					elif c == 'v':
						show_edof = True
					else:
						print("Unknown Option: %s" % c)
						print_usage()
						sys.exit(-1)
				
		for p in sys.argv[1:]:
			if p[0] != "-":
				main(p)