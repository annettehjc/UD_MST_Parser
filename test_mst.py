'''
 Course:      Data Structures and Algorithms for CL III - WS2324
 Assignment:  Final Project
 Author:      Hyunjoo Cho, Erik Zeiner
 Description: Tests for mst.py and scorer.py

 Honor Code:  We pledge that this program represents our own work.
'''

import pytest, os, glob, pytest_timeout
from mst import *
from scorer import *
from conllu import *


# Assignment part 2: write necessary tests that would at least detect
# the three bugs in the mst.py.
#
# Please try to make your tests concise and clearly understandable.
#

@pytest.fixture(scope="session", autouse=True)
def epsilon():
    """
    Epsilon for comparing performance of our scorer against the baseline.
    """

    return 0


@pytest.fixture(scope="session", autouse=True)
def baseline_scorer():
    """
    Fixture for the baseline scorer.
    """

    return BaselineScorer()


@pytest.fixture(scope="session", autouse=True)
def our_scorer():
    """
    Fixture for our improved scorer.
    """

    return Scorer()


def calculate_AS(sc, test_file):
    """
    Helper function to calculate macro averaged UAS and LAS of a given scorer
    Arguments:
        sc: Scorer object
        test_file: Path to test file
    Return:
        Macro averaged UAS, Macro averaged LAS
    """

    uassum, lassum, n = 0, 0, 0
    for sent in read_conllu(test_file):
        mst = mst_parse(sent, score_fn=sc.score)
        parsed = mst.nodes
        uas, las = evaluate(sent, parsed)
        uassum += uas
        lassum += las
        n += 1
    return uassum / n, lassum / n


@pytest.mark.parametrize("treebank",
                         [
                             "ud-treebanks-english-v2.13/UD_English-Atis",
                             "ud-treebanks-english-v2.13/UD_English-ESLSpok",
                             "ud-treebanks-english-v2.13/UD_English-EWT",
                             "ud-treebanks-english-v2.13/UD_English-GUM",
                             "ud-treebanks-english-v2.13/UD_English-GUMReddit",
                             "ud-treebanks-english-v2.13/UD_English-LinES",
                             "ud-treebanks-english-v2.13/UD_English-ParTUT",
                         ]
                         )
def test_scorer(baseline_scorer, our_scorer, epsilon, treebank):
    """
    Test our scorer against the baseline using all english treebanks.
    """

    # Get treebank data
    train_file = glob.glob(os.path.join(treebank, '*-ud-train.conllu'))[0]
    dev_file = glob.glob(os.path.join(treebank, '*-ud-dev.conllu'))[0]
    test_file = glob.glob(os.path.join(treebank, '*-ud-test.conllu'))[0]

    # Train scorers on the treebank
    baseline_scorer.train(train_file, dev_file)
    our_scorer.train(train_file, dev_file)

    # Calculate scores
    ourUAS, ourLAS = calculate_AS(our_scorer, test_file)
    baselineUAS, baselineLAS = calculate_AS(baseline_scorer, test_file)

    print(
        f'\n\t\tUAS \t\t\t\t LAS\nOUR\t\t{ourUAS}\t{ourLAS}\nBASE\t{baselineUAS}\t{baselineLAS}\nimpr \t {format(ourUAS - baselineUAS, ".0%")} \t\t\t\t {format(ourLAS - baselineLAS, ".0%")}')

    # Is our scorer epsilon better than the baseline?
    assert (ourUAS - baselineUAS > epsilon) and (ourLAS - baselineLAS > epsilon)


def test_find_cycle_exists():
    """
    Test the find_cycle function; the graph contains a cycle.
    """
    sentence_tokens = [
        Token('<ROOT>'),
        Token('I', 'I', 'PRON', 'Case=Nom|Number=Sing|Person=1|PronType=Prs'),
        Token('saw', 'see', 'VERB', 'Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin'),
        Token('her', 'her', 'PRON', 'Case=Gen|Gender=Fem|Number=Sing|Person=3|Poss=Yes|PronType=Prs'),
        Token('duck', 'duck', 'NOUN', 'Number=Sing')
    ]
    dg = DepGraph(sentence_tokens, add_edges=False)
    dg.add_edge(0, 2, weight=1)
    dg.add_edge(2, 1, weight=1)
    dg.add_edge(2, 4, weight=1)
    dg.add_edge(4, 3, weight=1)
    dg.add_edge(3, 0, weight=1)

    # Is there a cycle?
    assert len(dg.find_cycle()) > 0


def test_find_cycle_not_exists():
    """
    Test the find_cycle function; the graph does not contain a cycle
    ValueError is thrown on the line 'i = path.index(child)' in mst.py (3 is not in list)
    """

    sentence_tokens = [
        Token('<ROOT>'),
        Token('I', 'I', 'PRON', 'Case=Nom|Number=Sing|Person=1|PronType=Prs'),
        Token('saw', 'see', 'VERB', 'Mood=Ind|Number=Sing|Person=1|Tense=Past|VerbForm=Fin'),
        Token('her', 'her', 'PRON', 'Case=Gen|Gender=Fem|Number=Sing|Person=3|Poss=Yes|PronType=Prs'),
        Token('duck', 'duck', 'NOUN', 'Number=Sing')
    ]
    dg = DepGraph(sentence_tokens, add_edges=False)

    dg.add_edge(0, 2, weight=1)
    dg.add_edge(2, 1, weight=1)
    dg.add_edge(2, 4, weight=1)
    dg.add_edge(4, 3, weight=1)

    # Is there a cycle?
    assert len(dg.find_cycle()) == 0


@pytest.mark.timeout(30)
def test_mst_parse():
    """
    Test the mst_parse function; without our fix, there is an infinite loop since  the edges are not removed so the cycle can still remain.
    This test checks that the infinite loop has been removed. If it still present, test will timeout and fail.
    """

    train_file = glob.glob(os.path.join('ud-treebanks-english-v2.13/UD_English-Atis', '*-ud-train.conllu'))[0]
    dev_file = glob.glob(os.path.join('ud-treebanks-english-v2.13/UD_English-Atis', '*-ud-dev.conllu'))[0]
    test_file = glob.glob(os.path.join('ud-treebanks-english-v2.13/UD_English-Atis', '*-ud-test.conllu'))[0]

    baseline_scorer = BaselineScorer()
    baseline_scorer.train(train_file, dev_file)
    # calculate_AS uses mst_parse - without the fix, this will not finish running
    calculate_AS(baseline_scorer, test_file)


def test_evaluate():
    """
    Test the evaluate function; tests the score if the label is the same but the head is different
    """

    gold_sent = [
        Token('<ROOT>'),
        Token(form='I', head=2, deprel='nsubj'),
        Token(form='saw', head=0, deprel='root'),
        Token(form='her', head=4, deprel='nmod'),
        Token(form='duck', head=2, deprel='obj'),
    ]
    pred_sent = [
        Token('<ROOT>'),
        Token(form='I', head=4, deprel='nsubj'),
        Token(form='saw', head=0, deprel='root'),
        Token(form='her', head=4, deprel='nmod'),
        Token(form='duck', head=2, deprel='obj'),
    ]

    UAS, LAS = evaluate(gold_sent, pred_sent)
    assert UAS == 0.75 and LAS == 0.75
