#!/usr/bin/env python
"""
Main script for the examtex package.

Configuration order is:
    - default configuration file (in same directory as this file)
    - configuration file passed on command line (--config)
    - exam configuration file passed on command line (exam)
    - specific variables available on the command line (like --num_per_page)

Require parameters:
    - exam.tex:
        questions: created from question files
        num_per_page: specified in configuration or command line
    - question.tex:
        qtext: created from question files
    - Exam class:
        question_dir: specified in configuration
        exam_dir: specified in configuration
        course: specified in configuration
        semester: specified in configuration
        exam: specified in configuration
        versions: specified in configuration
        docopts: specified in configuration
        head_foot: specified in configuration
        front: specified in configuration
Optional parameters:
    - exam.tex:
        docopts_str: created from docopts
        packages: specified in configuration, defaults to none
        pkgconfig: specified in configuration, defaults to none
        start_on_new: specified in configuration or command line, defaults to false
        back: specified in configuration, defaults to none
    - question.tex:
        meta: specified in configuration, defaults to none
        pts: specified in configuration, defaults to none
        choices: created from question files
        correct: created from question files
        figure: created from question files
        fig_width: created from question files
        stext: created from question files
        solspace: created from question files



General configuration:
    num_per_page, question_dir, docopts, head_foot

Exam specific configuration:
    exam_dir, course, semester, exam, front, versions

"""
import copy
from examtex.util import QuestionFactory, JinjaEnv, check_config


class Exam(object):
    """
    The exam class.

    :param args: unused
    :type args: list
    :param kwargs: the configuration
    :type kwargs: dict

    """

    def __init__(self, *args, **kwargs):

        "Merge the configuration into the class dict."
        self.__dict__ = {**self.__dict__, **kwargs}

    def make_exams(self):
        """
        Make the exam tex files.
        """
        for version in self.versions:

            "create a short version of the semester for the output file names"
            sem, year = self.semester.split()
            short_sem = "{}{}".format('Fa', year)
            if sem == 'Spring':
                short_sem = "{}{}".format('Sp', year)
            elif sem == 'Summer':
                short_sem = "{}{}".format('Su', year)

            "create one with answers and one without answers"
            for answers in [False, True]:
                tex = self.render(version, answers=answers)

                outfile = "{}/{}{}_{}_{}.tex".format(self.exam_dir,
                                                     self.exam.replace(" ", ""),
                                                     version['version'],
                                                     self.course,
                                                     short_sem)
                if answers:
                    outfile = "{}/{}{}_{}_{}_soln.tex".format(self.exam_dir,
                                                              self.exam.replace(" ", ""),
                                                              version['version'],
                                                              self.course,
                                                              short_sem)

                "write to disk"
                with open(outfile, 'w') as f:
                    f.write(tex)

    def render(self, version, answers):
        """
        Render the exam file.

        :param version: version of the exam
        :type version: dict
        :param answers: flag controlling printing of answers
        :type answers: bool
        :return: a rendered exam file
        :rtype: str

        """

        # create the docopts_str
        docopts = copy.deepcopy(self.docopts)
        if answers:
            docopts.append('answers')
        self.docopts_str = ', '.join(docopts)

        # render the head_foot
        head_foot = JinjaEnv().env.from_string(self.head_foot).render(self.__dict__)

        # render the front page
        self.this_version = version['version']
        front = JinjaEnv().env.from_string(self.front).render(self.__dict__)

        # render the questions
        qf = QuestionFactory(question_dir=self.question_dir)
        qs = []
        for qn in version['order']:
            for q in version['questions']:
                if q['qid'] == qn:
                    pts = q['pts'] if 'pts' in q else None
                    perm = q['perm'] if 'perm' in q else None
                    qs.append(qf.make_question(qn, version=q['version'], pts=pts, perm=perm))

        # copy the current dict and replace any rendered fields
        tvars = copy.deepcopy(self.__dict__)
        tvars['questions'] = qs
        tvars['head_foot'] = head_foot
        tvars['front'] = front

        # now render the exam
        efile = JinjaEnv().env.get_template('exam.tex').render(tvars)

        return efile

    def __repr__(self):
        return str(self.__dict__)


if __name__ == "__main__":
    import argparse
    import os
    import inspect
    import yaml

    "Create the parser"
    parser = argparse.ArgumentParser(description="Examtex maker thingy")
    parser.add_argument('exam', type=argparse.FileType('r'),
                        help='Exam file (YAML format)')
    parser.add_argument('--config', help='Exam configuration file (YAML format)')
    parser.add_argument('--num_per_page', type=int, help='Number of questions per page')
    parser.add_argument('--start_on_new', choices=['true', 'false'],
                        help='Start questions on a new page')
    args = parser.parse_args()

    "if a config file is passed in use it, otherwise look for one in this directory"
    cfg_file = None
    if args.config:
        cfg_file = args.config
    else:
        cdir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
        cfg_file = "{}/../config.yml".format(cdir)

    "load the config file"
    try:
        with open(cfg_file, 'r') as f:
            default_cfg = yaml.load(f, Loader=yaml.Loader)
    except FileNotFoundError as err:
        print('Error setting up config: ', err)
        raise SystemExit

    "next load the exam file"
    try:
        exam_cfg = yaml.load(args.exam, Loader=yaml.Loader)
    except FileNotFoundError as err:
        print('Error loading exam yaml file: ', err)
        raise SystemExit

    "finally check for any overrides on the command line"
    arg_cfg = {}
    if args.num_per_page:
        arg_cfg['num_per_page'] = args.num_per_page
    if args.start_on_new:
        arg_cfg['start_on_new'] = args.start_on_new

    "merge the configs (in order)"
    cfg = {**default_cfg, **exam_cfg, **arg_cfg}

    "check that the configuration is valid"
    if not check_config(cfg):
        raise SystemExit

    "create the exam object"
    exam = Exam(**cfg)
    exam.make_exams()
