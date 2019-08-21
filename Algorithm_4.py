# Import necessary modules

from timeit import default_timer as timer

# A function that removes an exam from the timetable by specifying the room, 
# period and exam.

def RemoveExam(plan_df, per, room, exam):
    i = int(np.where(plan_df['Period'].isin([per]) & plan_df['Room'].isin([room]))[0])
    plan_df['Exams'][i] = [x for x in plan_df['Exams'][i] if x != exam]
    plan_df['N'][i] -= int(exam_df.loc[exam_df['Exam'] == exam, 'N'])
    plan_df['Spots'][i] += int(exam_df.loc[exam_df['Exam'] == exam, 'N'])
    plan_df['Durations'][i] = set([int(exam_df.loc[exam_df['Exam'] == e, 'Duration']) for e in plan_df['Exams'][i]]) 
    return plan_df

# A list that keeps track of which slots we can move exams to.

poss_slots = list(range(len(plan_df)))

# A function that moves an exam by considereing the penalty function. For more
# details, see Algorithm 4 in the dissertation file.

def MoveExam(plan_df, poss_slots):
    curr_most = 0
    for elem in poss_slots:
        if plan_df.loc[elem, 'Spots'] > curr_most:
            most_spots = plan_df.loc[elem]
            slot = elem
            curr_most = most_spots['Spots']
        
    infeas = list(itertools.chain(*plan_df[plan_df['Period'] == most_spots['Period']]['Exams']))
    ind_infeas = list(np.array(infeas) - 1)
    confl = [(np.where(conflict_matrix[i] > 0)[0] + 1).tolist() for i in ind_infeas]        
    confl = set(list(itertools.chain(*confl))).union(set(preassign_df['Exam'])).union(set(preassign_df['Exam'])).union(set(list(itertools.chain(*exam_coin))))
    feas_df = exam_df[(exam_df['Room Type'] == most_spots['Type']) & (exam_df['N'] < most_spots['Spots'])]
    
    if len(most_spots['Durations']) > 0:
        feas_df = feas_df[feas_df['Duration'] == list(most_spots['Durations'])[0]]

    feas_df = feas_df[[e not in confl for e in feas_df['Exam']]]    

    curr_score = ComputeScore(plan_df)
    decr = []
    print(curr_score)
    for i in range(len(feas_df)):
        exam = feas_df.iloc[i]['Exam']
        old_exam = plan_df[[exam in e for e in plan_df['Exams']]]
        RemoveExam(plan_df, old_exam['Period'], old_exam['Room'], exam)
        AddExam(plan_df, most_spots['Period'], most_spots['Room'], exam)
        score = ComputeScore(plan_df)
        decr.append(curr_score - score)
        RemoveExam(plan_df, most_spots['Period'], most_spots['Room'], exam)
        AddExam(plan_df, old_exam['Period'], old_exam['Room'], exam)
    best_ind = np.where([i == max(decr) for i in decr])[0][0]
    exam = feas_df.iloc[best_ind]['Exam']
    old_exam = plan_df[[exam in e for e in plan_df['Exams']]]    
    print(exam)
    print('Current period ', most_spots['Period'])
    print('Current room ', most_spots['Room'])

    if max(decr) > 0:
        RemoveExam(plan_df, old_exam['Period'], old_exam['Room'], exam)
        AddExam(plan_df, most_spots['Period'], most_spots['Room'], exam)    
    else:
        poss_slots.remove(slot)
        print(len(poss_slots))
    return plan_df, poss_slots


# Set up the timer
start_time = timer()
times = []
scores = []
elapsed = 0

# Keep moving exams until the time limit is reached

while elapsed < 100:
    MoveExam(plan_df, poss_slots)
    scores.append(ComputeScore(plan_df))
    elapsed = timer() - start_time
    print(elapsed)
    times.append(elapsed)
