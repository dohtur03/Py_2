import random

class Stud:
    def __init__(self, name, sex, passed):
        self.name = name
        self.sex = sex
        self.passed = passed

    def sex_converter(self):
        return "m" if self.sex == "М" else "j"

def importer():
      with open("examiners.txt", "r", encoding="utf-8") as file:
          lines = file.readlines()
      examers = [line.split()[0] for line in lines if line.strip()]

      studs = []
      with open("students.txt", "r", encoding="utf-8") as file:
          for line in file:
              params = line.strip().split()
              if len(params) == 2:
                  name, sex = params
                  studs.append(Stud(name, sex, 1))
                            
      with open("questions.txt", "r", encoding="utf-8") as file:
          quests = file.readlines()
  
      return examers, studs, quests

def golden(n):
    phi = 1.618
    proba = []
    rest = 1.0
    current = 1/phi
    for i in range (n):
        if i == 0:
            proba.append(current)
            rest -= current
        else:
            current = rest/phi
            proba.append(current)
            rest -= current

    s = sum(proba)
    proba = [p/s for p in proba]
    return proba

def stud_fate(quests, mj):
    fate_quests = random.sample(quests, 3)
    for quest in fate_quests:
        quest = quest.strip()
        words = quest.split()
        n = len(words)
        proba = golden(n)
        if mj != "m":
            proba.reverse()
        answer = random.choices(words, weights = proba, k=1)[0]
        print(f"chosen word: {answer}\nwords: {words}\nprobability: {proba}")
        
def main():
    examers, studs, quests = importer()
    for stud in studs:
        print(f"student: {stud.name}")
        sex = stud.sex_converter()
        stud_fate(quests, sex)

if __name__ == "__main__":
    main()
