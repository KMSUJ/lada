class Ballot():
  def __init__(self):
    self.preferences = list()
    self.rejected = set()
    self.value = 1
    
  def check_active(self):
    if len(self.preferences) is 0:
      self.value = 0
    
  def discard_candidate(self, name):
    self.preferences.remove(name)
    self.check_active()
    
  def first_preference(self):
    return self.preferences[0]
