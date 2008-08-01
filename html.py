import query, crawl_utils

STOCK_WIN_COLUMNS = \
    [ ('player', 'Player'),
      ('score', 'Score', True),
      ('charabbrev', 'Character'),
      ('turn', 'Turns'),
      ('duration', 'Duration'),
      ('god', 'God'),
      ('runes', 'Runes'),
      ('end_time', 'Time', True)
    ]

STOCK_COLUMNS = \
    [ ('player', 'Player'),
      ('score', 'Score', True),
      ('charabbrev', 'Character'),
      ('place', 'Place'),
      ('verb_msg', 'Death'),
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

def pretty_time(time):
  return "%04d-%02d-%02d %02d:%02d:%02d" % (time.tm_year, time.tm_mon,
                                            time.tm_mday,
                                            time.tm_hour, time.tm_min,
                                            time.tm_sec)

def wrap_tuple(x):
  if isinstance(x, tuple):
    return x
  else:
    return (x,)

def table_text(headers, data, cls=None, count=True, link=None):
  if cls:
    cls = ''' class="%s"''' % cls
  out = '''<table%s>\n<tr>''' % (cls or '')

  headers = [ wrap_tuple(x) for x in headers ]

  if count:
    out += "<th></th>"
  for head in headers:
    out += "<th>%s</th>" % head[0]
  out += "</tr>\n"
  odd = True

  nrow = 0
  for row in data:
    nrow += 1
    out += '''<tr class="%s">''' % (odd and "odd" or "even")
    odd = not odd

    if count:
      out += '''<td class="numeric">%s</td>''' % nrow

    for c in range(len(headers)):
      val = row[c]
      tcls = isinstance(val, str) and "celltext" or "numeric"
      out += '''<td class="%s">''' % tcls
      out += str(val)
      out += '</td>'
    out += "</tr>\n"
  out += '</table>\n'
  return out

def games_table(games, first=None, excluding=None, columns=None,
                cls=None, count=True, win=True):
  columns = columns or (win and STOCK_WIN_COLUMNS or STOCK_COLUMNS)

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
    odd = not odd

    if count:
      out += '''<td class="numeric">%s</td>''' % ngame

    for c in columns:
      val = fixup_column(c[0], game.get(c[0]) or '')
      tcls = isinstance(val, str) and "celltext" or "numeric"
      out += '''<td class="%s">''' % tcls

      need_link = len(c) >= 3 and c[2]
      if need_link:
        out += r'<a href="%s">' % crawl_utils.morgue_link(game)
      out += str(val)
      if need_link:
        out += '</a>'
      out += '</td>'
    out += "</tr>\n"
  out += "</table>\n"
  return out

def combo_highscorers(c):
  hs = query.get_top_combo_highscorers(c)
  return table_text( [ 'Player', 'Combo scores' ],
                     hs )

def deepest_xl1_games(c):
  games = query.get_deepest_xl1_games(c)
  return games_table(games, first = 'place', win=False)

def hyperlink_games(games, field):
  hyperlinks = [ crawl_utils.morgue_link(g) for g in games ]
  text = [ '<a href="%s">%s</a>' % (link, g[field])
           for link, g in zip(hyperlinks, games) ]
  return ", ".join(text)

def best_streaks(c):
  streaks = query.get_top_streaks(c)
  # Replace the list of streak games with hyperlinks.
  for s in streaks:
    streak_games = s.pop()
    streak_start = streak_games[0]['start_time']
    s.insert(2, pretty_date(streak_start))
    # Also fixup end date.
    s[3] = pretty_date(s[3])
    s.append( hyperlink_games(streak_games, 'charabbrev') )

  return table_text( [ 'Player', 'Streak', 'Start', 'End', 'Games' ],
                     streaks )

def best_clans(c):
  clans = query.get_top_clan_scores(c)
  return table_text( [ 'Clan', 'Captain', 'Points' ],
                     clans )

def clan_unique_kills(c):
  ukills = query.get_top_clan_unique_kills(c)
  return table_text( [ 'Clan', 'Captain', 'Unique Kills' ],
                     ukills )

def clan_combo_highscores(c):
  return table_text( [ 'Clan', 'Captain', 'Combo Highscores' ],
                     query.get_top_clan_combos(c) )
