class Query:
  def __init__(self, qstring, *values):
    self.query = qstring
    self.values = values

  def append(self, qseg, *values):
    self.query += qseg
    self.values += values

  def vappend(self, *values):
    self.values += values

  def execute(self, cursor):
    """Executes query on the supplied cursor."""
    self.query = self.query.strip()
    if not self.query.endswith(';'):
      self.query += ';'
    cursor.execute(self.query, self.values)

  def row(self, cursor):
    """Executes query and returns the first row tuple, or None if there are no
    rows."""
    self.execute(cursor)
    return cursor.fetchone()

  def rows(self, cursor):
    self.execute(cursor)
    return cursor.fetchall()

  def count(self, cursor, msg=None, exc=Exception):
    """Executes a SELECT COUNT(foo) query and returns the count. If there is
    not at least one row, raises an exception."""
    self.execute(cursor)
    row = cursor.fetchone()
    if row is None:
      raise exc(msg or "No rows returned for %s" % self.query)
    return row[0]

  first = count
