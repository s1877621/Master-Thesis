# Import necessary modules

import numpy as np
import itertools
import pandas as pd  

# Construct a list with pairs containing periods on the same day

same_day = [[] for i in range(len(set(period_df['Day'])))]
last_day = 0
counter = -1

for i in range(len(period_df)):
    curr_day = period_df['Day'][i]
    if curr_day != last_day:
        counter += 1
    same_day[counter].append(i + 1)
    last_day = curr_day

# Similarly, construct a list for the overnight pairs

overnight = []
    
for i in range(len(period_df) - 1):
    bol_1 = int(period_df['Day'][i][:2]) == int(period_df['Day'][i + 1][:2]) - 1
    bol_2 = period_df['Time'][i] == list(set(period_df['Time']))[0]
    bol_3 = period_df['Time'][i + 1] == list(set(period_df['Time']))[1]
    if(bol_1 and bol_2 and bol_3):
        overnight.append([i + 1, i + 2])

# Same for the morning and afternoon

morning = []
afternoon = []

for i in range(len(period_df)):
    if period_df['Time'][i] == list(set(period_df['Time']))[0]:
        afternoon.append(i + 1)
    else:
        morning.append(i + 1)

# Construct a list with pairs for which a penalty is incurred if a student has
# to take an exam in both periodss

s = 3 # We consider 3 periods exam spread

spread_per = [[[i, i + j] for i in range(1, len(period_df) - (j - 1))] for j in list(range(1, s + 1))]
spread_per = list(itertools.chain(*spread_per))  

# Obtain the students with the disabilities

morning_dis = list(disability_df.loc[disability_df['Disability'] == 'MORNING', 'Student'])
afternoon_dis = list(disability_df.loc[disability_df['Disability'] == 'AFTERNOON', 'Student'])
consec_dis = list(disability_df.loc[disability_df['Disability'] == 'NO_CONSECUTIVE', 'Student'])
twoday_dis = list(disability_df.loc[disability_df['Disability'] == 'TWO_DAY', 'Student'])      
 

# A function which computes the total penalty score for a given timetable. For
# more details, see Section 4.1 in the dissertation file.

def ComputeScore(plan_df):       
    same_day_pen = 0
    overnight_pen = 0
    spread_pen = 0
    morning_pen = 0
    afternoon_pen = 0
    consec_pen = 0
    twoday_pen = 0        
    
    for case in same_day:
        if len(case) == 1:
            break
        exams_1 = list(itertools.chain(*plan_df[plan_df['Period'] == case[0]]['Exams']))
        exams_2 = list(itertools.chain(*plan_df[plan_df['Period'] == case[1]]['Exams']))
        students_1 = set()
        for e in exams_1:
            students_1 = students_1.union(set(exam_df['Students'][e - 1]))
        students_2 = set()
        for e in exams_2:
            students_2 = students_2.union(set(exam_df['Students'][e - 1]))
        pen = len(students_1.intersection(students_2)) * int(weights_df[weights_df['Weight'] == 'TWO_IN_A_ROW_DAY']['Parameters'])
        same_day_pen += pen
        
        
    for case in overnight:
        exams_1 = list(itertools.chain(*plan_df[plan_df['Period'] == case[0]]['Exams']))
        exams_2 = list(itertools.chain(*plan_df[plan_df['Period'] == case[1]]['Exams']))
        students_1 = set()
        for e in exams_1:
            students_1 = students_1.union(set(exam_df['Students'][e - 1]))
        students_2 = set()
        for e in exams_2:
            students_2 = students_2.union(set(exam_df['Students'][e - 1]))
        pen = len(students_1.intersection(students_2)) * int(weights_df[weights_df['Weight'] == 'TWO_IN_A_ROW_NIGHT']['Parameters'])
        overnight_pen += pen
    
    
    for case in spread_per:
        exams_1 = list(itertools.chain(*plan_df[plan_df['Period'] == case[0]]['Exams']))
        exams_2 = list(itertools.chain(*plan_df[plan_df['Period'] == case[1]]['Exams']))
        students_1 = set()
        for e in exams_1:
            students_1 = students_1.union(set(exam_df['Students'][e - 1]))
        students_2 = set()
        for e in exams_2:
            students_2 = students_2.union(set(exam_df['Students'][e - 1]))
        pen = len(students_1.intersection(students_2)) * int(weights_df[weights_df['Weight'] == 'PERIOD_SPREAD']['Parameters'])
        spread_pen += pen
    
    for stud in morning_dis:
        exams = list(students_df[students_df['Student'] == stud]['Exams'])[0]
        per = [int(plan_df[[f in e for e in plan_df['Exams']]]['Period']) for f in exams]
        viol = sum([p not in morning for p in per])
        morning_pen += viol * int(weights_df[weights_df['Weight'] == 'DIS_MORNING']['Parameters'])
        
    for stud in afternoon_dis:
        exams = list(students_df[students_df['Student'] == stud]['Exams'])[0]
        per = [int(plan_df[[f in e for e in plan_df['Exams']]]['Period']) for f in exams]
        viol = sum([p not in morning for p in per])
        afternoon_pen += viol * int(weights_df[weights_df['Weight'] == 'DIS_AFTERNOON']['Parameters'])    
    
    for stud in consec_dis:   
        exams = list(students_df[students_df['Student'] == stud]['Exams'])[0]
        per = [int(plan_df[[f in e for e in plan_df['Exams']]]['Period']) for f in exams]
        per = sorted(per)
        viol = sum([per[i + 1] - per[i] < 2 for i in range(len(per) - 1)])
        consec_pen += viol * int(weights_df[weights_df['Weight'] == 'DIS_NO_CONSECUTIVE']['Parameters'])
    
    for stud in twoday_dis:
        exams = list(students_df[students_df['Student'] == stud]['Exams'])[0]
        per = [int(plan_df[[f in e for e in plan_df['Exams']]]['Period']) for f in exams]
        per = sorted(per)
        viol = sum([[per[i], per[i + 1]] in same_day for i in range(len(per) - 1)])
        twoday_pen += viol * int(weights_df[weights_df['Weight'] == 'DIS_TWO_DAY']['Parameters'])             
      
    total_pen = same_day_pen + overnight_pen + spread_pen + morning_pen + afternoon_pen + consec_pen + twoday_pen  
    return total_pen