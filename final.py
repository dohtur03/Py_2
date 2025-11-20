import random
from multiprocessing import Process, Manager, Lock
import time
from rich.live import Live
from rich.table import Table

class Stud:
    def __init__(self, name, sex, results, passed):
        self.name = name
        self.sex = sex
        self.results = results
        self.passed = passed

    def sex_converter(self):
        return "m" if self.sex == "М" else "j"

class Prepod:
    def __init__(self, name, sex, time, kill):
        self.name = name
        self.sex = sex
        self.time = time
        self.kill = kill

    def sex_converter(self):
        return "m" if self.sex == "М" else "j"

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
                studs.append(Stud(name, sex, 0, None))
                            
    with open("questions.txt", "r", encoding="utf-8") as file:
        quests = file.readlines()
  
    return preps, studs, quests

def table_studs(studs, statistics):
    table = Table()
    table.add_column("Студент", justify="left")
    table.add_column("Статус", justify="center")
    for stud in studs:
        stud_stat = statistics.get(f"stud_{stud.name}", {})
        status = stud_stat.get("passed")
        status_txt = "Сдал" if status else "Провалил" if status is not None else "Очередь"
        table.add_row(stud.name, status_txt)
    return table

def sort_status(stud, statistics):
    stud_stat = statistics.get(f"stud_{stud.name}", {})
    passed = stud_stat.get("passed")
    if passed is None:
        return 0
    return 1 if passed else 2

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
    return fate

def exam_run(prep, studs, quests, lock, statistics):
  
    while True:
        lock.acquire()
        if not studs:
            lock.release()
            break
        stud = studs.pop(0)
        lock.release()

        start_time = time.monotonic()
        pause_total = 0
        # exam_time = 1
        exam_time = random.randint(len(prep.name)-1, len(prep.name)+1)                                      
        time.sleep(exam_time)

        result = asker(quests, prep.sex, stud.sex, prep.name, stud.name)
        stud.results += result
        
        passed = stud_fate(stud.results, prep.name, stud.name)
        stud.passed = passed != 'fail'

        key_stud = f"stud_{stud.name}"
        with lock:
            stud_stat = statistics.get(key_stud, {})
            stud_stat.update({'passed': stud.passed, 'results': stud.results})
            statistics[key_stud] = stud_stat
        
        key_prep = f"prep_{prep.name}"
        end_time = time.monotonic()
        with lock:
            prep_stat = statistics.get(key_prep, {})
            prep_stat['time'] = int(prep_stat.get('time', 0) + (end_time - start_time - pause_total))
            if passed == 'fail':
                prep_stat['kill'] = prep_stat.get('kill', 0) + 1
            statistics[key_prep] = prep_stat

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
    statistics = manager.dict()
    lock = manager.Lock()
    processes = []
    for prep in prepods:
        p = Process(target=exam_run, args=(prep, studs, quests, lock, statistics))
        processes.append(p)
        p.start()

    sorted_studs = sorted(students, key=lambda stud: sort_status(stud, statistics))

    with Live(table_studs(sorted_studs, statistics), refresh_per_second=2) as live:
        while any(p.is_alive() for p in processes):
            time.sleep(0.5)
            sorted_studs = sorted(students, key=lambda stud: sort_status(stud, statistics))
            live.update(table_studs(sorted_studs, statistics))
        for p in processes:
           p.join()
        sorted_studs = sorted(students, key=lambda stud: sort_status(stud, statistics))
        live.update(table_studs(sorted_studs, statistics))

    for stud in students:
        stud_stat = statistics.get(f"stud_{stud.name}", {})
        stud.passed = stud_stat.get("passed", None)
        stud.results = stud_stat.get("results", 0)

    for prep in prepods:
        prep_stat = statistics.get(f"prep_{prep.name}", {})
        prep.time = prep_stat.get("time", 0)
        prep.kill = prep_stat.get("kill", 0)

    print("Итоговая статистика:")
    for stud in students:
        print(f"Name: {stud.name}, passed: {stud.passed}")
    for prep in prepods:
        print(f"Name: {prep.name}, time: {prep.time}, killed: {prep.kill}")


def main():
    preps, studs, quests = importer()
    for stud in studs:
        print(f"student: {stud.name}")
        sex_stud = stud.sex_converter()

        stud_fate(quests, sex_stud, "m")

if __name__ == "__main__":
    exam_process()
