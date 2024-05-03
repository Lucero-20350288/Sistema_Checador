class Department:

  def __init__(self, cid, name):
    self.cid = cid
    self.name = name 
  def toDBCollection(self):
    return{
      'cid': self.cid,
      'name': self.name
    }