import typing as tp
from enum import Enum

def calc_mcta_keys(answers: tp.List[str]) -> list():
    mctaKeys = []
    counter = 0
    mctaKeys.append(["", "Answer", "Title", "Concept"])
    for x in answers:
        if (x):
            counter += 1
            mctaKeys.append([f"Q{counter}", x, f"Q{counter}", "unknown"])
    return mctaKeys

def calc_mcta_answers(code: str, fqci: int, fcfv: int, answers: tp.List[tp.List[str]]) -> list():
    mcta_answers = []
    mcta_answers.append(answers[0][fqci:])
    for row in answers:
        if row[fcfv] == code: 
            mcta_answers.append(row[fqci:])
    
    first_col = []
    first_col.append("")
    for i in range(1, len(mcta_answers)):
        first_col.append(f"Student{i}")
    for x, y in zip(mcta_answers, first_col):
        x.insert(0,y)
    return mcta_answers

def get_form_code_column (fieldcols: list(Enum)) -> int:
    for col in fieldcols:
        if col.name == 'TEST_FORM_CODE':
            return col.value-1

