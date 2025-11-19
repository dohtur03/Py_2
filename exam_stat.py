import random
from multiprocessing import Process, Manager, Lock
import time

class Stud:
    def __init__(self, name, sex, passed):
        self.name = name
        self.sex = sex
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
                studs.append(Stud(name, sex, 1))
                            
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

def stud_fate(quests, mj_stud, mj_prep):
    correct = None
    fate_quests = random.sample(quests, 3)
    for quest in fate_quests:
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
        answer_prep = random.choices(words, weights = proba_prep, k=1)[0]
        print(f"stud: {answer_stud}, prepod: {answer_prep}")
        
def exam_run(prep, studs, quests, lock, result, times):
  
    while True:
        lock.acquire()
        if not studs:
            lock.release()
            break
        stud = studs.pop(0)
        lock.release()

        start_time = time.monotonic()
        pause_total = 0
        
        print(f"Prepod: {prep.name}, Stud: {stud.name}")

        for i in range(3):
            exam_time = random.randint(len(prep.name)-1, len(prep.name)+1)
            print(f"exam duration {exam_time} repeat: {i}")
            time.sleep(exam_time)
            print(f"Prep: {prep.name}, Stud: {stud.name}")
            stud_fate(quests, prep.sex, stud.sex)
        
        end_time = time.monotonic()
        times[prep.name] = times.get(prep.name, 0) + (end_time - start_time - pause_total)

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
    results = manager.dict()
    lock = manager.Lock()
    times = manager.dict()
    processes = []
    for prep in prepods:
        p = Process(target=exam_run, args=(prep, studs, quests, lock, results, times))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


def main():
    preps, studs, quests = importer()
    for stud in studs:
        print(f"student: {stud.name}")
        sex_stud = stud.sex_converter()

        stud_fate(quests, sex_stud, "m")

if __name__ == "__main__":
    exam_process()
