from classes_import import Stud, Prepod, Quests

def importer():
    preps = []
    with open("examiners.txt", "r", encoding="utf-8") as file:
        for line in file:
            params = line.strip().split()
            if len(params) == 2:
                name, sex = params
                preps.append(Prepod(name, sex, 0, 0))

    studs = []
    with open("students.txt", "r", encoding="utf-8") as file:
        for line in file:
            params = line.strip().split()
            if len(params) == 2:
                name, sex = params
                studs.append(Stud(name, sex, 0, None, 0))

    questions = []
    with open("questions.txt", "r", encoding="utf-8") as file:
        for line in file:
            questions.append(Quests(line.strip(), 0))

    return preps, studs, questions