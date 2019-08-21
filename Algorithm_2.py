# Import the necessary modules.

import pandas as pd
import itertools

# Construct the timetable.

plan_df = pd.DataFrame(columns = ['Period', 'Room', 'Type', 'Exams', 'N', 'Spots', 'Durations'])

plan_df['Period'] = np.repeat(np.arange(len(period_df)) + 1, len(room_df))
plan_df['Room'] = room_df['Room'].tolist() * len(period_df)
plan_df['Type'] = room_df['Type'].tolist() * len(period_df)
plan_df['Spots'] = room_df['Capacity'].tolist() * len(period_df)
plan_df['N'] = [0] * len(period_df) * len(room_df)
plan_df['Exams'] = [[] for i in range(len(room_df) * len(period_df))]
plan_df['Durations'] = [set() for i in range(len(room_df) * len(period_df))]

colexams_df = exam_df[[e in exams for e in exam_df['Exam']]]
pc_exams_df = colexams_df[colexams_df['Room Type'] == 1]
oth_exams_df = colexams_df[colexams_df['Room Type'] == 0]
pc_room_df = room_df[room_df['Type'] == 1]
oth_room_df = room_df[room_df['Type'] == 0]

# A function that adds an exam to the timetable by specifying the room, period
# and exam number

def AddExam(plan_df, per, room, exam):
    i = int(np.where(plan_df['Period'].isin([per]) & plan_df['Room'].isin([room]))[0])
    plan_df['Exams'][i] += [exam]
    plan_df['N'][i] += int(exam_df.loc[exam_df['Exam'] == exam, 'N'])
    plan_df['Spots'][i] -= int(exam_df.loc[exam_df['Exam'] == exam, 'N'])
    plan_df['Durations'][i] = plan_df['Durations'][i].union(set(exam_df.loc[exam_df['Exam'] == exam, 'Duration'])) 
    return plan_df

adj = []
for i in range(len(spots_left)):
    cumsum = [0] + list(np.cumsum(spots_left))
    adj.append(list(np.arange(cumsum[i], cumsum[i + 1]) + 1))
    
colors_df['Adjacent'] = adj + [None] 

# First, schedule the preassigned exams   
    
for i in range(len(preassign_df)):
    exam = preassign_df.iloc[i][0]
    exam_n = int(exam_df.loc[exam_df['Exam'] == exam, 'N'])
    period = preassign_df.iloc[i][1]
    typ = int(exam_df.loc[exam_df['Exam'] == exam, 'Room Type'])
    dur = int(exam_df.loc[exam_df['Exam'] == exam, 'Duration'])
    cand_df = plan_df.loc[(plan_df['Period'] == period) & (plan_df['Type'] == typ) & 
                          pd.Series([dur in s or len(s) == 0 for s in plan_df['Durations']])]
    if not any(cand_df['Spots'] >= exam_n):
        cand_df = plan_df.loc[(plan_df['Period'] == period) & (plan_df['Type'] == typ)]
    max_index = np.where(cand_df['Spots'] == max(cand_df['Spots']))[0]
    room = cand_df.iloc[max_index]['Room']
    AddExam(plan_df, period, room, exam)
    
# Then, schedule the regular exams in the clusters/color groups. For exact
# details on the scheduling procedure, see Algorithm 2 in the dissertation
# file.    
    
for i in range(len(colors_df) - 1):
    color = colors_df['Color'][i]
    exams = set(colors_df['Members'][i]).difference(set(preassign_df['Exam']))
    exams_size = list(exam_df.sort_values(by = ['N'], ascending = False)['Exam'])
    exams = [e for e in exams_size if e in exams]
    adj = sorted(colors_df['Adjacent'][i], key = lambda x: abs(color - x))
    for per in adj:    
        for e in exams:
            cand_df = plan_df[plan_df['Period'] == per]
            typ = int(exam_df.loc[exam_df['Exam'] == e, 'Room Type'])
            dur = int(exam_df.loc[exam_df['Exam'] == e, 'Duration'])
            cand2_df = cand_df.loc[(plan_df['Type'] == typ) & 
                                   pd.Series([dur in s or len(s) == 0 for s in plan_df['Durations']])]
            exam_n = int(exam_df.loc[exam_df['Exam'] == e, 'N'])
            if any(cand2_df['Spots'] >= exam_n):
                max_index = np.where(cand2_df['Spots'] == max(cand2_df['Spots']))[0][0]
                room = cand2_df.iloc[max_index]['Room']
                AddExam(plan_df, per, room, e)
        exams = [e for e in exams if e not in list(itertools.chain(*plan_df['Exams']))]


       