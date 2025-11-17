''' Создайте отдельный процесс для каждого экзаменатора, чтобы они работали параллельно.
# Каждый процесс будет принимать студентов из общей очереди (например, используя multiprocessing.Queue для межпроцессного взаимодействия).
# Процесс экзаменатора внутри себя реализует логику экзамена с вопросами и ответами, а также учитывает 30-секундный лимит до обеда и случайную задержку после него.'''

from multiprocessing import Process, Manager
import time
import random

def importer():
	with open("examiners.txt", "r", encoding="utf-8") as file:
		lines = file.readlines()
	examers = [line.split()[0] for line in lines if line.strip()]
	with open("students.txt", "r", encoding="utf-8") as file:
		lines = file.readlines()
	studs = [line.split()[0] for line in lines if line.strip()]
	with open("questions.txt", "r", encoding="utf-8") as file:
		quests = file.readlines()

	return examers, studs, quests

def exam_time(examer, studs, quests, times):

	start_time = time.monotonic()
	pause_total = 0

	
	while True:
		try:
			stud = studs.pop(0)
			print(stud)
		except IndexError:
			break

		exam_time = random.randint(len(examer)-1, len(examer)+1)
		print(f"examer: {examer}, exam time: {exam_time}")
		time.sleep(exam_time)

		time_now = time.monotonic()
		if time_now - start_time >= 30:
			pause_start = time.monotonic()
			pause_time = random.randint(12, 18)
			print(f"gehen wir nach hause es verboten ... pause time: {pause_time}, Prof: {examer}")
			time.sleep(pause_time)
			pause_end = time.monotonic()
			pause_duration = pause_end - pause_start
			pause_total += pause_duration
			start_time = time.monotonic()
	
		end_time = time.monotonic()
		times[examer] = end_time - start_time - pause_total
		
def exam_process():
	
	examers, students, quests = importer()
	manager = Manager()
	studs = manager.list(students)
	times = manager.dict()
	processes = []
	for e in examers:
		p = Process(target=exam_time, args=(e, studs, quests, times))
		processes.append(p)
		p.start()

	for p in processes:
		p.join()

if __name__ == "__main__":
	exam_process()

