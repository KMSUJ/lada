class Ballot():
  def __init__(self, preference = list(), reject = set()):
    self.preference = preference
    self.reject = reject
    self.value = 1
    self.check_active()
    
  def check_active(self):
    if len(self.preference) is 0:
      self.value = 0
    
  def discard(self, candidate):
    self.preference.remove(candidate)
    self.check_active()
    
  def first_preference(self):
    return self.preference[0]
