import random

def golden(n):
    phi = 1.618
    base = 1 / phi
    series = [base ** (i + 1) for i in range(n)]
    s = sum(series)
    proba = [x / s for x in series]
    return proba

def asker(quests, mj_stud, mj_prep, prep_n, stud_n, question_stats=None):
    result = 0
    fate_quests = random.sample(quests, 3)
    for quest in fate_quests:
        answers_prep = []
        words = quest.worder()
        n = len(words)
        proba_stud = golden(n)
        if mj_stud != "m":
            proba_stud.reverse()
        answer_stud = random.choices(words, weights=proba_stud, k=1)[0]
        proba_prep = golden(n)
        if mj_prep != "m":
            proba_prep.reverse()
        redo = True
        while redo and words:
            answer_prep = random.choices(words, weights=proba_prep, k=1)[0]
            answers_prep.append(answer_prep)
            index = words.index(answer_prep)
            words.pop(index)
            proba_prep.pop(index)
            redo = random.choice([True, False, False])
        if answer_stud in answers_prep:
            result += 1
            if question_stats is not None:
                question_stats[quest.text] = question_stats.get(quest.text, 0) + 1

    return result

def stud_fate(result, prep_n, stud_n):
    mood = random.choices(["bad", "good", "norm"], weights=[1, 2, 5], k=1)[0]
    if mood == "bad":
        return "fail"
    elif mood == "good":
        return "pass"
    else:
        return "pass" if result >= 2 else "fail"