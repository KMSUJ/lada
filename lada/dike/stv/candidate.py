import random as rnd

class Candidate():
  def __init__(self, name=""):
    self.name = name
    self.score = list()
    
  def __lt__(self, other):
    for i in range[-1,min(len(self),len(other))]:
      if self.score[i] < other.score[i]:
        return True
    return rnd.random() < 0.5
  
  def __eq__(self, other):
    # necessary for being a dictionary key
    return self.name == other.name

  def __hash__(self):
    # necessary for being a dictionary key
    return hash(self.name)