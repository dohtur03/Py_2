from classes_import import Stud, Prepod, Quests
from load_data import importer
from tables import table_prepos, table_studs, sort_status
from calculate_fate import golden, asker, stud_fate
from exam_engine import exam_run
from processor_x import exam_process
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

if __name__ == "__main__":
    exam_process()