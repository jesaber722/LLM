#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 12:10:41 2023

@author: miceland
"""

import numpy as np
import pandas as pd
import os


def sp(p, c):
    """Selects the true world, a_{k}, based on Surpisingly Popular
    
    Parameters
    __________
    p : 2D numpy array
        Probability distribution where p[k][i] represents the probability
        Pr(V = v_{i + 1} | S = s_{k + 1})
        
    c: 1D numpy array
        Vote counts where c[k] is the number of votes given to v_{k + 1}
        
    Returns
    _______
    int
        The value k in {1, 2, ..., m} with the greatest prediction-
        normalized vote
    """
    
    m = len(c) # m is the number of worlds
    n = np.sum(c)  # n is the total number of repondents
    
    maxK = -1
    maxPredictionNormalized = -1
    
    for k in range(m):
        
        currPredictionNormalized = 0
        
        for i in range(m):
            if (p[i][k] > 0):
                currPredictionNormalized += (p[k][i] / p[i][k])
        currPredictionNormalized *= (c[k] / n)
        
        if (currPredictionNormalized > maxPredictionNormalized):
            maxPredictionNormalized = currPredictionNormalized
            maxK = k;
        
    return maxK + 1

def plurality(c):
    """Selects the true world, a_{k}, based on simple plurality
    
    Parameters
    __________
    c: 1D numpy array
        Vote counts where c[k] is the number of votes given to v_{k + 1}
        
    Returns
    _______
    int
        The value k in {1, n, ..., m} with the most votes
    """
    
    result = -1
    maxVotes = -1
    
    for k in range(len(c)):
        if (c[k] > maxVotes):
            result = k
            maxVotes = c[k]
            
    return result + 1

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
    df = pd.read_csv(file, nrows=1)
    correct = df.columns.values[0][0]
    numAnswers = int(df.columns.values[0][1:])
    
    # Correct file into csv format
    lines = None
    with open(file, 'r') as f:
        lines = f.readlines()
    with open(file, 'w') as f:
        for line in lines:
            f.write(line.replace('###', ','))
    
    df = pd.read_csv(file, names=[i for i in range(numAnswers + 1)])
    
    # Drop erroneous rows
    for i in df.index:
        if (df.at[i, 0] == 'ERROR'):
            df = df.drop(i)
    df = df.drop(0)
    df = df.reset_index(drop=True)
    
    # Normalize percentages
    for i in df.index:
        total = sum(df.iloc[i, 1:])
        for j in range(1, len(df.iloc[i])):
            df.iloc[i, j] = (df.iloc[i, j] / total) * 100
            
    # create probability matrix
    p = np.zeros((numAnswers, numAnswers))
    c = np.zeros(numAnswers)
    
    for i in df.index:
        ans = df.at[i, 0]
        ansInt = ord(ans) - ord('A')
        
        if (ansInt >= numAnswers):
            continue
        
        c[ansInt] += 1
        for j in range(1, len(df.iloc[i])):
            p[ansInt][j - 1] += (df.iloc[i, j] - p[ansInt][j - 1]) / c[ansInt]
            
    spAnswer = sp(p, c)
    plurAnswer = plurality(c)
    
    return (spAnswer, plurAnswer, correct)

"""Main loop"""
path = 'multiple_choice_data_set/processed/'
files = os.listdir(path)

result = np.zeros((2, 2))
nAgree = 0
nDisagree = 0

for file in files:
    spAnswer, plurAnswer, correct = read(path + file)
    
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
        
with open('sp_results_1.txt', 'w') as f:
    f.write('Both correct: {}\n'.format(int(result[1][1])))
    f.write('SP correct, Plurality incorrect: {}\n'.format(int(result[1][0])))
    f.write('SP incorrect, Plurality correct: {}\n'.format(int(result[0][1])))
    f.write('Neither correct: {}\n\n'.format(int(result[0][0])))
    
    f.write('Number of agreements: {}\n'.format(nAgree))
    f.write('Number of disagreements: {}\n\n'.format(nDisagree))
    
    f.write('Implementation Notes:\n')
    f.write('* Ties are broken lexicographically\n')
    f.write('* Terms with division by zero in SP are disregarded\n')
    f.write('* Percentages are normalized\n')
    f.write('* Multiple choice answers out of range are disregarded (not very common)\n')