import random
from multiprocessing import Process, Manager, Lock
import time

class Stud:
    def __init__(self, name, sex, results, passed):
        self.name = name
        self.sex = sex
        self.results = results
        self.passed = passed

    def sex_converter(self):
        return "m" if self.sex == "М" else "j"

class Prepod:
    def __init__(self, name, sex):
        self.name = name
        self.sex = sex

    def sex_converter(self):
        return "m" if self.sex == "М" else "j"

def importer():
    preps = []    
    with open("examiners.txt", "r", encoding="utf-8") as file:
        for line in file:
            params = line.strip().split()
            if len(params) ==2:
                name, sex = params
                preps.append(Prepod(name, sex))

    studs = []
    with open("students.txt", "r", encoding="utf-8") as file:
        for line in file:
            params = line.strip().split()
            if len(params) == 2:
                name, sex = params
                studs.append(Stud(name, sex, 0, None))
                            
    with open("questions.txt", "r", encoding="utf-8") as file:
        quests = file.readlines()
  
    return preps, studs, quests

def golden(n):
    phi = 1.618
    base = 1 / phi
    series = [base**(i+1) for i in range(n)]
    s = sum(series)
    proba = [x / s for x in series]
    return proba

def asker(quests, mj_stud, mj_prep, prep_n, stud_n):
    result = 0
    fate_quests = random.sample(quests, 3)
    for quest in fate_quests:
        answers_prep = []
        quest = quest.strip()
        words = quest.split()
        n = len(words)
        proba_stud = golden(n)
        if mj_stud != "m":
            proba_stud.reverse()
        answer_stud = random.choices(words, weights = proba_stud, k=1)[0]
        proba_prep = golden(n)
        if mj_prep != "m":
            proba_prep.reverse()
        redo = True
        while redo and words:
            answer_prep = random.choices(words, weights = proba_prep, k=1)[0]
            answers_prep.append(answer_prep)
            index = words.index(answer_prep)
            words.pop(index)
            proba_prep.pop(index)
            redo = random.choice([True, False, False])
        print(f"Prepod: {prep_n}: {answers_prep}, Student: {stud_n}: {answer_stud}")
        if answer_stud in answers_prep:
            result += 1

    return result
        
def stud_fate(result, prep_n, stud_n):
    fate = 'unknown'
    mood = random.choices(['bad', 'good', 'norm'], 
                          weights = [1, 2, 5], k=1)[0]
    if mood == 'bad':
        fate = 'fail'
    elif mood == 'good':
        fate = 'pass'
    elif mood == 'norm' and result >= 2:
        fate = 'pass'
    else:
        fate = 'fail'
    print (f"Prepod: {prep_n}, mood {mood}, Student {stud_n}, result: {result}, fate: {fate}")
    return fate

def exam_run(prep, studs, quests, lock, passed, times):
  
    while True:
        lock.acquire()
        if not studs:
            lock.release()
            break
        stud = studs.pop(0)
        lock.release()

        start_time = time.monotonic()
        pause_total = 0
        exam_time = 1
        # exam_time = random.randint(len(prep.name)-1, len(prep.name)+1)                                      
        time.sleep(exam_time)

        result = asker(quests, prep.sex, stud.sex, prep.name, stud.name)
        stud.results += result
        
        stud.passed = stud_fate(stud.results, prep.name, stud.name) != 'fail'
        print(f"Prepod: {prep.name}, Student: {stud.name}, result: {stud.results}, passed: {stud.passed}")
        passed[stud.name] = stud.passed
        
        end_time = time.monotonic()
        times[prep.name] = int(times.get(prep.name, 0) + (end_time - start_time - pause_total))

        time_now = time.monotonic()
        if time_now - start_time >= 30:
            pause_start = time.monotonic()
            pause_time = random.randint(12, 18)
            print(f"gehen wir nach hause es verboten ... pause time: {pause_time}, Prep: {prep}")
            time.sleep(pause_time)
            pause_end = time.monotonic()
            pause_duration = pause_end - pause_start
            pause_total += pause_duration
            start_time = time.monotonic()

def exam_process():
    prepods, students, quests = importer()
    manager = Manager()
    studs = manager.list(students)
    passed = manager.dict()
    lock = manager.Lock()
    times = manager.dict()
    processes = []
    for prep in prepods:
        p = Process(target=exam_run, args=(prep, studs, quests, lock, passed, times))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    for stud in students:
        if stud.name in passed:
            stud.passed = passed[stud.name]
        else:
            stud.passed = None

    print("Итоговая статистика:")
    for stud in students:
        print(f"Name: {stud.name}, passed: {stud.passed}")
    print("Время экзаменаторов:", dict(times))


def main():
    preps, studs, quests = importer()
    for stud in studs:
        print(f"student: {stud.name}")
        sex_stud = stud.sex_converter()

        stud_fate(quests, sex_stud, "m")

if __name__ == "__main__":
    exam_process()
