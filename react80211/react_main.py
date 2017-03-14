from react_simulator import Centralized_react
import time
import numpy as np
import _thread
def main():
	T=[	[1, 1, 1],
		[1, 1, 1],
		[1, 1, 1]]
	w = [1,1,1]

	T=[	[1, 1, 0, 0],
		[1, 1, 1, 0],
		[0, 1, 1, 1],
		[0, 0, 1, 1]]
	w = [1,0,0,1]

	T=[	[1, 1, 1, 0],
		[1, 1, 1, 1],
		[1, 1, 1, 1],
		[0, 1, 1, 1]]
	w = [1,0,0,1]

	T=[	[1, 1, 0, 0],
		[1, 1, 1, 1],
		[0, 1, 1, 1],
		[0, 1, 1, 1]]
	w = [1,0,1,1]

	"""
	# ALTRO ESEMPIO: A-B-C-D-E
	T=[	[1,     1,     0,     0,     0],
		[1,     1,     1,     0,     0],
		[0,     1,     1,     1,     0],
		[0,     0,     1,     1,     1],
		[0,     0,     1,     1,     1]]
	w=[1,     0,     0,     1,     1]
	#Matrice Iniziale con Aggiunzioni di link A-C e B-D
	#connectivity matrix
	# [A]-->[B]<--[C]
	T=[	[1, 1, 0,],
		[1, 1, 1,],
		[0, 1, 1,]]
	w = [1,1,1]

	# FULL CONNECTED TOPOLOGY
	T=[	[1, 1, 1],
		[1, 1, 1],
		[1, 1, 1]]
	w = [1,1,1]
	"""

	iteration_number = 2
	# #		D		A		B	  C		E		F
	# T = [	[0,     1,     0,     0,     0,     0], #D
	# 		[1,     0,     1,     0,     0,     0], #A
	# 		[0,     1,     0,     1,     0,     1], #B
	# 		[0,     0,     1,     0,     1,     1], #C
	# 		[0,     0,     0,     1,     0,     1], #E
	# 		[0,     0,     1,     1,     1,     0]] #F
	#		D		A		B	  C		E		F
	T = [	[1,     1,     0,     0,     0,     0], #D
			[1,     1,     1,     0,     0,     0], #A
			[0,     1,     1,     1,     0,     1], #B
			[0,     0,     1,     1,     1,     1], #C
			[0,     0,     0,     1,     1,     1], #E
			[0,     0,     1,     1,     1,     1]] #F
	#		D		A		B	  C		E		F
	w = [0,     1,     0,     0,     1,     0]
	W = [	[0,     0,     0,     0,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     1,     0,     0],
			[0,     0,     0,     0,     0,     0]]

	x= Centralized_react(T, W, w, len(w))
	_thread.start_new_thread( x.run_loop, () )

	i=0
	while i < iteration_number:
		print(x.get_claim_list())
		time.sleep(1)
		i += 1

	#		D		A		B	  C		E		F
	w = [0,     0,     0,     0,     1,     0]
	W = [	[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     1,     0,     0],
			[0,     0,     0,     0,     0,     0]]
	x.update_traffic(W, w)

	i=0
	while i < iteration_number:
		print(x.get_claim_list())
		time.sleep(1)
		i += 1


	#	D		A		B	  C		E		F
	w = [0,     1,     0,     1,     0,     0]
	W = [	[0,     0,     0,     0,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     0,     0,     0]]
	x.update_traffic(W, w)
	i=0
	while i < iteration_number:
		print(x.get_claim_list())
		time.sleep(1)
		i += 1

	#	D		A		B	  C		E		F
	w = [0,     1,     1,     1,     0,     0]
	W = [	[0,     0,     0,     0,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     1,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     0,     0,     0]]
	x.update_traffic(W, w)
	i=0
	while i < iteration_number:
		print(x.get_claim_list())
		time.sleep(1)
		i += 1


	#	D		A		B	  C		E		F
	w = [0,     0.2,     0.2,     0.2,     0,     0]
	W = [	[0,     0,     0,     0,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     1,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     0,     0,     0]]
	x.update_traffic(W, w)
	i=0
	while i < iteration_number:
		print(x.get_claim_list())
		time.sleep(1)
		i += 1


	#	D		A		B	  C		E		F
	w = [0,     1,     0,     0,     1,     0]
	W = [	[0,     0,     0,     0,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     0,     1,     0,     0],
			[0,     0,     0,     0,     0,     0]]
	x.update_traffic(W, w)
	i=0
	while i < iteration_number:
		print(x.get_claim_list())
		time.sleep(1)
		i += 1

	#	D		A		B	  C		E		F
	w = [0,     1,     0,     1,     1,     0]
	W = [	[0,     0,     0,     0,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     0,     0,     0],
			[0,     0,     1,     0,     0,     0],
			[0,     0,     0,     1,     0,     0],
			[0,     0,     0,     0,     0,     0]]
	x.update_traffic(W, w)
	i=0
	while i < iteration_number:
		print(x.get_claim_list())
		time.sleep(1)
		i += 1

if __name__ == "__main__":
	main()

