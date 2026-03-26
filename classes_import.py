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
