import math

market_list = (2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 15, 21)
big_market_index = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)

package_market_dl = {}

googleplay_download_trans = {
	5: 3,
	50: 30,
	500: 300,
	5000: 3000,
	50000: 30000,
	500000: 300000,
	5000000: 3000000,
	50000000: 30000000,
	500000000: 300000000,
	5000000000: 3000000000,
	10: 7.5,
	100: 75,
	1000: 750,
	10000: 7500,
	100000: 75000,
	1000000: 750000,
	10000000: 7500000,
	100000000: 75000000,
	1000000000: 750000000,
	10000000000: 7500000000,
}

fin = open('downloads.txt', 'r')

for line in fin:
	package = line.split('\t')[0]
	marketid = int(line.split('\t')[1])
	dld = line.split('\t')[2].replace('\r', '').replace('\n', '')
	if dld == 'None': dld = None
	else: dld = int(dld)
	if dld != None and marketid in market_list:
		if not package in package_market_dl:
			package_market_dl[package] = {}
		if marketid == 0: package_market_dl[package][marketid] = googleplay_download_trans[dld]
		else: package_market_dl[package][marketid] = dld

print (len(package_market_dl))

iteration_round = 1

while True:

	print ('Iteration: '+str(iteration_round))

	cntll = []
	ratell = []

	for i in range(len(market_list)):
		cntll.append([0]*len(market_list))
		ratell.append([0]*len(market_list))

	for i in range(len(market_list)-1):
		for j in range(i+1, len(market_list)):
			sumi = 0
			sumj = 0
			cnt = 0
			marketi = market_list[i]
			marketj = market_list[j]
			for package, market_dl in package_market_dl.items():
				if marketi in market_dl and marketj in market_dl:
					cnt += 1
					sumi += market_dl[marketi]
					sumj += market_dl[marketj]
			#print (str(marketi)+' '+str(marketj)+' '+str(cnt)+' '+str(sumi)+' '+str(sumj))
			ratell[i][j] = sumi/sumj*cnt
			ratell[j][i] = sumj/sumi*cnt
			cntll[i][j] = cntll[j][i] = cnt

	cntsum = [0]*len(market_list)

	for i in range(len(market_list)):
		for j in range(len(market_list)):
			cntsum[i] += cntll[i][j]

	market_rate = [1/len(big_market_index)]*len(market_list)

	while True:
		prev_rate = market_rate[:]
		for i in range(len(market_list)):
			val = 0
			for j in range(len(market_list)):
				val += prev_rate[j]*ratell[j][i]
			market_rate[i] = val/cntsum[i]
		big_sum = 0
		for i in range(len(big_market_index)):
			big_sum += market_rate[big_market_index[i]]
		big_sum /= len(big_market_index)
		for i in range(len(market_list)):
			market_rate[i] /= big_sum
		#print (market_rate)
		eql = True
		for i in range(len(market_list)):
			if abs(prev_rate[i]-market_rate[i]) > 1e-10:
				eql = False
				break
		if eql:
			break

	print (market_rate)

	result = {}

	def average(lst, mkl):
		error_list = []
		if len(lst) <= 2:
			return sum(lst)/2, error_list
	#	if len(lst) >= 4:
	#		del(lst[lst.index(max(lst))])
	#		del(lst[lst.index(min(lst))])
		while len(lst) > 2:
			avg = sum(lst)/len(lst)
			ste = 0
			for i in lst:
				ste += (i-avg)*(i-avg)
			ste = math.sqrt(ste/len(lst))
			i = 0
			prevlen = len(lst)
			while i < len(lst):
				while i < len(lst) and (lst[i] > avg+1.96*ste): # or lst[i] < avg-1.96*ste
					if lst[i] < avg:
						error_list.append([mkl[i], '<'])
					else:
						error_list.append([mkl[i], '>'])
					del(lst[i])
					del(mkl[i])
				i += 1
			if len(lst) == prevlen:
				return avg, error_list
		return sum(lst)/len(lst), error_list

	factor = 3.7
	has_error = 0

	for package in package_market_dl.keys():
		dl_lst = []
		mk_lst = []
		for market, dl in package_market_dl[package].items():
			dl_lst.append(market_rate[market_list.index(market)]*dl*factor)
			mk_lst.append(market)
		result[package], error_list = average(dl_lst, mk_lst)
		result[package] = int(round(result[package]))
		if len(error_list):
			has_error += 1
			print (package)
			print (error_list)
			for error in error_list:
				del(package_market_dl[package][error[0]])

	if has_error > 0:
		print ('Error Num: '+str(has_error))
		iteration_round += 1
	else:
		break

rank = []
for key, val in result.items():
	rank.append(tuple([key, val]))

fout = open('Downloads_Rank.csv', 'w')

rank.sort(key=lambda x:(-x[1], x[0]))
for i in range(len(rank)):
	fout.write (rank[i][0].replace(',', '.')+','+str(rank[i][1])+'\n') #+','+str(len(package_market_dl[rank[i][0]]))+'\n')
#	for marketid in package_market_dl[rank[i][0]].keys():
#		print (marketid, end=' ')
#	print ()

fout.close()
