

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

def surprisingly_popular(choice_counts, percents):
	avg_percs = np.zeros(len(percents[0]))
	for i in range(len(avg_percs)):
		summ = 0
		for j in range(len(percents)):
			summ += percents[j][i]
		i_avg = summ / len(percents)
		avg_percs[i] = i_avg
	#print(str(avg_percs[i]))

	actual_percs = [(choice_count / sum(choice_counts)) for choice_count in choice_counts]
	scores = [actual_percs[i] - avg_percs[i] for i in range(len(choice_counts))]

	#print("actual"+str(actual_percs))
	#print("avg" + str(avg_percs))
	#print("score" + str(scores))

	winner = 0
	for i in range(len(scores)):
		if scores[i] > scores[winner]:
			winner = i
	return chr(winner + 65)

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
		data.append((ord(choice), perc))
		total += 1
	print(str(data))
	#print(str(choice_counts))
	true_answer = chr(correct_answer)
	#plur_winner = plurality(choice_counts)
	#sp_winner = surprisingly_popular(choice_counts, data)
	#print(str([true_answer, plur_winner, sp_winner]))
	file.close()
	#return (true_answer, plur_winner, sp_winner)

def parse(args):
	i = 0
	rows = []
	while os.path.exists(DATA_PATH + args.folder + "/question" + str(i) + ".txt"):
		#print("yes")
		if i == 1:
			break
		rows.append(parse_file("question" + str(i) + ".txt", args))
		i += 1
	plur_count = 0
	sp_count = 0
	for j in range(len(rows)):
		if rows[j][0] == rows[j][1]:
			plur_count += 1
		if rows[j][0] == rows[j][2]:
			sp_count += 1
	print(plur_count / len(rows))
	print(sp_count / len(rows))
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



















