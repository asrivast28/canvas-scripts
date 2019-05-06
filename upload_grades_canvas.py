##
# @brief Upload grades and comments for an assignment to Canvas.
#
# @author Ankit Srivastava <asrivast@gatech.edu>


def parse_args(argv):
    """
    Parse command line arguments passed to the executable.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Upload grade and feedback to Canvas.')
    parser.add_argument('--course', '-s', metavar='ID', required=True, type=str, help='canvas id of the course')
    parser.add_argument('--assignment', '-a', metavar='ID', required=True, type=str, help='canvas id of the assignment')
    parser.add_argument('--config', '-c', metavar='FILE', type=str, default='config.json', help='name of the json config file')
    parser.add_argument('--grades', '-g', metavar='FILE', type=str, default='grades.csv', help='name of the csv file from which grades are to be read')
    args = parser.parse_args(argv)
    return args


def parse_config(json_config):
    """
    Read the configs from the given JSON file.
    """
    import json

    with open('config.json') as json_data_file:
        configuration = json.load(json_data_file)
        access_token = configuration['canvas']['access_token']
        base_url = 'https://{}/api/v1/courses'.format(configuration['canvas']['host'])
    return access_token, base_url


def assign_grade_for_assignment(base_url, header, user_id, grade, comment, verbose=False):
    """
    Use the Canvas API to assign a grade for an assignment
    PUT /api/v1/courses/:course_id/assignments/:assignment_id/submissions/:user_id

    Request Parameters:
    comment[text_comment]		string	Add a textual comment to the submission.
    comment[group_comment]		boolean	Whether or not this comment should be sent to the entire group (defaults to false). Ignored if this is not a group assignment or if no text_comment is provided.
    comment[media_comment_id]		string	Add an audio/video comment to the submission.
    comment[media_comment_type]		string	The type of media comment being added.
    comment[file_ids][]		integer	Attach files to this comment that were previously uploaded using the Submission Comment API's files action
    include[visibility]		string	Whether this assignment is visible to the owner of the submission
    submission[posted_grade]		string	Assign a score to the submission, updating both the "score" and "grade" fields on the submission record. This parameter can be passed in a few different formats:
    submission[excuse]		boolean	    Sets the "excused" status of an assignment.
    submission[late_policy_status]		string	Sets the late policy status to either "late", "missing", "none", or null.
    submission[seconds_late_override]		integer	Sets the seconds late if late policy status is "late"
    rubric_assessment		RubricAssessment	Assign a rubric assessment to this assignment submission. The sub-parameters here depend on the rubric for the assignment. The general format is, for each row in the rubric:

    This function is based on the following:
    https://kth.instructure.com/courses/11/pages/inserting-a-grade-for-a-student-into-a-course
    """
    import requests

    url = '{}/submissions/{}'.format(base_url, user_id)
    if verbose:
       print 'url: ' + url

    payload = {'submission[posted_grade]': grade}
    if comment:
        payload.update({'comment[text_comment]': comment})

    r = requests.put(url, headers=header, data=payload)

    if verbose:
        print 'result of put assign_grade_for_assignment:', r.text
    if r.status_code == requests.codes.ok:
        page_response = r.json()
        return True
    return False


def get_grades_from_csv(grades_file):
    """
    Read grades and comments from the given CSV file.
    """
    import csv

    csv_fieldnames = ['name', 'id', 'username', 'section', 'grade', 'comment']
    all_grades = []
    with open(grades_file, 'rb') as grades:
        csv_reader = csv.DictReader(grades, fieldnames=csv_fieldnames)
        for line in csv_reader:
            all_grades.append((line['name'], line['id'], line['grade'], line['comment']))
    return all_grades


def upload_assignment_grades(json_config, course_id, assignment_id, grades_file):
    """
    Upload the assignment grades and comments to Canvas.
    """
    all_grades = get_grades_from_csv(grades_file)
    access_token, base_url = parse_config(json_config)
    url = '{}/{}/assignments/{}'.format(base_url, course_id, assignment_id)
    header = {'Authorization': 'Bearer ' + access_token}
    for name, user_id, grade, comment in all_grades:
        if assign_grade_for_assignment(url, header, user_id, grade, comment):
            print 'Successfully uploaded grade for', name
        else:
            print 'Failed to upload grade for', name


def main(args):
    """
    Main function.
    """
    upload_assignment_grades(args.config, args.course, args.assignment, args.grades)


if __name__ == '__main__':
    import sys

    main(parse_args(sys.argv[1:]))
