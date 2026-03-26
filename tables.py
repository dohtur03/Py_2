from prettytable import PrettyTable

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