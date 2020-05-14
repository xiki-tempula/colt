from abc import ABCMeta
#
from .questions import QuestionASTGenerator
from .ask import AskQuestions
from .commandline import get_config_from_commandline


__all__ = ["Colt"]


def add_defaults_to_dict(clsdict, defaults):
    """ add defaults to dict """
    for key, default in defaults.items():
        if key not in clsdict:
            clsdict[key] = default


def delete_inherited_keys(keys, clsdict):
    for key in keys:
        if clsdict[key] == 'inherited':
            del clsdict[key]


def join_subquestions(func1, func2):
    if isinstance(func1, classmethod):
        func1 = func1.__func__
    if isinstance(func2, classmethod):
        func2 = func2.__func__

    def _generate_subquestions(cls, questions):
        func1(questions)
        func2(cls, questions)

    return classmethod(_generate_subquestions)


def colt_modify_class_dict(clsdict, bases):
    """setup the clsdict in colt to avoid inheritance problems

       it modifies both the clsdict and its annotations!
    """
    colt_defaults = {'_generate_subquestions': classmethod(lambda cls, questions: 0),
                     '_questions': "",
                     }
    # rewrite that....it is horrible
    if clsdict.get('__annotations__', None) is not None:
        if clsdict['__annotations__'].get('subquestions', None) == 'inherited':
            if '_generate_subquestions' in clsdict:
                if len(bases) > 0:
                    clsdict['_generate_subquestions'] = join_subquestions(
                        bases[0]._generate_subquestions,
                        clsdict['_generate_subquestions'])
            else:
                clsdict['_generate_subquestions'] = bases[0]._generate_subquestions
            # delete task from annotations, and clean unnecessary annotations!
            del clsdict['__annotations__']['subquestions']
            if clsdict['__annotations__'] == {}:
                del clsdict['__annotations__']
    #
    add_defaults_to_dict(clsdict, colt_defaults)
    delete_inherited_keys(["_questions"], clsdict)


class ColtMeta(ABCMeta):
    """Metaclass to handle hierarchical generation of questions"""

    def __new__(cls, name, bases, clsdict):
        colt_modify_class_dict(clsdict, bases)
        return ABCMeta.__new__(cls, name, bases, clsdict)

    @property
    def questions(cls):
        return cls._generate_questions()

    def _generate_questions(cls):
        """generate questions"""
        questions = QuestionASTGenerator(cls._questions)
        cls._generate_subquestions(questions)
        return questions

    def _generate_subquestions(cls, questions):
        """This class will not be inherited"""


class Colt(metaclass=ColtMeta):
    """Basic Class to manage colts question routines"""

    @property
    def questions(self):
        return self.__class__.questions

    @classmethod
    def generate_questions(cls, config=None, presets=None):
        return AskQuestions(cls.questions, config=config, presets=presets)

    @classmethod
    def from_questions(cls, *args, check_only=False, config=None, savefile=None, **kwargs):
        questions = cls.generate_questions(config=config)
        if check_only is True:
            answers = questions.check_only(savefile)
        else:
            answers = questions.ask(savefile)
        return cls.from_config(answers, *args, **kwargs)

    @classmethod
    def from_config(cls, answer, *args, **kwargs):
        raise Exception("Cannot load from_config, as it is not implemented!, "
                        "also from_questions depend on that!")

    @classmethod
    def from_commandline(cls, *args, description=None, **kwargs):
        """Initialize file from commandline options"""
        answers = cls.get_commandline_args(description=description)
        return cls.from_config(answers, *args, **kwargs)

    @classmethod
    def get_commandline_args(cls, description=None, presets=None):
        """for the moment we accept only linear trees!"""
        return get_config_from_commandline(cls.questions, description=description, presets=presets)

    @classmethod
    def generate_input(cls, filename, config=None, presets=None):
        questions = cls.generate_questions(config=config, presets=presets)
        return questions.generate_input(filename)


def _init(self, function):
    self.function = function
    self.__doc__ = self.function.__doc__


def _call(self, *args, **kwargs):
    # call with arguments
    if any(len(value) != 0 for value in (args, kwargs)):
        return self.function(*args, **kwargs)
    # call from commandline
    answers = self.from_commandline(self.description)
    return self.function(**answers)


def _from_config(cls, answers, *args, **kwargs):
    return answers


class FromCommandline:
    """Decorator to parse commandline arguments"""

    def __init__(self, questions, description=None):

        self._cls = type("CommandlineInterface", (Colt,), {
            '_questions': questions,
            'description': description,
            '__init__': _init,
            'from_config': classmethod(_from_config),
            '__call__': _call,
            })

    def __call__(self, function):
        return self._cls(function)
