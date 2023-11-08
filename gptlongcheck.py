

DATA_PATH = "C:/Users/jesab/gpt/runs/"
import numpy as np
import os
import argparse

def plurality(choice_counts):
	#print(str(choice_counts))
	max_count = 0
	for i in range(len(choice_counts)):
		if choice_counts[i] > choice_counts[max_count]:
			max_count = i
	return chr(max_count + 65)

def surprisingly_popular(choice_counts, data):
	relevant = []
	total_votes = sum(choice_counts)
	for i in range( len(choice_counts)):
		if choice_counts[i] > 0:
			relevant.append(i)
	orig_to_relevant = {}
	for i in range(len(relevant)):
		orig_to_relevant[relevant[i]] = i
	
	relevant_percs = [[] for _ in range( len(relevant))]
	for data_point in data:
		relevant_percs[orig_to_relevant[data_point[0]]].append(data_point[1])
	average_percs = np.zeros(len(relevant))
	for i in range(len(relevant)):
		average_percs[i] = sum(relevant_percs[i])/len(relevant_percs[i])
		if average_percs[i] > 1:
			average_percs[i] = 1
		if average_percs[i] < 0:
			average_percs[i] = 0
	matrix = np.zeros((len(relevant), len(relevant)))
	for i in range(len(relevant)):
		for j in range(len(relevant)):
			if i == j:
				matrix[i][j] = average_percs[i]
			else:
				matrix[i][j] = (1 - average_percs[i])/(len(relevant)-1)
	scores = np.zeros(len(relevant))
	for i in range(len(relevant)):
		score = 0
		for j in range(len(relevant)):
			if matrix[j][i] != 0:
				score += matrix[i][j]/matrix[j][i]
		score *= choice_counts[relevant[i]]/total_votes
		scores[i] = score

	max_ind = 0
	#print(str(scores))
	#print(str(scores[0]))
	#print(str(scores[1]))
	#print(scores[2])
	for i in range(len(relevant)):
		print(str(i))
		if scores[i] > scores[max_ind]:
			max_ind = i
	return chr(relevant[max_ind] + 65)



def parse_file(filename, args):
	#print("hello")
	file = open(DATA_PATH + args.folder + "/" + filename, encoding='UTF-8')
	print(filename)
	content = file.read()
	lines = content.split("\n")
	answers = lines[1:len(lines)-1]
	first = lines[0]
	correct_answer = ord(first[0])
	worlds = int(first[1:])
	total = 0
	choice_counts = np.zeros(worlds)
	data = []
	for answer in answers:
		if answer == "ERROR":
			continue
		choice, unparsed_percent = answer.split('###')
		if ord(choice) - 65 >= len(choice_counts) or ord(choice) - 65 < 0:
			continue
		choice_counts[ord(choice) - 65] += 1
		perc = float(unparsed_percent)
		perc = min(100, perc)
		perc /= 100
		data.append((ord(choice) - 65, perc))
		total += 1
	#print(str(data))
	#print(str(choice_counts))
	true_answer = chr(correct_answer)
	plur_winner = plurality(choice_counts)
	sp_winner = surprisingly_popular(choice_counts, data)
	print(str([true_answer, plur_winner, sp_winner]))
	file.close()
	return (true_answer, plur_winner, sp_winner)

def parse(args):
	i = 0
	rows = []
	while os.path.exists(DATA_PATH + args.folder + "/question" + str(i) + ".txt"):
		#print("yes")
		rows.append(parse_file("question" + str(i) + ".txt", args))
		i += 1
	plur_count = 0
	sp_count = 0
	print(str(rows))
	different = []
	for j in range(len(rows)):
		if rows[j][0] == rows[j][1]:
			plur_count += 1
		if rows[j][0] == rows[j][2]:
			sp_count += 1
		if rows[j][1] != rows[j][2]:
			different.append(j)
	print(plur_count / len(rows))
	print(sp_count / len(rows))
	print(str(different))
	print("Length: " + str(len(different)))
	for q in different:
		print("Question " + str(q))
		print(str(rows[q]))
	pass


def main():
	parser = argparse.ArgumentParser(description="Your program description here.")
	parser.add_argument("folder", type=str)
	parser.add_argument("--destination", type=str, default="")
	args = parser.parse_args()
	if args.destination == "":
		args.destination = args.folder + "_results"
	if not os.path.exists(DATA_PATH + args.destination):
		os.makedirs(DATA_PATH + args.destination)
	else:
		print("ERROR: path exists")
		#return
	print("hi")
	print(DATA_PATH + args.destination)
	parse(args)



if __name__ == '__main__':
	main()



















