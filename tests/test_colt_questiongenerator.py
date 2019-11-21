import pytest
#
from colt import QuestionGenerator
from colt import Question

@pytest.fixture
def questions():
    return """
      value = 2 :: int :: [1, 2, 3]
      # hallo ihr
      # ihr auch
      name = :: str :: [hallo, du]
      ilist = :: ilist
      flist = 1.2 3.8 :: flist

      [qm]
      nqm = 100 :: int
      nmm = 200 :: int

      [examplecase(yes)]
      a = 10
      [examplecase(no)]
      a = 666

      [examplecase(no)::further]
      a = 666

      [examplecase(no)::further::andmore]
      a = 666
      select = :: str

      [examplecase(no)::further::andmore::select(yes)]
      a = yes

      [examplecase(no)::further::andmore::select(no)]
      a = no

      [examplecase(no)::further::andmore::select(maybe)]
      a = maybe :: str :: :: What was the question?
    """

def test_generate_questions(questions):
    """test parsing of basic questions string"""
    questions = QuestionGenerator(questions).questions
    assert questions['value'] == Question("value", "int", '2', choices=['1', '2', '3'])
    assert questions['name'] == Question("name", "str", None, choices=['hallo', 'du'], comment=" hallo ihr\n ihr auch")
    assert questions['ilist'] == Question("ilist", "ilist", None)
    assert questions['flist'] == Question("flist", "flist", '1.2 3.8')
    assert questions['examplecase']['no']['further']['andmore']['select']['maybe']['a'] == Question("What was the question?", "str", 'maybe')

def test_add_question_to_block(questions):
    """test parsing of basic questions string

       and add additional questions
    """
    questions_generator = QuestionGenerator(questions)
    questions_generator.add_questions_to_block("""
        add =
    """)

    questions = questions_generator.questions

    assert questions['value'] == Question("value", "int", '2', choices=['1', '2', '3'])
    assert questions['name'] == Question("name", "str", None, choices=['hallo', 'du'], comment=" hallo ihr\n ihr auch")
    assert questions['ilist'] == Question("ilist", "ilist", None)
    assert questions['flist'] == Question("flist", "flist", '1.2 3.8')
    assert questions['add'] == Question("add", "str")

def test_add_question_to_block_no_overwrite(questions):
    """test parsing of basic questions string """
    questions_generator = QuestionGenerator(questions)
    questions_generator.add_questions_to_block("""
        value =
        add =
    """, overwrite=False)

    questions = questions_generator.questions

    assert questions['value'] == Question("value", "int", '2', choices=['1', '2', '3'])
    assert questions['name'] == Question("name", "str", None, choices=['hallo', 'du'], comment=" hallo ihr\n ihr auch")
    assert questions['ilist'] == Question("ilist", "ilist", None)
    assert questions['flist'] == Question("flist", "flist", '1.2 3.8')
    assert questions['add'] == Question("add", "str")

def test_add_question_block(questions):
    """test parsing of basic questions string

       and add additional questions
    """
    questions_generator = QuestionGenerator(questions)
    #
    questions_generator.generate_block("hallo", """
        du =
        add =
    """)
    #
    questions = questions_generator.questions

    assert questions['value'] == Question("value", "int", '2', choices=['1', '2', '3'])
    assert questions['name'] == Question("name", "str", None, choices=['hallo', 'du'], comment=" hallo ihr\n ihr auch")
    assert questions['ilist'] == Question("ilist", "ilist", None)
    assert questions['flist'] == Question("flist", "flist", '1.2 3.8')
    assert questions['hallo']['add'] == Question("add", "str")
    assert questions['hallo']['du'] == Question("du", "str")


def test_add_question_to_subblock(questions):
    """test parsing of basic questions string

       and add additional questions
    """
    questions_generator = QuestionGenerator(questions)
    #
    questions_generator.add_questions_to_block("""
        du =
        add =
    """, block="::qm")

    questions = questions_generator.questions

    assert questions['value'] == Question("value", "int", '2', choices=['1', '2', '3'])
    assert questions['name'] == Question("name", "str", None, choices=['hallo', 'du'], comment=" hallo ihr\n ihr auch")
    assert questions['ilist'] == Question("ilist", "ilist", None)
    assert questions['flist'] == Question("flist", "flist", '1.2 3.8')
    assert questions['qm']['nqm'] == Question("nqm", "int", '100')
    assert questions['qm']['nmm'] == Question("nmm", "int", '200')
    assert questions['qm']['add'] == Question("add", "str")
    assert questions['qm']['du'] == Question("du", "str")

def test_add_question_to_created_subblock(questions):
    """test parsing of basic questions string

       and add additional questions
    """
    questions_generator = QuestionGenerator(questions)
    #
    questions_generator.generate_block("hallo", """
        du =
    """)
    #
    questions_generator.add_questions_to_block("""
        add =
    """, block="::hallo")

    questions = questions_generator.questions

    assert questions['value'] == Question("value", "int", '2', choices=['1', '2', '3'])
    assert questions['name'] == Question("name", "str", None, choices=['hallo', 'du'], comment=" hallo ihr\n ihr auch")
    assert questions['ilist'] == Question("ilist", "ilist", None)
    assert questions['flist'] == Question("flist", "flist", '1.2 3.8')
    assert questions['hallo']['add'] == Question("add", "str")
    assert questions['hallo']['du'] == Question("du", "str")

def test_add_cases_keyerror(questions):
    """test parsing of basic questions string
    """
    questions_generator = QuestionGenerator(questions)
    #
    with pytest.raises(KeyError):
        questions_generator.generate_cases("software", {
            'qchem': "basis = sto-3g\nfunctional=b3lyp",
            'gaussian': "basis = 6-31g*\nfunctional=cam-b3lyp",
            }, "::hallo")

def test_add_cases(questions):
    """test parsing of basic questions string

       and add additional questions
    """
    questions_generator = QuestionGenerator(questions)
    #
    questions_generator.generate_cases("software", {
        'qchem': "basis = sto-3g\nfunctional=b3lyp",
        'gaussian': "basis = 6-31g*\nfunctional=cam-b3lyp",
    })
    #
    questions = questions_generator.questions

    assert questions['value'] == Question("value", "int", '2', choices=['1', '2', '3'])
    assert questions['name'] == Question("name", "str", None, choices=['hallo', 'du'], comment=" hallo ihr\n ihr auch")
    assert questions['ilist'] == Question("ilist", "ilist", None)
    assert questions['flist'] == Question("flist", "flist", '1.2 3.8')
    assert questions['software']['qchem']['basis'] == Question("basis", "str", "sto-3g")
    assert questions['software']['qchem']['functional'] == Question("functional", "str", "b3lyp")
    assert questions['software']['gaussian']['basis'] == Question("basis", "str", "6-31g*")
    assert questions['software']['gaussian']['functional'] == Question("functional", "str", "cam-b3lyp")

def test_add_block_to_cases(questions):
    """test parsing of basic questions string

       and add additional questions
    """
    questions_generator = QuestionGenerator(questions)
    #
    questions_generator.generate_cases("software", {
        'qchem': "basis = sto-3g\nfunctional=b3lyp",
        'gaussian': "basis = 6-31g*\nfunctional=cam-b3lyp",
    })

    questions_generator.generate_block("system", """
    mem= 10GB
    ncpus = 4 :: int
    """, "::software(qchem)")
    #
    questions = questions_generator.questions

    assert questions['value'] == Question("value", "int", '2', choices=['1', '2', '3'])
    assert questions['name'] == Question("name", "str", None, choices=['hallo', 'du'], comment=" hallo ihr\n ihr auch")
    assert questions['ilist'] == Question("ilist", "ilist", None)
    assert questions['flist'] == Question("flist", "flist", '1.2 3.8')
    assert questions['software']['qchem']['basis'] == Question("basis", "str", "sto-3g")
    assert questions['software']['qchem']['functional'] == Question("functional", "str", "b3lyp")
    assert questions['software']['qchem']['system']['mem'] == Question("mem", "str", "10GB")
    assert questions['software']['qchem']['system']['ncpus'] == Question("ncpus", "int", "4")
    assert questions['software']['gaussian']['basis'] == Question("basis", "str", "6-31g*")
    assert questions['software']['gaussian']['functional'] == Question("functional", "str", "cam-b3lyp")
