import random
import time
from calculate_fate import asker, stud_fate

def get_student(studs, prep, lock, statistics):
    #Взять студента из очереди
    lock.acquire()
    if not studs:
        statistics.pop(f"current_stud_{prep.name}", None)
        lock.release()
        return None, None
    stud = studs.pop(0)
    statistics[f"current_stud_{prep.name}"] = stud.name
    lock.release()
    return stud, time.monotonic()


def conduct_exam(prep, stud, quests, question_stats):
    #Провести экзамен для одного студента
    exam_time = random.randint(len(prep.name) - 1, len(prep.name) + 1)
    if exam_time < 0:
        exam_time = 1
    time.sleep(exam_time)
    
    result = asker(
        quests,
        prep.sex_converter(),
        stud.sex_converter(),
        prep.name,
        stud.name,
        question_stats
    )
    stud.results += result
    
    fate = stud_fate(stud.results, prep.name, stud.name)
    stud.passed = fate == "pass"
    stud.time = int(time.monotonic() - stud.start_time)
    
    return result, fate

def save_student_stats(stud, prep, lock, statistics):
    #Сохранить статистику студента
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


def save_examiner_stats(prep, start_time, pause_total, fate, lock, statistics):
    #Сохранить статистику экзаменатора
    key_prep = f"prep_{prep.name}"
    end_time = time.monotonic()
    with lock:
        prep_stat = statistics.get(key_prep, {})
        prep_stat['time'] = prep_stat.get('time', 0) + (end_time - start_time - pause_total)
        if fate == "fail":
            prep_stat['kill'] = prep_stat.get('kill', 0) + 1
        statistics[key_prep] = prep_stat
    return end_time


def handle_lunch_break(prep, start_time, pause_total, lock, statistics):
    #Обед!
    with lock:
        statistics.pop(f"current_stud_{prep.name}", None)
    
    pause_start = time.monotonic()
    pause_time = random.randint(12, 18)
    print(f"Pause time: {pause_time}s, Prep: {prep.name}")
    time.sleep(pause_time)
    
    pause_duration = time.monotonic() - pause_start
    pause_total += pause_duration
    new_start_time = time.monotonic()
    
    return pause_total, new_start_time

def exam_run(prep, studs, quests, lock, statistics, question_stats):
    #Цикл экзаменатора
    while True:
        # Взять студента
        stud, student_start_time = get_student(studs, prep, lock, statistics)
        if stud is None:
            break
        
        stud.start_time = student_start_time
        start_time = student_start_time
        pause_total = 0
        
        # Провести экзамен
        result, fate = conduct_exam(prep, stud, quests, question_stats)
        
        # Сохранить статистику
        save_student_stats(stud, prep, lock, statistics)
        save_examiner_stats(prep, start_time, pause_total, fate, lock, statistics)
        
        # Проверить обед
        time_now = time.monotonic()
        if time_now - start_time >= 30:
            pause_total, start_time = handle_lunch_break(prep, start_time, pause_total, lock, statistics)