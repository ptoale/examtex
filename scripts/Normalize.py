#!/usr/bin/env python
"""
Normalize exam results
    - Exam cfg file contains the mapping
    - Download csv files from testing services, these are the inputs
    - the output is a normalized csv file

"""
import argparse
import yaml
import csv

"Create and configure the command-line argument parser"
parser = argparse.ArgumentParser(description='Exam Result Normalizer')
parser.add_argument('config', type=argparse.FileType('r'),
                    help='Exam configuration file (YAML format)')
parser.add_argument('--files', nargs='+', type=argparse.FileType('r'), default=[],
                    help='Exam result files, must be in order! (csv format)')
parser.add_argument('--out', type=argparse.FileType('w'),
                    help='Exam normalized result file name')
args = parser.parse_args()


"Load the exam configuration"
try:
    cfg = yaml.safe_load(args.config)
except:
    parser.error('Config file does not appear to be valid YAML.')


"Fill the data needed to construct the mapping"
questions = {}
for vi, v in enumerate(cfg['versions']):
    q_key = "q{}".format(vi)
    p_key = "p{}".format(vi)

    for i, q in enumerate(v['order']):
        n_skipped = 0
        if q != 'np':
            for qd in v['questions']:
                if 'perm' in qd:
                    if q == qd['qid']:
                        if q not in questions:
                            questions[q] = {}
                        questions[q][q_key] = i
                        questions[q][p_key] = qd['perm']
                else:
                    n_skipped += 1

"This is the master list of questions"
q_list = sorted(questions.keys())
#print(questions)

"Now process each of the input files"
csv_header = None
norm_students = []
for i, f in enumerate(args.files):
    reader = csv.DictReader(f)

    "Create the csv header for the outfile"
    csv_header = reader.fieldnames[:5]
    for q in q_list:
        csv_header.append(q)

    "These are the keys for question/permutation"
    qs = 'q' + str(i)
    ps = 'p' + str(i)

    "Get the exam key"
    key = next(reader)
    
    "Iterate over the student responses"
    for student in reader:

        "Create the normalized output for this student"
        norm = {}
        norm['CWID'] = student['CWID']
        norm['Mybama ID'] = student['Mybama ID']
        norm['Student Name'] = student['Student Name']
        norm['Raw Score'] = int(student['Raw Score']) - n_skipped

        "Iterate over the master question list"
        for q in q_list:
        
            "Get the question number and answer permutation for this version"
            ver_q = questions[q][qs]
            ver_p = questions[q][ps]
            
            "Get the student response and check for correct answers"
            response = student[str(ver_q+1)]
            if response == '.':
                response = key[str(ver_q+1)]

            "Now map the response using this versions permutation"
            try:
                r = int(response)  # This will fail for '*', '-', and ' '
                mapped_response = str(ver_p[r-1]+1)
            except:
                mapped_response = response
            
            "Add the mapped question/response to the normalized student response"
            norm[q] = mapped_response

        "Append this student"
        norm_students.append(norm)

"Finally, write it out"
if args.out:
    writer = csv.DictWriter(args.out, csv_header)     
    writer.writeheader()
    
    for ns in norm_students:
        writer.writerow(ns)
