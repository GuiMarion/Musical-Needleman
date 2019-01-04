import nwalign as nw
from functions import *
import random
import sys
from tqdm import tqdm

SIZEMAX = 100

def testNeedleman(N):

	alpha = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
	Validated = 0
	SamePath = 0
	for epoch in tqdm(range(N)):
		sizeA = random.randint(1, SIZEMAX)
		sizeB = random.randint(sizeA//2, 2*sizeA)
		A = ""
		B = ""
		for i in range(sizeA):
			A += alpha[random.randint(0,len(alpha)-1)]

		for i in range(sizeB):
			B += alpha[random.randint(0,len(alpha)-1)]

		aligned = nw.global_align(A, B, matrix='atiam-fpa_alpha.dist', gap_open=-3, gap_extend=-3)
		score = nw.score_alignment(aligned[0], aligned[1], gap_open=-3, gap_extend=-3, matrix='atiam-fpa_alpha.dist')

		res = (aligned[0], aligned[1], score)

		try:
			(a, b, s) = myNeedleman(A, B, matrix='atiam-fpa_alpha.dist', gap_open=-3, gap_extend=-3)

			if s == score:
				Validated += 1

			if res == (a, b, s):
				SamePath += 1
		except RuntimeError:
			print(A, B)
			pass

	print(str(100*Validated/N) +  "% are validated.")
	print(str(100*SamePath/N) + "% have the exact same path.")

if __name__ == "__main__":
	try:
		testNeedleman(int(sys.argv[1]))
	except ValueError:
		print("You have to provide an integer.")



