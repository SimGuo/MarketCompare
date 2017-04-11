from constant import *
import pymysql, os, codecs, datetime

def edit_distance(str1, str2):
	if str1 == None or str2 == None:
		return None
	str1 = str1.replace('\r', "").replace('\n', "").replace(' ', "").replace('\t', "")
	str2 = str2.replace('\r', "").replace('\n', "").replace(' ', "").replace('\t', "")
	l1 = len(str1)
	l2 = len(str2)
	# f(x, y) = match(s1[x], s2[y])?f(x+1, y+1): 1+min(f(x+1, y), f(x, y+1), f(x+1, y+1))
	oldmem = [0] * (l2+1)
	newmem = [0] * (l2+1)
	oldmem[l2] = 0
	for j in range(l2-1, -1, -1):
		oldmem[j] = l2-j
	for i in range(l1-1, -1, -1):
		newmem[l2] = l1-i
		for j in range(l2-1, -1, -1):
			if str1[i] == str2[j] or (str1[i] in (' ', '\n', '\t') and str2[j] in (' ', '\n', '\t')):
				newmem[j] = oldmem[j+1]
			else:
				newmem[j] = 1+min(min(oldmem[j], oldmem[j+1]), newmem[j+1])
		tmpmem = oldmem
		oldmem = newmem
		newmem = tmpmem
	ed = oldmem[0]/max(50, max(l1, l2))
	if ed <= 0.02: return 0
	elif ed <= 0.1: return 1
	elif ed <= 0.3: return 2
	elif ed <= 0.6: return 3
	else: return 4
	
if __name__ == '__main__':
	conn = pymysql.connect(host='localhost', port=3306, user='root', password='pkuoslab', db='Android', charset='utf8')
	cursor = conn.cursor()
	content = []
	for i in range(len(package_list)):
		package = package_list[i]
		package_content = []
		for market in market_list:
			ifexists = cursor.execute("select Market_APK_ID from Market_APP_Metadata where Package_Name = '"+package+"' and MarketID="+str(market))
			if ifexists == 0:
				package_content.append((None, None))
				print("Not Found "+package+" In "+market_name[market])
			else:
				market_apk_id = cursor.fetchall()[0][0]
				cursor.execute("select Description, ReleaseNote from Market_APK_Metadata where ID="+str(market_apk_id))
				info = cursor.fetchall()[0]
				package_content.append((info[0], info[1]))
				print("Get "+package+" In "+market_name[market])
		content.append(package_content)
	result = []
	for i in range(len(market_list)):
		result.append([0] * len(market_list))
	for i in range(len(market_list)):
		for j in range(i+1, len(market_list)):
			ed_sum = 0
			cnt = 0
			for k in range(len(package_list)):
				if content[k][i][0] != None and content[k][j][0] != None:
					if content[k][i][1] != None and content[k][j][1] != None:
						str1 = content[k][i][0]+content[k][i][1]
						str2 = content[k][j][0]+content[k][j][1]
						ed = edit_distance(str1, str2)
					else:
						str1 = content[k][i][0]
						str2 = content[k][j][0]
						ed = edit_distance(str1, str2)
						if content[k][i][1] != None:
							str1 = content[k][i][0]+content[k][i][1]
							str2 = content[k][j][0]
							ed = min(edit_distance(str1, str2), ed)
						if content[k][j][1] != None:
							str1 = content[k][i][0]
							str2 = content[k][j][0]+content[k][j][1]
							ed = min(edit_distance(str1, str2), ed)
					ed_sum += ed
					cnt += 1	
			result[i][j] = result[j][i] = ed_sum/cnt
			print("Edit Distance Between "+market_name[market_list[i]]+" and "+market_name[market_list[j]]+" = "+str(result[i][j]))
	fout = open('Edit_Distance.csv', 'w')
	for j in range(len(market_list)):
		fout.write(','+market_name[market_list[j]])
	fout.write("\n")
	for i in range(len(market_list)):
		fout.write(market_name[market_list[i]])
		for j in range(len(market_list)):
			fout.write(","+str(result[i][j]))
		fout.write("\n")
	fout.close()
	ed_sum = [0] * len(market_list)
	for i in range(len(market_list)):
		for j in range(len(market_list)):
			ed_sum[i] += result[i][j]
	tag = [True] * len(market_list)
	market_left = len(market_list)
	prev_worst = -1
	while market_left > 2:
		cur_worst = -1
		for i in range(len(market_list)):
			if tag[i] and (cur_worst == -1 or ed_sum[i] > ed_sum[cur_worst]):
				cur_worst = i
		print('Current Worst Market is '+market_name[market_list[cur_worst]])
		if prev_worst != -1:
			for i in range(len(market_list)):
				if tag[i]:
					ed_sum[i] -= result[i][prev_worst]
		tag[cur_worst] = False
		prev_worst = cur_worst
		market_left -= 1
	for i in range(len(market_list)):
		if tag[i]:
			print('One of the Best Market is '+market_name[market_list[i]])