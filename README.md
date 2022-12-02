examtex documentation
======================

Templating framework for latex-based exams. Uses the [`exam`](https://ctan.org/pkg/exam?lang=en) document class, 
[`jinja`](https://pypi.org/project/Jinja2/) templates, and [`yaml`](https://yaml.org) configuration files.
To use it, you must:
1. Create a collection of question files
2. Create an exam configuration
3. Run the program to generate tex files

## Questions:

Each question is created within a python file located at: `<question_dir>/q<qid>.py`, where `<qid>` is a 
unique string. The job of the question python file is to render an instance of the `question.tex` template. 
The template requires 1 parameter:
- `qtext`: the question text

It accepts several optional parameters:
- `meta`: meta information, in the form of a latex comment
- `pts`: the point value of the question
- `choices`: the choices for a multiple-choice question
- `correct`: the index of the correct choice for a multiple-choice question
- `figure`: the file name for any figure used
- `fig_width`: the figure width as a fraction of the minipage width
- `stext`: solution text
- `solspace`: space to leave for a solution

All question files must contain a method named `make` with the signature:

    def make(version, pts=None, permutation=None):
      """
      version (int): version number
      pts (int): point value
      permutation (list): permutation of choices for multiple-choice questions
      
      returns (str): rendered question
      """

It should import `examtex.util.JinjaEnv` and use it to render the question with:

    question = JinjaEnv().env.get_template('question.tex').render(
        meta=meta,
        pts=pts,
        qtext=qtext,
        choices=choices,
        correct=correct,
        figure=figure,
        fig_width=fig_width,
        solspace=solspace,
        stext=stext
    )

An example of a question file is:

    from examtex.util import JinjaEnv, si, render, permute

    meta = r"""%-----------------------------------------------------------------------------------
    % Question 001
    %   Given the amount of work required to move a charge between two points, find
    %   the magnitude of the potential difference between those points.
    %
    %   Outcomes: some list of outcomes
    %   
    %   Modifications: some list of modifications
    %
    %-----------------------------------------------------------------------------------"""

    qtemp = r"""If \VAR{work} of work is required to carry a \VAR{charge} charge from one point to 
    another, the magnitude of the potential difference between these two points is"""

    stemp = r"""The work done is equal (in magnitude) to the change in the potential energy, which 
    is proportional to the change in electric potential:
    \[
    |\Delta V| = \left|\frac{\Delta U}{q}\right| 
               = \left|\frac{W}{q}\right| 
               = \frac{\VAR{work}}{\VAR{charge}} 
               = \VAR{potential}
    \]"""

    inputs = {
        'work': [500, 500, 500],
        'charge': [40, 60, 30]
    }


    def make(version, pts=None, permutation=None):

        "get the input values for this version"
        W = inputs['work'][version]
        Q = inputs['charge'][version]

        "calculate the answers"
        V0 = W / Q
        V1 = W * Q
        V2 = Q / W
        V3 = 0
        V4 = r'depends on the path between the points'

        "format the answers"
        opts = 'round-mode=figures, round-precision=3'
        choiceA = si(V0, r'\volt', opts)
        choiceB = si(V1 / 1000, r'\volt', opts)
        choiceC = si(V2 * 1000, r'\volt', opts)
        choiceD = si(V3, r'\volt', opts)
        choiceE = V4

        "create the choices list"
        choices = [choiceA, choiceB, choiceC, choiceD, choiceE]
        correct = 0
        if permutation:
            choices, correct = permute(choices, permutation)

        "format the question and solution text"
        work = si(W, r'\joule', opts)
        charge = si(Q, r'\coulomb', opts)
        potential = choiceA

        qtext = render(qtemp, work=work, charge=charge)
        stext = render(stemp, work=work, charge=charge, potential=potential)

        "format the question"
        question = JinjaEnv().env.get_template('question.tex').render(
            meta=meta,
            pts=pts,
            qtext=qtext,
            choices=choices,
            correct=correct,
            figure=None,
            fig_width=None,
            solspace='0in',
            stext=stext
        )

        return question


## Exam configuration:

The exam is configured at three levels:
1. General configuration information in `config.yml`
2. Exam specific configuration in a `yaml`-formatted file
3. Command-line arguments (limited to a few parameters)

The general configuration is common items that do not change from one exam to the next. The exam specific
configuration file contains most of the exam information, including the question details. A few parameters
can be configured on the command line. The overall configuration is the union of these three with precedent
being: command line > exam yaml > config yaml. The configuration must contain the following fields:
- question_dir: the path to the directory with the question files
- docopts: list of latex exam documentclass options
- head_foot: configuration of the page headers and footers
- front: the front page of the exam
- exam_dir: the directory to write the output tex files
- course: the course ('PH102')
- semester: the semester ('Fall 2022')
- exam: the exam ('Exam 3')
- versions: list of versions with question configuration
- num_per_page: number of questions per page

An example exam configuration file looks like:

    course: xx101
    semester: Fall 2022
    exam: Exam 3
    exam_dir: /Users/patoale/Dropbox/projects/examtex/example
    front: |
      \noindent\makebox[\textwidth]{\VAR{course} \VAR{semester} \quad\quad\quad\quad Name:\enspace\hrulefill}
      \noindent \VAR{exam}, Version \VAR{this_version}
      \vspace{0.15in}
  
      \noindent This exam covers some stuff. There are \numquestions\ 
      questions worth a total of \numpoints\ points. You have 50 minutes to complete it. Make sure:
      \begin{enumerate}
      \item your name is clearly printed on the line above
      \item your name and CWID are bubbled in on your scantron
      \end{enumerate}
      When you are finished, turn in both this exam and your scantron.
      \vspace{0.25in}
  
    versions:
      - version: AA
        order: ['000', '001', '178']
        questions:
          - {qid: '000', version: 0}
          - {qid: '001', pts: 1, version: 0, perm: [ 0, 1, 2, 3, 4 ]}
          - {qid: '178', pts: 1, version: 0, perm: [ 0, 1, 2, 3, 4 ]}
      - version: BA
        order: ['000', '178', '001']
        questions:
          - {qid: '000', version: 1}
          - {qid: '001', pts: 1, version: 1, perm: [ 1, 2, 3, 4, 0 ]}
          - {qid: '178', pts: 1, version: 1, perm: [ 1, 2, 3, 4, 0 ]}


## Generating tex:

To generate the tex file, once the questions and exam configuration are created, run:

    > python examtex/exam.py <path_to_exam>/exam.yml

This will create two tex files for each version; one without answers, one with answers. They will be located 
wherever `exam_dir` points. To see all options:

    > python examtex/exam.py -h
    usage: exam.py [-h] [--config CONFIG] [--num_per_page NUM_PER_PAGE] [--start_on_new {true,false}] exam

    Examtex maker thingy

    positional arguments:
      exam                  Exam file (YAML format)

    options:
      -h, --help            show this help message and exit
      --config CONFIG       Exam configuration file (YAML format)
      --num_per_page NUM_PER_PAGE
                            Number of questions per page
      --start_on_new {true,false}
                            Start questions on a new page
