#!/usr/bin/env python
"""
Analyze normalized exam results
    - If multiple versions, use Normalize first

"""
import sys
import math
import argparse
import csv

"Create and configure the command-line argument parser"
parser = argparse.ArgumentParser(description='Exam Result Normalizer')
parser.add_argument('infile', type=argparse.FileType('r'),
                    help='Exam result file (csv format)')
parser.add_argument('--plot', action='store_true', help='Plot stuff!')
parser.add_argument('--nskip', type=int, default=0, help='Number to skip')
args = parser.parse_args()


"Read input file"
q_list = None
students = []
scores = []
reader = csv.DictReader(args.infile)
skip = list(range(args.nskip))

for row in reader:

    "Get the list of questions (not counting first), if not done already"
    if not q_list:
        q_list = reader.fieldnames[5:]

    "Iterate over the question columns"
    responses = []
    score = 0
    for q, qn in enumerate(q_list):
        
        "Get the response to this question"
        a = row[qn]

        "Handle the first question differently"
        if q in skip:
            "If wrong, skip this student"
            if a != '1':
                print('WARNING: Wrong response for version number, skipping student')
                break

        else:
            "Increment score"
            if a == '1':
                score += 1

            "Save response"
            responses.append(a)
    
    "Save data for this student"        
    if responses:
        scores.append(score)
        students.append({'score': score, 'responses': responses})

"This is the number of student responses (with correct version number)"
n_s = len(students)

"This is the number of questions"
for i in skip:
    q_list.pop(0)  # now we can remove the first question
n_q = len(q_list)

"Get the sums and min/max"
sum_s1 = 0
sum_s2 = 0
num_s = 0
min_s = sys.maxsize
max_s = -sys.maxsize - 1
for student in students:
    s = student['score']
    num_s += 1
    sum_s1 += s
    sum_s2 += s**2
    
    if s < min_s:
        min_s = s
    if s > max_s:
        max_s = s

"Calculate the average and std dev"
avg = sum_s1/num_s
sig = math.sqrt((num_s*sum_s2 - sum_s1**2)/(num_s*(num_s-1)))

"Prep the responses"
N_A = []
N_B = []
N_C = []
N_D = []
N_E = []
N_all = []
for q in q_list:
    N_A.append(0)
    N_B.append(0)
    N_C.append(0)
    N_D.append(0)
    N_E.append(0)
    N_all.append(0)

"Now fill the responses"
for s in students:
    for q, a in enumerate(s['responses']):
        if a == '1':
            N_A[q] += 1
            N_all[q] += 1
        elif a == '2':
            N_B[q] += 1
            N_all[q] += 1
        elif a == '3':
            N_C[q] += 1
            N_all[q] += 1
        elif a == '4':
            N_D[q] += 1
            N_all[q] += 1
        elif a == '5':
            N_E[q] += 1
            N_all[q] += 1

pq = 0
print('{:>6s} {:>3s} | {:^13s} | {:^13s} | {:^13s} | {:^13s} | {:^13s}'.format('Q', 'N', 'A', 'B', 'C', 'D', 'E'))
print('------------------------------------------------------------------------------------------')
for q, qn in enumerate(q_list):
    qs = str(q+1)
    
    d = N_A[q]/N_all[q]   
    num_c = N_A[q]  
    num_w = N_all[q] - num_c   

    pq += d*(1-d)

    sum_a = 0
    sum_b = 0
    sum_c = 0
    sum_d = 0
    sum_e = 0
    for student in students:
        s = student['score']
        a = student['responses'][q]
            
        if a == '1':
            sum_a += s
        elif a == '2':
            sum_b += s
        elif a == '3':
            sum_c += s
        elif a == '4':
            sum_d += s
        elif a == '5':
            sum_e += s
    
    avg_a_c = 0
    if N_A[q] > 0:
        avg_a_c = sum_a/N_A[q]
    avg_a_w = 0
    if N_A[q] < N_all[q]:
        avg_a_w = (sum_b + sum_c + sum_d + sum_e)/(N_all[q] - N_A[q])
    del_a = avg_a_c-avg_a_w

    avg_b_c = 0
    if N_B[q] > 0:
        avg_b_c = sum_b/N_B[q]
    avg_b_w = 0
    if N_B[q] < N_all[q]:
        avg_b_w = (sum_a + sum_c + sum_d + sum_e)/(N_all[q] - N_B[q])
    del_b = avg_b_c-avg_b_w

    avg_c_c = 0
    if N_C[q] > 0:
        avg_c_c = sum_c/N_C[q]
    avg_c_w = 0
    if N_C[q] < N_all[q]:
        avg_c_w = (sum_a + sum_b + sum_d + sum_e)/(N_all[q] - N_C[q])
    del_c = avg_c_c-avg_c_w

    avg_d_c = 0
    if N_D[q] > 0:
        avg_d_c = sum_d/N_D[q]
    avg_d_w = 0
    if N_D[q] < N_all[q]:
        avg_d_w = (sum_a + sum_b + sum_c + sum_e)/(N_all[q] - N_D[q])
    del_d = avg_d_c-avg_d_w

    avg_e_c = 0
    if N_E[q] > 0:
        avg_e_c = sum_e/N_E[q]
    avg_e_w = 0
    if N_E[q] < N_all[q]:
        avg_e_w = (sum_a + sum_b + sum_c + sum_d)/(N_all[q] - N_E[q])
    del_e = avg_e_c-avg_e_w

    cor_a = del_a*math.sqrt(N_A[q]*(N_all[q]-N_A[q])/(N_all[q]*(N_all[q]-1)))/sig
    cor_b = del_b*math.sqrt(N_B[q]*(N_all[q]-N_B[q])/(N_all[q]*(N_all[q]-1)))/sig
    cor_c = del_c*math.sqrt(N_C[q]*(N_all[q]-N_C[q])/(N_all[q]*(N_all[q]-1)))/sig
    cor_d = del_d*math.sqrt(N_D[q]*(N_all[q]-N_D[q])/(N_all[q]*(N_all[q]-1)))/sig
    cor_e = del_e*math.sqrt(N_E[q]*(N_all[q]-N_E[q])/(N_all[q]*(N_all[q]-1)))/sig
        
    f1 = 100*N_A[q]/N_all[q]
    f2 = 100*N_B[q]/N_all[q]
    f3 = 100*N_C[q]/N_all[q]
    f4 = 100*N_D[q]/N_all[q]
    f5 = 100*N_E[q]/N_all[q]
        
    print("{:6s} {:3d} | {:5.1f}% {:6.3f} | {:5.1f}% {:6.3f} | {:5.1f}% {:6.3f} | {:5.1f}% {:6.3f} | {:5.1f}% {:6.3f}".format(qn, N_all[q], f1, cor_a, f2, cor_b, f3, cor_c, f4, cor_d, f5, cor_e))

print('------------------------------------------------------------------------------------------')

"Calc the rest"
r20 = (n_q/(n_q-1))*(1-pq/sig**2)
stderr = sig*math.sqrt(1-r20)
range_s = max_s - min_s
range_sig = range_s/sig
range_stderr = range_s/stderr

err_on_mean = sig/math.sqrt(n_s)

print('Average = {:5.2f} +- {:4.2f} = ({:4.1f} +- {:3.1f})%'.format(avg, err_on_mean, 100*avg/n_q, 100*err_on_mean/n_q))
print('Standard error of measurement = {:4.2f}'.format(stderr))
print('Range = [{} - {}] = {} = {:4.2f} stderrs'.format(max_s, min_s, range_s, range_stderr))
print('KR20 = {:5.3f}'.format(r20))


if args.plot:
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt

    name = args.infile.name.split('/')[-1]
    lab = "{} Questions, {} Students".format(n_q, n_s)

    q1 = np.percentile(scores, 25)
    q2 = np.percentile(scores, 50)
    q3 = np.percentile(scores, 75)

    b0 = -0.5
    bins = []
    for i in range(n_q+2):
        b = b0 + i
        bins.append(b)

    sns.set(style="ticks")

    f, (ax_hist, ax_box) = plt.subplots(nrows=2, sharex='col',
                                        gridspec_kw={"height_ratios": (.9, .1)})

    sns.boxplot(x=scores, ax=ax_box, showmeans=True, notch=True, orient="h")
    sns.histplot(scores, bins=bins, ax=ax_hist, stat='density', kde=True, label=lab)

    ax_hist.set(xlim=[-0.5, n_q+0.5])
    ax_box.set(yticks=[])
    ax_hist.axvline(x=avg, alpha=0.3, color='red')
    ax_hist.axvspan(avg-0.5*stderr, avg+0.5*stderr, alpha=0.15, color='red')
    ax_hist.grid()
    ax_box.grid()
    plt.subplots_adjust(wspace=0, hspace=0)

    ax_hist.legend()
    f.suptitle(name)
    plt.show()
