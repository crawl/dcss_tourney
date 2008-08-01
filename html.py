import query

STOCK_COLUMNS = \
    [ ('player', 'Player'),
      ('score', 'Score', True),
      ('charabbrev', 'Character'),
      ('turn', 'Turns'),
      ('duration', 'Duration'),
      ('god', 'God'),
      ('runes', 'Runes'),
      ('end_time', 'Time', True)
    ]

def fixup_column(col, data):
  if col.find('time') != -1:
    return pretty_date(data)
  elif col.find('duration') != -1:
    return pretty_dur(data)
  return data

def pretty_dur(dur):
  secs = dur % 60
  dur /= 60
  mins = dur % 60
  dur /= 60
  hours = dur % 24
  dur /= 24
  days = dur
  stime = "%02d:%02d:%02d" % (hours, mins, secs)
  if days > 0:
    stime = str(days) + ", " + stime
  return stime

def pretty_date(date):
  return "%04d-%02d-%02d %02d:%02d:%02d" % (date.year, date.month, date.day,
                                            date.hour, date.minute,
                                            date.second)

def games_table(games, first=None, excluding=None, columns=None,
                cls=None, count=True):
  columns = columns or STOCK_COLUMNS

  if excluding:
    columns = [c for c in columns if c[0] not in excluding]

  if first and not isinstance(first, tuple):
    first = (first, 1)

  if first and columns[0][0] != first[0]:
    firstc = [ c for c in columns if c[0] == first[0] ]
    columns = [ c for c in columns if c[0] != first[0] ]
    columns.insert( first[1], firstc[0] )

  if cls:
    cls = ''' class="%s"''' % cls
  out = '''<table%s>\n<tr>''' % (cls or '')
  if count:
    out += "<th></th>"
  for col in columns:
    out += "<th>%s</th>" % col[1]
  out += "</tr>\n"
  odd = True
  ngame = 0
  for game in games:
    ngame += 1
    out += '''<tr class="%s">''' % (odd and "odd" or "even")

    if count:
      out += '''<td class="numeric">%s</td>''' % ngame

    for c in columns:
      val = fixup_column(c[0], game.get(c[0]) or '')
      tcls = isinstance(val, str) and "celltext" or "numeric"
      out += '''<td class="%s">''' % tcls

      need_link = len(c) >= 3 and c[2]
      if need_link:
        out += r'<a href="%s">' % query.morgue_link(game)
      out += str(val)
      if need_link:
        out += '</a>'
      out += '</td>'
    out += "</tr>\n"
  out += "</table>\n"
  return out
