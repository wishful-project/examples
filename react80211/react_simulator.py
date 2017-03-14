import time
import numpy as np
import _thread

#---------- CONSTANTS ----------
C = 1
#-------------------------------

class Centralized_react:
	""" init functions
	"""
	def __init__(self, T, W, w, node_number):
		self.debug_mode = 0
		self.T = T
		self.T_virtual = [row[:] for row in self.T]
		self.W = W
		self.w = w
		self.S = []
		self.node_number = node_number

		if self.debug_mode:
			self.print_matrix(self.T)
		self.add_two_hops_link()
		if self.debug_mode:
			self.print_matrix(self.T_virtual)
		self.S = self.init_S()

		self.update_enabler = False


	def init_S(self):
		S = []
		N = len(self.T)
		for i in range(0, N):
			tmp_s = {}
			for j in range(0, N):
				tmp_s[i] = {}
			S.append(tmp_s)

		for i in range(0,N):
			for j in range(0,N):
				if self.T_virtual[i][j]!= 0:
					S[i][j]= {'w' : self.w[j], 'claim' : self.w[j], 'offer' : 1}

		# i=0
		# for s in S:
		# 	print("node: {}".format(i))
		# 	#print(s)
		# 	for k, v in s.items():
		# 		if v:
		# 			print("k : {} w:{} \t claim:{}\t offer:{}".format(k, v['w'], v['claim'], v['offer']))
		# 	i+=1

		return S


	def add_two_hops_link(self):
		for i in range(0, self.node_number):
			for j in range(0, self.node_number):
				#print("%d - %d" %(i, self.W[i][j]))
				if self.W[i][j] > 0 :
					neighj = [k for k,x in enumerate(self.T[j]) if x==1] #neighj=find(G(j,:)==1);
					#print(self.T[j])
					#print(neighj)
					#print(self.T_virtual[i])
					for k in range(0, len(neighj)):
						self.T_virtual[i][neighj[k]] = 1 #G2(i,neighj)=1;
						self.T_virtual[neighj[k]][i] = 1 #G2(neighj,i)=1;
					#print(self.T_virtual[i])
					#self.print_matrix(self.T)

	""" react functions
	"""
	def update_offer(self, neigh_list ,my_mac):
		done = False
		A = C
		D = [key for key,val in neigh_list.items()]
		Dstar = []
		iteration = 0
		#print('%d - set(D) %s - set(Dstar) %s - offer %f' % (iteration, str(set(D)), str(set(Dstar)), neigh_list[my_mac]['offer']))
		while done == False:
			Ddiff = list(set(D) - set(Dstar))

			if set(D) == set(Dstar):
				done = True
				neigh_list[my_mac]['offer'] = A + max([val['claim'] for key,val in neigh_list.items()])
			else:
				done = True
				neigh_list[my_mac]['offer'] = A / float(len(Ddiff))
				for b in Ddiff:
					if neigh_list[b]['claim'] < neigh_list[my_mac]['offer']:
						Dstar.append(b)
						A -= neigh_list[b]['claim']
						done = False
			iteration += 1
			#print('%d - set(D) %s - set(Dstar) %s - offer %f' % (iteration, str(set(D)), str(set(Dstar)), neigh_list[my_mac]['offer']))
		return neigh_list

	def update_claim(self, neigh_list, my_mac):
		off_w = [ val['offer'] for key,val in neigh_list.items() ]
		off_w.append( neigh_list[my_mac]['w'] )
		neigh_list[my_mac]['claim'] = min(off_w)
		return neigh_list

	def send_react_msg(self, ll_a, ll_b):
		for key_a, val_a in ll_a.items():
			for key_b, val_b in ll_b.items():
				if key_a == key_b:
					ll_b[key_b]['claim'] = ll_a[key_a]['claim']
					ll_b[key_b]['offer'] = ll_a[key_a]['offer']
		return ll_b


	""" printing functions
	"""

	def print_matrix(self, A):
		print('--------------------')
		print('\n'.join([''.join(['{}\t'.format(item) for item in row]) for row in A]))
		print('--------------------')

	def print_neigh_list(self,S):
		i=0
		for s in S:
			print("node: {}".format(i))	
			for k,v in s.items():
				#if v:
				if v and k == i:
					print("k : {} w:{} \t claim:{}\t offer:{}".format(k, v['w'], v['claim'], v['offer']))
			i+=1

	def get_claim_list(self):
		node_index = 0
		curr_claim=[0 for x in range(0, self.node_number)]
		for s in self.S:
			#print("node: {}".format(node_index))
			for k, v in s.items():
				if v and node_index == k:
					print("k: {} - node claim: {}".format(k, v['claim']))
					curr_claim[node_index] = v['claim']
			node_index += 1
		return curr_claim

	def get_node_react_list(self):
		node_index = 0
		curr_claim=[0 for x in range(0, self.node_number)]
		curr_w=[0 for x in range(0, self.node_number)]
		curr_offer=[0 for x in range(0, self.node_number)]
		for s in self.S:
			#print("node: {}".format(node_index))
			for k, v in s.items():
				if v and node_index == k:
					#print("node claim: {}".format(v['claim']))
					curr_claim[node_index] = v['claim']
					curr_w[node_index] = v['w']
					curr_offer[node_index] = v['offer']
			node_index += 1
		return [curr_claim, curr_w, curr_offer]


	def update_traffic(self, W, w):
		self.W = W
		self.w = w
		self.T_virtual = [row[:] for row in self.T]

		if self.debug_mode:
			self.print_matrix(self.T)
		self.add_two_hops_link()
		if self.debug_mode:
			self.print_matrix(self.T_virtual)
		self.S = self.init_S()

		self.update_enabler = True

		time.sleep(0.5)

		self.update_enabler = False


	def run_loop(self):
		# init neighbors list

		while True:
			if self.update_enabler:
				#self.print_neigh_list(self.S)
				#curr_claim=self.get_claim_list()
				for i in range(0, self.node_number):
					self.S[i]=self.update_offer(self.S[i],i)
					self.S[i]=self.update_claim(self.S[i],i)

					#send claim,offer to neighbors:
					for key in self.S[i]:
						if i!=key:
							self.S[key] = self.send_react_msg(self.S[i], self.S[key])
			time.sleep(0.1)

def main():
	pass

if __name__ == "__main__":
	main()

