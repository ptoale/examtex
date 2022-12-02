"""

utility stuff...


"""
import os
import runpy
import jinja2


class JinjaEnv(object):
    """
    Singleton instance of jinja2 environment, configured for latex.

    """
    __instance = None

    def __new__(cls):
        if JinjaEnv.__instance is None:
            JinjaEnv.__instance = object.__new__(cls)
            JinjaEnv.__instance.env = jinja2.Environment(
                block_start_string=r'\BLOCK{',
                block_end_string='}',
                variable_start_string=r'\VAR{',
                variable_end_string='}',
                comment_start_string=r'\#{',
                comment_end_string='}',
                line_statement_prefix='%%',
                line_comment_prefix='%#',
                trim_blocks=True,
                autoescape=False,
                loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../templates'))
            )

        return JinjaEnv.__instance


def check_config(cfg):
    """
    Check to make sure that the configuration has all the required keys.

    :param cfg: the configuration
    :type cfg: dict
    """
    required = ['question_dir', 'docopts', 'head_foot', 'front',
                'exam_dir', 'course', 'semester', 'exam', 'versions', 'num_per_page']

    missing = []
    for k in required:
        if k not in cfg:
            missing.append(k)

    if missing:
        print("Configuration is missing the following keys: {}".format(missing))
        return False
    return True


class QuestionFactory(object):
    """
    Helper class for rendering questions.

    :param question_dir: path to directory containing question files
    :type question_dir: str

    """

    def __init__(self, *args, **kwargs):
        self.question_dir = kwargs['question_dir']

    def make_question(self, qid, version=0, pts=None, perm=None):
        """
        method for getting a formated question from a question file.

        :param qid: id of question
        :type qid: str
        :param version: version of question to process
        :type version: int
        :param pts: the point value of the question, optional
        :type pts: int or None
        :param perm: the choice permutation for multiple-choice questions, optional
        :type perm: list of ints
        :return: the rendered question
        :rtype: str

        """

        "Form name of question file"
        question_name = "{}/q{}.py".format(self.question_dir, qid)

        "Run the file through runpy to get global dict"
        glob = runpy.run_path(question_name)

        "Call the files make function to do the dirty work"
        qtex = glob['make'](version, pts, perm)

        return qtex


def si(value, unit=None, opts=None):
    """
    Return a unicode string that conforms to the Latex siunitx package

    >>> print(si(1.0))
    \\num{1.0}
    >>> print(si(1.0, unit=r'\meter'))
    \\qty{1.0}{\meter}
    >>> print(si(1/8, unit=r'\meter', opts=r'round-mode=figures, round-precision=2'))
    \\qty[round-mode=figures, round-precision=2]{0.125}{\meter}
    """
    env = JinjaEnv().env

    if unit:
        if opts:
            return env.from_string(r'\qty[\VAR{opts}]{\VAR{value}}{\VAR{unit}}').render(opts=opts, value=value,
                                                                                        unit=unit)
        else:
            return env.from_string(r'\qty{\VAR{value}}{\VAR{unit}}').render(value=value, unit=unit)
    else:
        if opts:
            return env.from_string(r'\num[\VAR{opts}]{\VAR{value}}').render(opts=opts, value=value)
        else:
            return env.from_string(r'\num{\VAR{value}}').render(value=value)


def render(template, **kwargs):
    """
    Shortcut method for rendering string templates

    :param template: the template
    :type template: str
    :param kwargs: a dict containing any needed variables
    :type kwargs: dict
    :return: the rendered text
    :rtype: str

    """
    return JinjaEnv().env.from_string(template).render(kwargs)


def permute(choices, permutation):
    """
    Permute the answer choices for a multiple-choice question.

    :param choices: the answer choices
    :type choices: list of strs
    :param permutation: the permutation of the choices
    :type permutation: list of ints containing 0-(n_choice-1)
    :return: permuted list and index of correct answer
    :rtype: [list, int]

    """
    correct = permutation.index(0)
    result = [choices[i] for i in permutation]
    return result, correct


if __name__ == '__main__':
    import doctest
    doctest.testmod()
