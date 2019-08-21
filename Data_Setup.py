# Import necessary modules

import pandas as pd
import numpy as np
import itertools

# First, set the indices for the input data file

lines = [line.rstrip('\n') for line in open('Exam1_Edi.txt')]

index_exams = [idx for idx, s in enumerate(lines) if '[Exams:' in s][0]
index_periods = [idx for idx, s in enumerate(lines) if '[Periods:' in s][0]
index_rooms = [idx for idx, s in enumerate(lines) if '[Rooms:' in s][0]
index_periodhard = [idx for idx, s in enumerate(lines) if '[PeriodHard' in s][0]
index_preassign = [idx for idx, s in enumerate(lines) if '[Pre' in s][0]
index_disability = [idx for idx, s in enumerate(lines) if '[Dis' in s][0]
index_weight = [idx for idx, s in enumerate(lines) if '[Ins' in s][0]

# Create an exam dataframe containing all the data about the exams
exam_data = lines[(index_exams + 1):index_periods]    

exam_df = pd.DataFrame(columns=['Exam', 'Room Type', 'Students', 'N', 'Duration'])
exam_df['Exam'] = list(range(1, (len(exam_data) + 1)))

roomtypes = []
durations = []
students = []
N_students = []
for s in exam_data:
    single_exam = [int(i) for i in s.split(',')]
    durations.append(single_exam[0])
    roomtypes.append(single_exam[1])
    students.append(single_exam[2:])
    N_students.append(len(single_exam) - 2)
    
exam_df['Duration'] = durations    
exam_df['Students'] = students
exam_df['Room Type'] = roomtypes
exam_df['N'] = N_students

# Similary, create a dataframe for all the periods

period_data = lines[(index_periods + 1):index_rooms]

period_df = pd.DataFrame(columns = ['Period', 'Day', 'Time'])
period_df['Period'] = list(range(1, (len(period_data) + 1)))

periods = []
days = []
times = []

for s in period_data:
    single_period = [str(i) for i in s.split(', ')]
    days.append(single_period[0])
    times.append(single_period[1])
    
period_df['Day'] = days
period_df['Time'] = times

# Dataframe about the rooms

room_data = lines[(index_rooms + 1):index_periodhard]

room_df = pd.DataFrame(columns = ['Room', 'Capacity', 'Type'])
room_df['Room'] = list(range(1, (len(room_data) + 1))) 

capacities = []
roomtypes = []

for s in room_data:
    single_room = [int(i) for i in s.split(',')]
    capacities.append(single_room[0])
    roomtypes.append(single_room[1])

room_df['Capacity'] = capacities
room_df['Type'] = roomtypes   
    
periodhard_data = lines[(index_periodhard + 1):index_preassign]

periodhard_df = pd.DataFrame(columns = ['Type', 'Exam 1', 'Exam 2']) 

types = []
exams_1 = []
exams_2 = []

# Dataframe about all the period related hard constraints

for s in periodhard_data:
    single_hardcons = [i for i in s.split(', ')]
    types.append(single_hardcons[1])
    exams_1.append(int(single_hardcons[0]))
    exams_2.append(int(single_hardcons[2]))    

periodhard_df['Type'] = types
periodhard_df['Exam 1'] = exams_1
periodhard_df['Exam 2'] = exams_2

preassign_data = lines[(index_preassign + 1):index_disability]

# Dataframe about all the preassignments

preassign_df = pd.DataFrame(columns = ['Exam', 'Period']) 

exams = []
periods = []

for s in preassign_data:
    single_preassign = [i for i in s.split(', ')]
    exams.append(int(single_preassign[0]))
    periods.append(int(single_preassign[1])) 

preassign_df['Exam'] = exams
preassign_df['Period'] = periods

# If an exam is an preassignment and needs to be scheduled with another exam,
# we can als preassign the other exam.

exam_coin = periodhard_df.loc[periodhard_df['Type'] == 'EXAM_COINCIDENCE', 
                              ['Exam 1', 'Exam 2']].values.tolist()

for c in exam_coin:
    if c[0] in list(preassign_df['Exam']) and c[1] not in list(preassign_df['Exam']):
        preassign_df.loc[len(preassign_df)] = ([c[1], int(preassign_df.loc[preassign_df['Exam'] == c[0], ['Period']].values)])
    if c[1] in list(preassign_df['Exam']) and c[0] not in list(preassign_df['Exam']):
        preassign_df.loc[len(preassign_df)] = ([c[0], int(preassign_df.loc[preassign_df['Exam'] == c[1], ['Period']].values)])        
        

# Dataframe about all disabilities

disability_data = lines[(index_disability + 1):index_weight]

disability_df = pd.DataFrame(columns = ['Student', 'Disability'])

students = []
disabilities = []

for s in disability_data:
    single_disability = [i for i in s.split(', ')] 
    students.append(int(single_disability[0]))
    disabilities.append(single_disability[1])

disability_df['Student'] = students
disability_df['Disability'] = disabilities   

# Dataframe about the institutional weightings   

weights_data = lines[(index_weight + 1):len(lines)]

weights_df = pd.DataFrame(columns = ['Weight', 'Parameters'])

weights = []
values = []

for s in weights_data:
    single_weight = [i for i in s.split(',')]
    weights.append(single_weight[0])
    values.append(int(single_weight[1]))

weights_df['Weight'] = weights
weights_df['Parameters'] = values

# Dataframe about all the students

all_students = set(itertools.chain(*exam_df['Students'])) 

students = []
exams = []
for s in all_students:
    students.append(s)
    exams.append(list(exam_df.loc[[s in stud for stud in exam_df['Students']], 'Exam']))
    
students_df = pd.DataFrame(columns = ['Student', 'Exams'])
students_df['Student'] = students
students_df['Exams'] = exams  

# Construction of the conflict matrix

n_exam = len(exam_df)
conflict_matrix = np.empty([n_exam, n_exam])

for e1 in range(n_exam):
    s_e1 = exam_df['Students'][e1]
    for e2 in range(n_exam):
        s_e2 = exam_df['Students'][e2]
        conflict_matrix[e1, e2] = len(set(s_e1).intersection(set(s_e2)))
    conflict_matrix[e1, e1] = 0    
    
for e in range(len(periodhard_df)):
    if periodhard_df['Type'][e] == 'EXAM_COINCIDENCE':
        e1 = periodhard_df['Exam 1'][e] - 1
        e2 = periodhard_df['Exam 2'][e] - 1
        newsum = conflict_matrix[e1] + conflict_matrix[e2]
        conflict_matrix[e1] = newsum
        conflict_matrix[:, e1] = newsum
        conflict_matrix[e2] = newsum
        conflict_matrix[:, e2] = newsum
        conflict_matrix[e1, e2] = 0
        conflict_matrix[e2, e1] = 0
        exam_df['N'][e1] += exam_df['N'][e2]
        exam_df['N'][e2] = 0
        exam_df['Students'][e1] += exam_df['Students'][e2]
        exam_df['Students'][e2] = []


        
    