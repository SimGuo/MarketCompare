market_list = (0, 4, 8, 21, 24, 26)

market_rating_lst = {}

for i in market_list:
	market_rating_lst[i] = []

fin = open('rating.txt', 'r')

for line in fin:
	pkg = line.split('\t')[0]
	marketid = int(line.split('\t')[1])
	if marketid in market_rating_lst:
		rating = line.split('\t')[2]
		if rating == 'None': rating = None
		else: rating = float(rating)
		rating_num = line.split('\t')[3]
		if rating_num == 'None': rating_num = None
		else: rating_num = int(rating_num)
		stars = line.split('\t')[4].replace('\r', "").replace('\n', "")
		if stars == 'None': stars = None
		else:
			each_star = stars.split(';')
			stars = []
			for i in each_star:
				stars.append(int(i))
		market_rating_lst[marketid].append(tuple([rating, rating_num, stars]))

fin.close()

for marketid in market_list:
	cnt = 0
	error_sum = 0
	error_cnt = 0
	for rating_arr in market_rating_lst[marketid]:
		if rating_arr[1] != None and rating_arr[2] != None and rating_arr[1] > 0 and sum(rating_arr[2]) > 0:
			rating_show = rating_arr[0]
			rating_real = 0
			for i in range(5):
				rating_real += (i+1)*2*rating_arr[2][i]
			rating_real /= sum(rating_arr[2])
			cnt += 1
			error = abs(rating_show-rating_real)
			error_sum += error
			if error > 0.5:
				error_cnt += 1
	print (str(marketid)+' '+str(cnt)+' '+str(error_sum/cnt)+' '+str(error_cnt/cnt))