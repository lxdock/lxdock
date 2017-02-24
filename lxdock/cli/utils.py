import collections


def yesno(question, default=False):
    """ Asks the user to answer the yes/no question and returns the corresponding boolean. """
    question_suffix = ' [Yn] ' if default else ' [yN] '
    answer = input(question.strip() + question_suffix).strip().lower()
    answer_to_bool = collections.defaultdict(lambda: default)
    answer_to_bool.update({'yes': True, 'y': True, 'no': False, 'n': False, })
    return answer_to_bool[answer]
