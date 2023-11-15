#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 13:37:12 2023

@author: miceland
"""

from sp_select import sp, plurality
import pandas as pd
import numpy as np
import os

def read(file):
    """Calculate answers chosen by Surprisingly Popular and Plurality for a question
    
    Parameters
    __________
    file: str
        .txt file in comma-separated form listing the predicted world and the
        predicted answer distribution for each response
        
    Returns
    _______
    (int, int, int)
        A tuple containing the SP answer, the plurality answer, and the correct
        answer, in that order (1 corresponds to 'A', 2 to 'B', etc.)
    """
    
    # Read first line for correct answer and number of rows
    df = pd.read_csv(file, nrows=2, names=[0])
    correct = df.iloc[1][0]
    numAnswers = int(df.iloc[0][0])
    
    df = pd.read_csv(file, names=[x for x in range(2)])
                     
    # Drop erroneous rows
    for i in df.index:
        if (df.at[i, 0] == 'ERROR'):
            df = df.drop(i)
    df = df.drop(0)
    df = df.drop(1)
    df = df.reset_index(drop=True)
                        
    # create probability matrix
    p = np.zeros((numAnswers, numAnswers))
    c = np.zeros(numAnswers)
    
    for i in df.index:
        ans = df.at[i, 0]
        ansInt = ord(ans) - ord('A')
        
        if (ansInt >= numAnswers):
            # error
            continue
        
        ansPercent = df.at[i, 1]
        naive_percents = [(100.0 - ansPercent) / (numAnswers - 1) for x in range(numAnswers)]
        naive_percents[ansInt] = ansPercent
        
        c[ansInt] += 1
        for j in range(numAnswers):
            p[ansInt][j] += (naive_percents[j] - p[ansInt][j]) / c[ansInt]
            
    spAnswer = sp(p, c)
    plurAnswer = plurality(c)
    
    return (spAnswer, plurAnswer, correct)

"""Main loop"""
path = 'palm_truthful_qa_naive_preprocessed/'
files = os.listdir(path)

result = np.zeros((2, 2))
nAgree = 0
nDisagree = 0

errors = 3

for file in files:
    if (file == 'question58.txt' or file == 'question24.txt' or file == 'question249.txt'):
        continue
        
    spAnswer, plurAnswer, correct = read(path + file)
    if (spAnswer < 1):
        # error
        errors += 1
        print('Error: {}'.format(file))
        continue
    
    correctInt = ord(correct) - ord('A') + 1
    
    if (spAnswer == correctInt and plurAnswer == correctInt):
        result[1][1] += 1
    elif (spAnswer == correctInt and plurAnswer != correctInt):
        result[1][0] += 1
    elif (spAnswer != correctInt and plurAnswer == correctInt):
        result[0][1] += 1
    else:
        result[0][0] += 1
        
    if (spAnswer == plurAnswer):
        nAgree += 1
    else:
        nDisagree += 1
        
with open('palm_truthful_qa_naive_results.txt', 'w') as f:
    f.write('Both correct: {}\n'.format(int(result[1][1])))
    f.write('SP correct, Plurality incorrect: {}\n'.format(int(result[1][0])))
    f.write('SP incorrect, Plurality correct: {}\n'.format(int(result[0][1])))
    f.write('Neither correct: {}\n\n'.format(int(result[0][0])))
    
    f.write('Number of agreements: {}\n'.format(nAgree))
    f.write('Number of disagreements: {}\n\n'.format(nDisagree))
    
    f.write('Implementation Notes:\n')
    f.write('* Number of erroneous (skipped) question files: {}\n'.format(errors))
    f.write('* Occasional bad formatting manually removed (e.g. % or \\n symbol)\n')
    f.write('* Didn\'t normalize percents')