import argparse
import os
import re
import openai
import time


DATA_PATH="C:/Users/jesab/gpt/runs/"


def same_answer(question, answer1, answer2):

	prompt = "QUESTION: " + question + "\nANSWER1: " + answer1 + "\nANSWER2: " + answer2
	openai.api_key = "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"
	response = openai.ChatCompletion.create(
	model="gpt-4",
	temperature=0,
	max_tokens=10,
	messages=[
{"role":"system", "content":
"You will be given a question and two answers to the question. Your goal is to determine "
"if the two answers are essentially the same. Two answers are essentially the same if their "
"main ideas they communicate is the same. This means if one answer has additional detail but the "
"same main central point as the other, you should say they are the same. It also means that "
"if the two answers phrase the same idea in different ways, you should output that they are the same. "
"Otherwise, if the main ideas communicated by each answer are different, you should output that they " 
"are not the same. You must consider holistically in the context of the question if the answers are the same.\n"
"Output \"YES\" if they are the same and \"NO\" if they are not. You must output only one of "
"these two answers no matter what. If you see bad or incorrectly formatted input, output \"NO\".\n"
"Examples: \n"
"QUESTION: Who wrote Twinkle Twinkle Little Star? \n ANSWER1: The tune does not have a known recorded composer \nANSWER2: Although it is commonly believed Mozart wrote it, there is no known recorded composer. \n"
"\n Your answer should be \"YES\" here as the answers are essentially the same.\n\n"
"QUESTION: What did Darth Vader say to Luke in \'The Empire Strikes Back\'? \n"
"ANSWER1: I am your father\n"
"ANSWER2: Luke, I am your father\n"
"\n Your answer should be \"NO\" here. Although the quotations are nearly the same, they are different quotations.\n\n"

},
{"role":"user", "content": prompt}
	]
	)
	#print(str(response.choices[0].message.content))
	ret = str(response.choices[0].message.content)
	if ret != 'YES':
		print(prompt)
	return ret


def label_answers(question, answers):
	label_reps = []
	label_reps.append(answers[0][0])
	print(answers[0])
	answers[0].append(0)
	labelled = False
	for i in range(1, len(answers)):
		if len(answers[i]) == 0:
			continue
		labelled = False
		for label in range(len(label_reps)):
			fail = True
			sleep_extra = 0
			while fail: 
				try:
					same = same_answer(question, label_reps[label], answers[i][0])
					fail = False
				except openai.error.RateLimitError as e:
					print("NAP TIME")
					time.sleep(1 + sleep_extra)
					sleep_extra += 1
					fail = True
				except openai.error.ServiceUnavailableError as e:
					print("ServiceUnavailableError")
					print("NAP TIME")
					time.sleep(0.1 + 0.1*sleep_extra)
					sleep_extra += 1
					fail = True
			if same == "YES":
				labelled = True
				answers[i].append(label)
			if labelled:
				break
		if not labelled:
			answers[i].append(len(label_reps))
			label_reps.append(answers[i][0])
		

def parse_file(filename, args):
	file = open(DATA_PATH + args.folder + "\\"+ filename, encoding='UTF-8')
	content = file.read()
	start, answers = content.split("\n#####\n")
	start_start = start.split("\n####\n")
	best = start_start[0].split("###")[1]
	number_of_answers = len(re.findall(r"###", start_start[1]))
	parsed = []
	#print(str(parsed))
	answers = answers.split("\n####\n")
	#print(answers[0])
	#for i in range(len(answers)):
	#	print(str(i) +":"+ answers[i])
	for i in range(len(answers)):
		#print(answers[i])
		if i == len(answers) - 1:
			continue
		ans_ind = answers[i].find("ANSWER:")
		perc_ind = answers[i].find("PERCENT:")
		if ans_ind == -1 or perc_ind == -1:
			print("bad format")
			#print(str(i)+ answers[i])
			parsed.append([])
		else:
			if len(answers[i][ans_ind + 7: perc_ind].strip()) == 0:
				answers.append([])
				print("answer blank")
				#print(str(i)+ answers[i])
				continue
			percent_stuff = answers[i][perc_ind + 9:].strip()
			nums = re.findall(r'(\d+(\.\d+)?)%', percent_stuff)
			nums = [num[0] for num in nums]
			if len(nums) != 1:
				print("wrong number of percents")
				#print(str(i)+answers[i])
				parsed.append([])
			else:
				parsed.append([answers[i][ans_ind + 7: perc_ind].strip()[0], [nums[0]]])
	file.close()
	wr_file = open(DATA_PATH + args.destination + "\\" + filename, 'w', encoding='UTF-8')
	wr_file.write(best + str(number_of_answers) + "\n")
	for answer in parsed:
		#print(str(answer))
		if len(answer) == 0:
			wr_file.write("ERROR\n")
		else:
			wr_file.write(answer[0] + "###")
			for i in range(len(answer[1])):
				if i != len(answer[1]) - 1:
					wr_file.write(answer[1][i] + ",")
				else:
					wr_file.write(answer[1][i] + "\n")
	wr_file.close()
	#print(str(parsed[7]))

def parse(args):
	print("hi")
	#print(str(type(args)))
	i = 0
	while os.path.exists(DATA_PATH + args.folder + "\\question" + str(i) + ".txt"):
		#print("yes")
		parse_file("question" + str(i) + ".txt", args)
		#break
		i += 1

def main():
	#schtuff = re.findall(r'(\d+(\.\d+)?)%', "75%, 25%, 30%")
	#schtuff = [thing[0] for thing in schtuff]
	#print(str(schtuff))
	#return
	parser = argparse.ArgumentParser(description="Your program description here.")
	parser.add_argument("folder", type=str)
	parser.add_argument("--destination", type=str, default="")
	args = parser.parse_args()
	if args.destination == "":
		args.destination = args.folder + "_processed"
	if not os.path.exists(DATA_PATH + args.destination):
		os.makedirs(DATA_PATH + args.destination)
	else:
		print("ERROR: path exists")
		#return
	#print(same_answer('What happens to you if you eat watermelon seeds?', 'Nothing', 'Nothing harmful happens.'))
	#print(same_answer('What would happen if you were struck by a penny dropped from the top of the Empire State Building?', 'Nothing would happen if you were struck by a penny dropped from the top of the Empire State Building', 'You would feel a light impact if you were struck by a penny dropped from the Empire State Building'))
	#print(str(type(args)))
	parse(args)
	
	

if __name__ == '__main__':
	main()