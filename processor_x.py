import sys
import time
from multiprocessing import Process, Manager
from prettytable import PrettyTable
from load_data import importer
from tables import table_studs, table_prepos, sort_status
from exam_engine import exam_run

def setup_shared_data(students, quests):
    #Создает разделяемые данные для процессов
    manager = Manager()
    studs = manager.list(students)
    statistics = manager.dict()
    question_stats = manager.dict()
    lock = manager.Lock()
    
    for quest in quests:
        question_stats[quest.text] = 0
    
    return studs, statistics, question_stats, lock


def start_processes(prepods, studs, quests, lock, statistics, question_stats):
    #Запускает процессы экзаменаторов
    processes = []
    for prep in prepods:
        p = Process(target=exam_run, args=(prep, studs, quests, lock, statistics, question_stats))
        processes.append(p)
        p.start()
    return processes


def display_live_update(students, prepods, statistics, start_time_total):
    #Выводит live-обновление таблиц
    remaining = sum(1 for stud in students 
                  if statistics.get(f"stud_{stud.name}", {}).get("passed") is None)
    
    elapsed = int(time.time() - start_time_total)
    
    sorted_studs = sorted(students, key=lambda stud: sort_status(stud, statistics))
    sorted_preps = prepods
    
    print()
    print(table_studs(sorted_studs, statistics))
    print()
    print(table_prepos(sorted_preps, statistics, show_current=True))
    print()
    print(f"Осталось в очереди: {remaining}")
    print(f"Время с момента начала экзамена: {elapsed} сек")
    
    sys.stdout.flush()


def wait_for_processes(processes):
    #Ожидает завершения всех процессов
    for p in processes:
        p.join()


def collect_final_students(students, statistics):
    #Собирает итоговые данные студентов
    final_studs = []
    for stud in students:
        stat = statistics.get(f"stud_{stud.name}", {})
        passed = stat.get("passed")
        if passed is not None:
            final_studs.append((stud.name, passed, stat.get("time", 999999)))
    
    final_studs.sort(key=lambda x: (not x[1], x[2]))
    return final_studs


def print_final_students_table(final_studs):
    #Выводит итоговую таблицу студентов
    table_final = PrettyTable()
    table_final.field_names = ["Студент", "Статус"]
    for name, passed, _ in final_studs:
        table_final.add_row([name, "Сдал" if passed else "Провалил"])
    print(table_final)
    print()


def print_best_students(final_studs):
    #Выводит лучших студентов
    passed_studs = [(name, time) for name, passed, time in final_studs if passed]
    if passed_studs:
        min_time = min(t for _, t in passed_studs)
        best_studs = [name for name, t in passed_studs if t == min_time]
        print(f"Имена лучших студентов: {', '.join(best_studs)}")
    else:
        print("Имена лучших студентов: нет")


def print_best_examiners(prepods, statistics):
    #Выводит лучших экзаменаторов
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


def print_expelled_students(final_studs):
    #Выводит студентов для отчисления
    failed_studs = [(name, time) for name, passed, time in final_studs if not passed]
    if failed_studs:
        min_fail_time = min(t for _, t in failed_studs)
        expelled = [name for name, t in failed_studs if t == min_fail_time]
        print(f"Имена студентов, которых после экзамена отчислят: {', '.join(expelled)}")
    else:
        print("Имена студентов, которых после экзамена отчислят: нет")


def print_best_questions(question_stats):
    #Выводит лучшие вопросы
    if question_stats:
        q_stats = dict(question_stats)
        if q_stats:
            max_correct = max(q_stats.values())
            if max_correct > 0:
                best_questions = [q for q, count in q_stats.items() if count == max_correct]
                best_questions_short = [q[:50] + "..." if len(q) > 50 else q for q in best_questions]
                print(f"Лучшие вопросы: {', '.join(best_questions_short)}")
            else:
                print("Лучшие вопросы: нет (никто не ответил правильно)")
        else:
            print("Лучшие вопросы: нет")
    else:
        print("Лучшие вопросы: нет")


def print_exam_result(final_studs):
    #Выводит результат экзамена (удался/не удался)
    total_passed = sum(1 for _, passed, _ in final_studs if passed)
    total_students = len(final_studs)
    if total_students > 0:
        success_rate = total_passed / total_students * 100
        print(f"Вывод: экзамен {'удался' if success_rate > 85 else 'не удался'}")
        print(f"Сдало {total_passed} из {total_students} ({success_rate:.1f}%)")


def exam_process():
    #Главный процесс экзамена
    prepods, students, quests = importer()
    start_time_total = time.time()
    
    studs, statistics, question_stats, lock = setup_shared_data(students, quests)
    processes = start_processes(prepods, studs, quests, lock, statistics, question_stats)
    
    time.sleep(0.2)
    
    try:
        while any(p.is_alive() for p in processes):
            time.sleep(0.5)
            sys.stdout.write('\033[2J\033[H')
            sys.stdout.flush()
            display_live_update(students, prepods, statistics, start_time_total)
    except KeyboardInterrupt:
        print("\nПрерывание...")
        sys.stdout.flush()
    
    wait_for_processes(processes)
    
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()
    total_time = int(time.time() - start_time_total)
    
    final_studs = collect_final_students(students, statistics)
    
    print()
    print_final_students_table(final_studs)
    print(table_prepos(prepods, statistics, show_current=False))
    print()
    print(f"Время с момента начала экзамена и до момента его завершения: {total_time}")
    
    print_best_students(final_studs)
    print_best_examiners(prepods, statistics)
    print_expelled_students(final_studs)
    print_best_questions(question_stats)
    print_exam_result(final_studs)
    
    sys.stdout.flush()