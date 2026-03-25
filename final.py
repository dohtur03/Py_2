import sys
import io

# Force UTF-8 for stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import random
from multiprocessing import Process, Manager, Lock
import time
from prettytable import PrettyTable
import os
class Stud:
    def __init__(self, name, sex, results, passed, time=0):
        self.name = name
        self.sex = sex
        self.results = results
        self.passed = passed
        self.time = time

    def sex_converter(self):
        return "m" if self.sex == "М" else "f"


class Prepod:
    def __init__(self, name, sex, time=0, kill=0):
        self.name = name
        self.sex = sex
        self.time = time
        self.kill = kill

    def sex_converter(self):
        return "m" if self.sex == "М" else "f"


class Quests:
    def __init__(self, text, passed):
        self.text = text
        self.passed = passed

    def worder(self):
        return self.text.split()


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


def table_studs(studs, statistics):
    table = PrettyTable()
    table.field_names = ["Студент", "Статус"]
    table.align["Студент"] = "l"
    table.align["Статус"] = "c"
    
    for stud in studs:
        stud_stat = statistics.get(f"stud_{stud.name}", {})
        status = stud_stat.get("passed")
        if status is None:
            status_txt = "Очередь"
        elif status:
            status_txt = "Сдал"
        else:
            status_txt = "Провалил"
        table.add_row([stud.name, status_txt])
    
    return table


def table_prepos(preps, statistics, show_current=True):
    table = PrettyTable()
    if show_current:
        table.field_names = ["Экзаменатор", "Текущий студент", "Всего студентов", "Завалил", "Время работы"]
    else:
        table.field_names = ["Экзаменатор", "Всего студентов", "Завалил", "Время работы"]
    
    for prep in preps:
        current_stud = statistics.get(f"current_stud_{prep.name}", "-") if show_current else None
        total_stud = statistics.get(f"total_stud_{prep.name}", 0)
        prep_stat = statistics.get(f"prep_{prep.name}", {})
        kill = prep_stat.get("kill", 0)
        time_work = int(prep_stat.get("time", 0))
        
        if show_current:
            table.add_row([prep.name, current_stud, total_stud, kill, time_work])
        else:
            table.add_row([prep.name, total_stud, kill, time_work])
    
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
    series = [base ** (i + 1) for i in range(n)]
    s = sum(series)
    proba = [x / s for x in series]
    return proba


def asker(quests, mj_stud, mj_prep, prep_n, stud_n):
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

    return result


def stud_fate(result, prep_n, stud_n):
    mood = random.choices(["bad", "good", "norm"], weights=[1, 2, 5], k=1)[0]
    if mood == "bad":
        return "fail"
    elif mood == "good":
        return "pass"
    else:
        return "pass" if result >= 2 else "fail"


def exam_run(prep, studs, quests, lock, statistics):
    print(f"DEBUG: {prep.name} started", file=sys.stderr)  # ДОБАВИТЬ
    
    while True:
        lock.acquire()
        if not studs:
            statistics.pop(f"current_stud_{prep.name}", None)
            lock.release()
            print(f"DEBUG: {prep.name} finished - no students", file=sys.stderr)  # ДОБАВИТЬ
            break
        
        stud = studs.pop(0)
        statistics[f"current_stud_{prep.name}"] = stud.name
        lock.release()
        
        print(f"DEBUG: {prep.name} examining {stud.name}", file=sys.stderr)  # ДОБАВИТЬ
        
        # Record student start time
        student_start_time = time.monotonic()
        start_time = student_start_time
        pause_total = 0
        
        exam_time = random.randint(len(prep.name) - 1, len(prep.name) + 1)
        if exam_time < 0:
            exam_time = 1
        time.sleep(exam_time)
        
        result = asker(
            quests,
            prep.sex_converter(),
            stud.sex_converter(),
            prep.name,
            stud.name
        )
        stud.results += result
        
        fate = stud_fate(stud.results, prep.name, stud.name)
        stud.passed = fate == "pass"
        
        # Track student duration
        stud.time = int(time.monotonic() - student_start_time)
        
        key_stud = f"stud_{stud.name}"
        with lock:
            stud_stat = statistics.get(key_stud, {})
            stud_stat.update({
                'passed': stud.passed,
                'results': stud.results,
                'time': stud.time
            })
            statistics[key_stud] = stud_stat
            
            total = statistics.get(f"total_stud_{prep.name}", 0)
            statistics[f"total_stud_{prep.name}"] = total + 1
        
        key_prep = f"prep_{prep.name}"
        end_time = time.monotonic()
        with lock:
            prep_stat = statistics.get(key_prep, {})
            prep_stat['time'] = prep_stat.get('time', 0) + (end_time - start_time - pause_total)
            if fate == "fail":
                prep_stat['kill'] = prep_stat.get('kill', 0) + 1
            statistics[key_prep] = prep_stat
        
        time_now = time.monotonic()
        if time_now - start_time >= 30:
            with lock:
                statistics.pop(f"current_stud_{prep.name}", None)
            
            pause_start = time.monotonic()
            pause_time = random.randint(12, 18)
            print(f"Pause time: {pause_time}s, Prep: {prep.name}")
            time.sleep(pause_time)
            
            pause_duration = time.monotonic() - pause_start
            pause_total += pause_duration
            start_time = time.monotonic()

def exam_process():
    prepods, students, quests = importer()
    start_time_total = time.time()
    
    manager = Manager()
    studs = manager.list(students)
    statistics = manager.dict()
    lock = manager.Lock()
    processes = []

    for prep in prepods:
        p = Process(target=exam_run, args=(prep, studs, quests, lock, statistics))
        processes.append(p)
        p.start()

    # Даем процессам время запуститься
    time.sleep(0.2)
    
    try:
        while any(p.is_alive() for p in processes):
            time.sleep(0.5)
            
            # Очистка экрана и перемещение курсора в начало
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # 🔥 ВАЖНО: перемещаем курсор в верхний левый угол 🔥
            # Это работает в большинстве терминалов
            sys.stdout.write('\033[H')
            sys.stdout.flush()
            
            remaining = sum(1 for stud in students 
                          if statistics.get(f"stud_{stud.name}", {}).get("passed") is None)
            
            elapsed = int(time.time() - start_time_total)
            
            sorted_studs = sorted(students, key=lambda stud: sort_status(stud, statistics))
            sorted_preps = prepods
            
            # Теперь печатаем с самого верха

            print()
            print(table_studs(sorted_studs, statistics))
            print()
            print(table_prepos(sorted_preps, statistics, show_current=True))
            print()
            print(f"Время с момента начала экзамена: {elapsed} сек")
            
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        print("\nПрерывание...")
        sys.stdout.flush()
    
    for p in processes:
        p.join()
    time.sleep(0.2)
    
    # Final output
    os.system('cls' if os.name == 'nt' else 'clear')
    time.sleep(0.1)
    total_time = int(time.time() - start_time_total)
    
    # Final students table (passed/failed only)
    final_studs = []
    for stud in students:
        stat = statistics.get(f"stud_{stud.name}", {})
        passed = stat.get("passed")
        if passed is not None:
            final_studs.append((stud.name, passed, stat.get("time", 999999)))
    
    # Sort: passed first, then failed
    final_studs.sort(key=lambda x: (not x[1], x[2]))
    
    table_final = PrettyTable()
    table_final.field_names = ["Студент", "Статус"]
    for name, passed, _ in final_studs:
        table_final.add_row([name, "Сдал" if passed else "Провалил"])
    print()
    print(table_final)
    print()
    
    # Final examiners table (4 columns)
    print(table_prepos(prepods, statistics, show_current=False))
    print()
    
    print(f"Время с момента начала экзамена и до момента и его завершения: {elapsed} сек")
    # Best students (fastest to pass)
    passed_studs = [(name, time) for name, passed, time in final_studs if passed]
    if passed_studs:
        min_time = min(t for _, t in passed_studs)
        best_studs = [name for name, t in passed_studs if t == min_time]
        print(f"Имена лучших студентов: {', '.join(best_studs)}")
    else:
        print("Имена лучших студентов: нет")
    
    # Best examiners (lowest fail percentage)
    prep_stats = []
    for prep in prepods:
        total = statistics.get(f"total_stud_{prep.name}", 0)
        kill = statistics.get(f"prep_{prep.name}", {}).get("kill", 0)
        if total > 0:
            fail_pct = kill / total
            prep_stats.append((prep.name, fail_pct, kill, total))
    
    if prep_stats:
        min_fail = min(p[1] for p in prep_stats)
        best_preps = [p[0] for p in prep_stats if p[1] == min_fail]
        print(f"Имена лучших экзаменаторов: {', '.join(best_preps)}")
    else:
        print("Имена лучших экзаменаторов: нет")
    
    # Students to expel (failed and finished earlier than other failed)
    failed_studs = [(name, time) for name, passed, time in final_studs if not passed]
    if failed_studs:
        min_fail_time = min(t for _, t in failed_studs)
        expelled = [name for name, t in failed_studs if t == min_fail_time]
        print(f"Имена студентов, которых после экзамена отчислят: {', '.join(expelled)}")
    else:
        print("Имена студентов, которых после экзамена отчислят: нет")
    
    # Best questions (most correct answers)
    # Track question stats
    question_stats = {}
    for quest in quests:
        question_stats[quest.text] = 0
    
    for stud in students:
        stud_stat = statistics.get(f"stud_{stud.name}", {})
        # This part would need additional tracking in exam_run
        # For now, placeholder
    print("Лучшие вопросы: (требуется дополнительное логирование)")
    
    # Exam success
    total_passed = sum(1 for _, passed, _ in final_studs if passed)
    total_students = len(final_studs)
    if total_students > 0:
        success_rate = total_passed / total_students * 100
        print(f"Вывод: экзамен {'удался' if success_rate > 85 else 'не удался'}")


if __name__ == "__main__":
    exam_process()