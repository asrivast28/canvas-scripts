##
# @brief Grade multiple PDF submissions from Canvas.
#
# @author Ankit Srivastava <asrivast@gatech.edu>

import csv


def parse_args(argv):
    """
    Parse command line arguments passed to the executable.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Grade Canvas PDF submissions.')
    parser.add_argument('--submissions', '-s', metavar='DIR', type=str, required=True, help='name of the directory which contains all the PDF submissions')
    parser.add_argument('--maximum', '-m', metavar='SCORE', type=float, required=True, help='max score used when no comments provided')
    parser.add_argument('--csv', '-c', metavar='FILE', type=str, default='roster.csv', help='name of the csv file from which the student information is read')
    parser.add_argument('--grades', '-g', metavar='FILE', type=str, default='grades.csv', help='name of the csv file to which the student information is written')
    args = parser.parse_args(argv)
    return args


# name of the first four fields in the csv
csv_fieldnames = ['name', 'id', 'username', 'section']

def get_students_from_csv(csv_name):
    """
    Get student information from the given CSV file.

    Gets the name, id, username, and section for all the students
    from the given CSV file. This has been tested using the CSV
    file exported from Canvas.
    """
    import re

    all_students = []
    username_pattern = re.compile(r'^[a-z]+[0-9]+[a-z]?$')
    with open(csv_name, 'rb') as csvFile:
        csv_reader = csv.DictReader(csvFile, fieldnames=csv_fieldnames)
        for line in csv_reader:
            if username_pattern.match(line['username']):
                all_students.append(dict((key, value) for key, value in line.items() if key))
    return all_students


def grade_student_pdfs(students, submissions, grades, open_pdf, maximum):
    """
    Grade submitted PDFs for the given students.

    This opens PDFs for students, one at a time. The grades and
    comments entered are recorded in a CSV file. The function
    relies on the uniqueness of Canvas assigned ID and assumes
    the corresponding naming format used by Canvas.
    """
    import glob
    import os.path
    import subprocess

    mode = 'wb'
    if os.path.exists(grades):
        mode = 'a'
        print 'Existing grade file found. Appending to it.'
        graded_students = get_students_from_csv(grades)
        students = [s for s in students if s not in graded_students]

    with open(grades, mode) as grades_file:
        csv_writer = csv.DictWriter(grades_file, fieldnames=csv_fieldnames + ['grade', 'comment'])
        for student in students:
            pdfs = glob.glob(os.path.join(submissions, '*_{}_*.pdf'.format(student['id'])))
            info = student.copy()
            info['grade'] = ''
            info['comment'] = ''
            if len(pdfs) == 1:
                pdf = pdfs[0]
                print 'Grading submission for "{}"'.format(student['name'])
                p = subprocess.Popen(open_pdf + [pdf])
                info['comment'] = str(raw_input('Comment: '))
                if info['comment']:
                    info['grade'] = float(raw_input('Grade (max = {}): '.format(maximum)) or 0)
                else:
                    response = str(raw_input('No comments provided. Use max score? [Y/n]')) or 'y'
                    if response.lower().startswith('y'):
                        info['grade'] = maximum
                    else:
                        print 'Not recording grade. Skipping.'
                p.terminate()
            elif len(pdfs) == 0:
                print 'No submission found for "{}"'.format(student['name'])
                info['comment'] = 'Submission not found.'
            else:
                print 'More than one pdf found for "{}". Skipping'.format(student['name'])
            csv_writer.writerow(info)
            grades_file.flush()


def main(args):
    """
    Main function.
    """
    all_students = get_students_from_csv(args.csv)

    # Modify the following for your platform and grading requirements
    open_pdf = ['xreader', '-p', '1', '-l', 'Preamble']
    grade_student_pdfs(all_students, args.submissions, args.grades, open_pdf, args.maximum)


if __name__ == '__main__':
    import sys
    main(parse_args(sys.argv[1:]))
