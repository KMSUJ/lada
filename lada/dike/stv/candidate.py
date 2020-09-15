import random as rnd

class Candidate():
  def __init__(self, id=""):
    self.id = id
    self.score = list()
    
  def __lt__(self, other):
    for i in range(-1,min(len(self.score),len(other.score))):
      if self.score[i] < other.score[i]:
        return True
      elif self.score[i] > other.score[i]:
        return False
    print(f'A random choice has been made in favour of ') # log this properly
    return rnd.random() < 0.5
  
  def __eq__(self, other):
    # necessary for being a dictionary key
    return self.id == other.id

  def __hash__(self):
    # necessary for being a dictionary key
    return hash(self.id)
