# Import necessary modules

import numpy as np
import pandas as pd
import math
import itertools

# Create a dataframe with all the information about the cluster/colors.

colors_df = pd.DataFrame(columns = ['Color', 'Members', 'N Students', 'Spots'])

colors = []
members = []

# Construct a cluster for every period that contains a preassigned exam.

for c in set(preassign_df['Period']):
    colors.append(c)
    members.append(preassign_df.loc[preassign_df['Period'] == c, ['Exam']]['Exam'].values.tolist())

colors_df['Color'] = colors
colors_df['Members'] = members

total_cap = sum(room_df['Capacity'])
factor = 0.7  # Alpha
spots_left = []

# A function that computes the number of adjacent periods for a cluster.

def ComputeSpots(col, n_col):
    spots = [None] * len(col)
    for i in range(len(col)):
        if i == 0:
            spots[i] = col[i] + math.ceil((col[i + 1] - col[i] - 1) / 2)
        elif i == (len(col) - 1):
            spots[i] = (n_col - col[i]) + math.floor((col[i] - col[i - 1] - 1) / 2) + 1
        else:
            spots[i] = math.ceil((col[i + 1] - col[i] - 1) / 2) + math.floor((col[i] - col[i - 1] - 1) / 2) + 1
    return spots 

# Compute the available spots and add them to the dataframe
    
n_students = [[exam_df['N'][e - 1] for e in colors_df['Members'][c]] for c in range(len(colors_df))]
n_students = [sum(i) for i in n_students]    
spots_left = ComputeSpots(colors_df['Color'], len(period_df))
colors_df['Spots'] = list(np.round(factor * total_cap * np.array(spots_left) - np.array(n_students)))

# Add number of students to every cluster in the dataframe

colors_df['N Students'] = n_students

# Add the null cluster to the dataframe 

colors_df.loc[len(colors_df)]=[0, [], None, None]

colored = set(list(itertools.chain.from_iterable(colors_df['Members'][:len(colors_df) - 1])))

# A function that creates a dataframe about the uncolored exams/nodes based on 
# the dataframe about the clusters

def ConstructUnColMatrix(l_colored):
    uncolored = set(range(1, n_exam + 1)).difference(l_colored)  
    coldeg_matrix = np.delete(np.delete(conflict_matrix, np.array(list(l_colored)) - 1, 0), 
                              np.array(list(uncolored)) - 1, 1)
    uncoldeg_matrix = np.delete(np.delete(conflict_matrix, np.array(list(l_colored)) - 1, 0), 
                                np.array(list(l_colored)) - 1, 1)
    l_uncol_df = pd.DataFrame(columns = ['Exam', 'Col Deg', 'Uncol Deg'])
    
    coldeg = []
    
    for c in range(len(uncolored)):    
        adj = set([list(l_colored)[s] for s in np.where([coldeg_matrix[c] > 0])[1]])
        coldeg.append(np.array([bool(set(s).intersection(adj)) for s in colors_df['Members'][:len(colors_df) - 1]]).sum())
    
    uncoldeg = [(uncoldeg_matrix[s] > 0).sum() for s in range(len(uncoldeg_matrix))]
    l_uncol_df['Exam'] = list(uncolored)
    l_uncol_df['Col Deg'] = coldeg
    l_uncol_df['Uncol Deg'] = uncoldeg
    l_uncol_df = l_uncol_df.sort_values(['Col Deg', 'Uncol Deg'], ascending = [False, False])
    return l_uncol_df

uncol_df = ConstructUnColMatrix(colored)

# A function that assigns an exam to a cluster and updates the cluster
# dataframe and the dataframe about the uncolored exams.

def AddColor(l_colors_df, l_uncol_df):
    i = 0
    while True:
        exam = l_uncol_df.iloc[i]['Exam']
        if exam not in l_colors_df['Members'][len(l_colors_df) - 1]:
            break
        i += 1
    colors_df.append([0, None, None, None])
    adj = set(np.where([s > 0 for s in conflict_matrix[exam - 1]])[0] + 1)
    poss_col = []
    add_col = None
    for col in range(len(l_colors_df) - 1):
        if len(set(adj).intersection(set(l_colors_df['Members'][col]))) == 0:
            poss_col.append(l_colors_df['Color'][col])
            cand_df = l_colors_df[l_colors_df['Color'].isin(poss_col)]
            add_col = list(cand_df[cand_df['Spots'] == max(cand_df['Spots'])]['Color'])[0]
    if add_col in list(l_colors_df['Color']) and list(l_colors_df.loc[l_colors_df['Color'] == add_col, 'Spots'])[0] > exam_df['N'][exam - 1]:
        l_colors_df.loc[l_colors_df['Color'] == add_col, 'Members'] += [exam]
        l_colors_df.loc[l_colors_df['Color'] == add_col, 'N Students'] += exam_df['N'][exam - 1]
        l_colors_df.loc[l_colors_df['Color'] == add_col, 'Spots'] -= exam_df['N'][exam - 1]
    else:
        l_colors_df.loc[l_colors_df['Color'] == 0, 'Members'] += [exam]
    l_colored = set(list(itertools.chain.from_iterable(l_colors_df['Members'][:len(l_colors_df) - 1])))
    l_uncol_df = ConstructUnColMatrix(l_colored)    
    return l_colors_df, l_uncol_df    

# Finally, assign all the exams to a cluster

for i in range(len(uncol_df)):
    (colors_df, uncol_df) = AddColor(colors_df, uncol_df)
    
# For the exact details on the scheduling procedure, see Algorithm 1 in the 
# dissertation file.
