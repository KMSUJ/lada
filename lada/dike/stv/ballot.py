class Ballot():
  def __init__(self, preference = list(), reject = set()):
    self.preference = list(preference)
    self.reject = set(reject)
    self.value = 1
    self.check_active()

    if len(set(self.preference) & self.reject):
      raise ValueError(f'Ballot preference and reject has non-empty intersection: {self}')

    if len(set(self.preference)) != len(self.preference):
      raise ValueError(f'Ballot preference contains duplicates: {self}')
    
  def check_active(self):
    if len(self.preference) is 0:
      self.value = 0
    
  def discard(self, candidate):
    self.preference.remove(candidate)
    self.check_active()
    
  def first_preference(self):
    return self.preference[0]

  def __repr__(self):
    return f'Ballot({self.preference}, {self.reject})'
