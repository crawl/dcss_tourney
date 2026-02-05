import collections
import decimal
import query, crawl_utils, time, datetime
import loaddb
import sys
import logging
import json

from crawl_utils import clan_link, player_link, linked_text
import crawl_utils
import re

PseudoCol = collections.namedtuple("PseudoCol", ("html_display_name", "numeric_data", "transform_fn"))

EXT_WIN_COLUMNS = \
    [ ('score', 'Score', True),
      ('race', 'Species'),
      ('class', 'Background'),
      ('god', 'God'),
      ('title', 'Title'),
      ('xl', 'XL'),
      ('turn', 'Turns'),
      ('duration', 'Duration'),
      ('runes', 'Runes'),
      ('end_time', 'Date')
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

STOCK_WIN_COLUMNS = [col for col in STOCK_COLUMNS if col[0] not in ('place', 'verb_msg')]

EXT_COLUMNS = \
    [ ('score', 'Score', True),
      ('race', 'Species'),
      ('class', 'Background'),
      ('god', 'God'),
      ('title', 'Title'),
      ('place', 'Place'),
      ('verb_msg', 'Death'),
      ('xl', 'XL'),
      ('turn', 'Turns'),
      ('duration', 'Duration'),
      ('runes', 'Runes'),
      ('end_time', 'Date')
    ]

WHERE_COLUMNS = \
    [ ('race', 'Species'),
      ('cls', 'Background'),
      ('god', 'God'),
      ('title', 'Title'),
      ('place', 'Place'),
      ('xl', 'XL'),
      ('turn', 'Turns'),
      ('time', 'Time'),
      ('status', 'Status')
    ]

R_STR_DATE = re.compile(r'^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})')

def fixup_column(col, data, game):
  if col.find('time') != -1:
    return pretty_date(data)
  elif col.find('duration') != -1:
    return pretty_dur(data)
  elif col == 'place' and game.get('killertype') == 'winning':
    return ''
  elif col == 'score' and data == '':
    return 0
  return data

def pretty_dur(dur):
  if (not dur) and dur != 0:
    return ""
  try:
    secs = dur % 60
  except:
    print("FAIL on %s" % dur)
    raise
  dur /= 60
  mins = dur % 60
  dur /= 60
  hours = dur
  stime = "%d:%02d:%02d" % (hours, mins, secs)

  return stime

def is_stringlike(s):
  try:
    return isinstance(s, (str, unicode)) #py2
  except:
    return isinstance(s, (str, bytes)) #py3

def pretty_date(date):
  if not date:
    return ''

  if is_stringlike(date):
    m = R_STR_DATE.search(date)
    if not m:
      return date
    return "%s-%s-%s %s:%s:%s" % (m.group(1), m.group(2), m.group(3),
                                  m.group(4), m.group(5), m.group(6))

  return "%04d-%02d-%02d %02d:%02d:%02d" % (date.year, date.month, date.day,
                                            date.hour, date.minute,
                                            date.second)

def pretty_time(time):
  return "%04d-%02d-%02d %02d:%02d:%02d" % (time.tm_year, time.tm_mon,
                                            time.tm_mday,
                                            time.tm_hour, time.tm_min,
                                            time.tm_sec)

def how_old(date, bold_cutoff = 0): #cutoff in hours
  if not date:
    return None,None
  if type(date) == "string":
    delta = datetime.datetime.utcnow() - query.time_from_str(date)
  else:
    delta = datetime.datetime.utcnow() - date
  h = 24*delta.days + delta.seconds / 60 / 60
  m = (delta.seconds / 60) % 60
  s = delta.seconds % 60
  if h < 0:
    return "0:00:00", (0 < bold_cutoff)
  return ("%d:%02d:%02d" % (h, m, s)), (h < bold_cutoff)

def update_time():
  return '''<div class="row">
              <small>Last updated %s UTC.</small>
            </div>''' % pretty_time(time.gmtime())

def wrap_tuple(x):
  if isinstance(x, tuple):
    return x
  else:
    return (x,)

def is_player_header(header):
  return header.lower() in ['player', 'captain']

def is_clan_header(header):
  return header.lower() in ['clan', 'team', 'teamname']


def _is_numeric_table_value(value, header=""):
  if is_player_header(header) or is_clan_header(header):
    return False
  if isinstance(value, (int, float, decimal.Decimal)):
    return True
  if is_stringlike(value):
    if value.isdigit():
      return True
    try:
      float(value)
    except ValueError:
      return False
    return True
  return False

# DEPRECATED: Build a wrapper function around _table to replace this
def table_text(headers, data, count=True,
               place_column=-1, stub_text='No data', skip=False, bold=False,
               extra_wide_support=False, caption=None, datatables=False):
  """Create a HTML table of players.

  :param List[str] headers: Column headers
  :param List[List[str]] data: Column data
  :param bool count: Add a "count" column at the start
  :param int place_column: Use this column to determine ranking ties (-1 there are no ties)
  :param str stub_text: Text to show if the table has no data.
  :param bool skip: Use sparse rank numbers (eg two people at rank n means next rank is n+2)
  :param bool bold: Mark winning rows
  :param Optional[str] caption: Table description (for screen readers).

  """
  table_classes = set(("table",
    "table-hover",
    "table-striped",
    "table-dark",
  ))
  if extra_wide_support:
    table_classes.add("table-bordered")
  if datatables:
    table_classes.add("dcss-datatable-wide" if extra_wide_support else "dcss-datatable")
    table_classes.add("nowrap") # keep table rows on one line
  else:
    table_classes.add("table-sm")
    table_classes.add("w-auto")
  out = '''<div class="table-responsive">\n<table class="%s">\n''' % (" ".join(table_classes))

  if caption is not None:
    out += '''<caption class="sr-only">%s</caption>\n''' % caption

  out += '''<thead>\n<tr>'''

  headers = [ wrap_tuple(x) for x in headers ]

  if count:
    out += '''<th scope="col">#</th>'''
  for head in headers:
    out += '''<th scope="col">%s</th>''' % head[0]
  out += "</tr>\n</thead>\n"

  if not data:
    ncols = len(headers) + (1 if count else 0)
    out += '''<tr><td colspan='%s'>%s</td></tr>''' % (ncols, stub_text)

  # XXX: this is something to do with ranking?
  nplace = 0
  rplace = 0
  last_value = None

  for row in data:
    # TODO: not sure this is necessary with DataTables?
    if bold and row[-1]:
      # Invert colours
      out += '''<tr class="table-secondary">'''
    else:
      out += '''<tr class="">'''

    rplace += 1
    if place_column == -1:
      nplace += 1
    elif last_value != row[place_column]:
      nplace += 1
      if skip:
        nplace = rplace
      last_value = row[place_column]

    if count:
      out += '''<th class="%s" scope="row">%s</th>''' % (
        "py-1 px-2" if datatables else "",
        nplace,
      )

    for c in range(len(headers)):
      call_classes = set()
      if datatables:
        # More compact display
        call_classes.update(["py-1", "px-2"])
      val = row[c]
      if isinstance(val, str):
        # TODO: is there a better sort value than something like this to use?
        sort_val = "9999999999" if val == "" or val == "-" else val
        val_embedded_str = sort_val.find('"')
        if val_embedded_str > -1:
          # pretty hacky: if there is an embedded '"', we take the contents of
          # that, in order to handle clan links. Better would be to construct the
          # clan link in this function (like player), but doing so is annoyingly
          # complicated. Could also extract the inner text.
          try:
            sort_val = sort_val[val_embedded_str:].split('"')[1]
          except:
            print(sort_val)
            raise
      else:
        sort_val = str(val)
      header = headers[c]

      numeric_col = _is_numeric_table_value(val, header[0])
      pseudo_numeric_col = val == '-'
      if numeric_col:
        val = '{:,}'.format(isinstance(val, str) and int(val) or val)
      if numeric_col or pseudo_numeric_col:
        call_classes.add("text-right")
        call_classes.add("text-monospace")
      if extra_wide_support and is_player_header(header[0]):
        call_classes.add('text-dark')

      if c == place_column:
        out += '''<th class="%s" scope="row">''' % " ".join(call_classes)
      else:
        out += '''<td class="%s" data-sort="%s">''' % (
                  " ".join(call_classes),
                  sort_val)
      val = str(val)
      if is_player_header(header[0]):
        val = linked_text(val, player_link)
      out += val
      if c == place_column:
        out += '</th>'
      else:
        out += '</td>'
    out += "</tr>\n"
  out += '</table>\n</div>'
  return out

# DEPRECATED: Build a wrapper function around _table to replace this
def games_table(games, first=None, excluding=None, columns=None,
                including=None,
                count=True, win=True,
                place_column=-1, skip=False,
                caption=None):
  """Create a HTML table of games.

  :param List[List[str]] games: Games to list
  :param bool first: ?
  :param Optional[List[str]] excluding: If set, a list of column names to exclude from columns
  :param Optional[List[Union[Tuple[str,str],Tuple[str,str,bool]]]] columns: If set, a list of colum descriptions. The format is (sql column name, html column name[, link col=False]). Defaults to STOCK_WIN_COLUMNS if win is True, otherwise STOCK_COLUMNS.
  :param Optional[List[Tuple[int,Union[Tuple[str,str],Tuple[str,str,bool]]]]] including: If set, a list of (pos, name) tuples of columns to include. pos is the position to insert at.
  :param bool count: Add a count column at the start.
  :param bool win: Select default columns if `columns` is None. See `columns` param for more info.
  :param Optional[str] caption: Table description (for screen readers).
  """
  if columns is None:
    columns = STOCK_WIN_COLUMNS if win else STOCK_COLUMNS

  # Copy columns.
  columns = list(columns)

  if excluding:
    columns = [c for c in columns if c[0] not in excluding]

  if including:
    for pos, col in including:
      columns.insert(pos, col)

  if first and not isinstance(first, tuple):
    first = (first, 1)

  if first and columns[0][0] != first[0]:
    firstc = [ c for c in columns if c[0] == first[0] ]
    columns = [ c for c in columns if c[0] != first[0] ]
    columns.insert( first[1], firstc[0] )

  table_classes = set(("table",
    "table-sm",
    "table-hover",
    "table-striped",
    "table-dark",
    "w-auto",
    ))

  out = '''<div class="table-responsive">\n<table class="%s">\n''' % " ".join(table_classes)

  if caption is not None:
    out += '''<caption class="sr-only">%s</caption>\n''' % caption
  out += '''<thead>\n<tr>'''
  if count:
    out += '''<th scope="col">#</th>'''
  for col in columns:
    out += '''<th scope="col">%s</th>''' % col[1]
  out += "</tr>\n</thead>\n"

  if not games:
    ncols = len(columns) + (1 if count else 0)
    out += '''<tr><td colspan='%s'>No games</td></tr>''' % ncols

  # XXX: this is something to do with ranking?
  nplace = 0
  rplace = 0
  last_value = None

  for game in games:
    row_class = "table-secondary" if game.get('killertype') == 'winning' else ""

    out += '''<tr class="%s">''' % row_class

    rplace += 1
    if place_column == -1:
      nplace += 1
    elif last_value != game.get(columns[place_column][0]):
      nplace += 1
      if skip:
        nplace = rplace
      last_value = game.get(columns[place_column][0])

    if count:
      out += '''<th class="text-right" scope="row">%s</th>''' % nplace

    for i, c in enumerate(columns):
      val = fixup_column(c[0], game.get(c[0]) or '', game)
      numeric_col = _is_numeric_table_value(val, c[0])
      pseudo_numeric_col = val == '-'
      if numeric_col:
        val = '{:,}'.format(isinstance(val, str) and int(val) or val)
      td_class = "text-right text-monospace" if (numeric_col or pseudo_numeric_col) else ""
      if i == place_column:
        out += '''<th class="%s" scope="row">''' % td_class
      else:
        out += '''<td class="%s">''' % td_class

      # XXX: this should change
      need_link = len(c) >= 3 and c[2]
      if need_link:
        try:
          out += r'<a href="%s">' % crawl_utils.morgue_link(game)
        except:
          sys.stderr.write("Error processing game: " + loaddb.xlog_str(game))
          raise
      elif is_player_header(c[1]):
        val = linked_text(val, player_link)
      out += str(val)
      if need_link:
        out += '</a>'
      if i == place_column:
        out += '</th>'
      else:
        out += '</td>'
    out += "</tr>\n"
  out += "</table>\n</div>\n"
  return out

def _table(columns, rows, row_classes_fn=None, brief=False):
  # type: (Sequence[ColumnDisplaySpec], Sequence[Sequence[Any]], Optional[Callable[[Any], str]]) -> str
  '''
  Display a HTML table.

  @param columns: Details about columns in display order.
  @param rows: Rows of data in display order.
  @param row_classes_fn: If set, a function which gets passed each row to
                         determine classes for its <tr>.
  '''

  n_columns = len(columns)

  out = ''

  table_classes = set(("table",
    "table-hover",
    "table-striped",
    "table-dark",
    ))
  if brief:
    table_classes.add("dcss-datatable-compact")
  else:
    table_classes.add("dcss-datatable")
    table_classes.add("table-bordered")

  out += '<div class="table-responsive">\n'
  out += '<table class="{classes}">\n'.format(classes=" ".join(table_classes))

  # Table column headers
  out += '<thead>\n'
  out += '<tr>'
  for column in columns:
    out += '<th>{name}</th>'.format(name=column.html_display_name)
  out += '</tr>\n'
  out += '</thead>\n'

  for row in rows:
    if len(row) != n_columns:
      raise ValueError("Row length {n_row} != columns length {n_cols}. Row data: {row} Col data: {cols}".format(
        n_row=len(row),
        n_cols=n_columns,
        row=repr(row),
        cols=columns,
      ))

    out += '<tr class="{row_classes}">'.format(
      row_classes="" if row_classes_fn is None else row_classes_fn(row)
    )

    for column, base_value in zip(columns, row):
      cell_classes = set([
        # compact rows
        "py-1",
        "px-2",
      ])
      if column.numeric_data:
        cell_classes.update(['text-right', 'text-monospace'])

      if callable(column.transform_fn):
        display_value = column.transform_fn(base_value)
      elif column.numeric_data:
        # Basic thousands separators for untransformed numeric data
        display_value = '{:,}'.format(base_value)
      else:
        try:
          display_value = unicode(base_value)
        except:
          display_value = base_value # already unicode in py3

      out += '<td class="{cell_classes}">{value}</td>'.format(
        cell_classes=" ".join(cell_classes),
        value = display_value,
      )
    out += '</tr>\n'
  out += '</table>\n'
  out += '</div>\n'
  return out

def category_table(category, rows, row_classes_fn=None, brief=False):
  """
  Display a HTML table for a given category. We just need to add the
  Rank & Player/Captain columns.
  """
  cols = [col for col in category.columns if (not brief or col.include_in_compact_display)]
  # logging.info(
  #   "category_table %s %s brief:%s base_cols:%s row0:%s",
  #   category.type, category.name, brief, len(cols),
  #   rows[0] if len(rows) else "<empty>")
  if category.type == 'individual':
    cols.insert(0, PseudoCol(
      "Player",
      False,
      lambda player: crawl_utils.linked_text(key=player, link_fn=crawl_utils.player_link),
    ))
  else:
    def _pretty_clan_name(data):
      info = json.loads(data)
      name = info["name"]
      return '<a href="{url}">{name}</a>'.format(
          url=crawl_utils.clan_link(name, info["captain"]), name=name,
      )
    cols.insert(0, PseudoCol("Team", False, _pretty_clan_name))
  cols.insert(0, PseudoCol("#", True, None))

  return _table(
    columns=cols,
    rows=rows,
    row_classes_fn=row_classes_fn,
    brief=brief,
  )

def full_games_table(games, **pars):
  if not pars.get('columns'):
    if 'win' in pars:
      win = pars['win']
    else:
      win = True
    pars['columns'] = win and EXT_WIN_COLUMNS or EXT_COLUMNS
  return games_table(games, **pars)

def ext_games_table(games, win=True, **pars):
  cols = win and EXT_WIN_COLUMNS or EXT_COLUMNS
  pars.setdefault('including', []).append((1, ('player', 'Player')))
  return games_table(games, columns=cols, count=False, **pars)

def combo_highscorers(c):
  hs = query.get_top_combo_highscorers(c)
  return table_text( [ 'Player', 'Combo scores' ],
                     hs, place_column=1, skip=True )

def deepest_xl1_games(c):
  games = query.get_deepest_xl1_games(c)
  return games_table(games, first = 'place', win=False)

def hyperlink_games(games, field):
  hyperlinks = [ crawl_utils.morgue_link(g) for g in games ]
  text = [ '<a href="%s">%s</a>' % (link, g[field])
           for link, g in zip(hyperlinks, games) ]
  return ", ".join(text)

def youngest_rune_finds(c):
  runes = query.youngest_rune_finds(c)
  runes = [list(r) for r in runes]
  for r in runes:
    r[3] = pretty_date(r[3])
  return table_text([ 'Player', 'Rune', 'XL', 'Time' ], runes)

def most_deaths_to_uniques(c):
  rows = query.most_deaths_to_uniques(c)
  for r in rows:
    r.insert(1, len(r[1]))
    r[2] = ", ".join(r[2])
  return table_text([ 'Player', '#', 'Uniques', 'Time'], rows)

def streak_table(streaks, active=False, place=False):
  # Replace the list of streak games with hyperlinks.
  result = []

  nplace = 0
  rplace = 0
  last_value = None
  for s in streaks:
    games = s['games']
    game_text = hyperlink_games(games, 'charabbrev')
    if active and s['is_active']:
      game_text += ", " + (s['next_char'] or "?")
    rplace += 1
    if last_value != s['length']:
      nplace = rplace
      last_value = s['length']
    row = [nplace, s['player'], s['length'], game_text]
    result.append(row)

  return _table([ PseudoCol('#', True, None),
                  PseudoCol('Player', False, lambda player: crawl_utils.linked_text(key=player, link_fn=crawl_utils.player_link)),
                  PseudoCol('Streak Length', True, None),
                  PseudoCol('Games', False, None), ],
                  result, brief=True)

def best_active_streaks(c):
  return streak_table(query.get_top_active_streaks(c), active=True)

def best_streaks(c):
  streaks = query.get_top_streaks(c)
  return streak_table(streaks, place=True)

def fixup_clan_rows(rows):
  rows = [ list(r) for r in rows ]
  for clan in rows:
    clan[0] = linked_text(clan[1], clan_link, clan[0])
  return rows

def best_clans(c):
  clans = fixup_clan_rows(query.get_top_clan_scores(c))
  return table_text( [ 'Clan', 'Captain', 'Points' ],
                     clans, place_column=2, skip=True )

def clan_unique_kills(c):
  ukills = fixup_clan_rows(query.get_top_clan_unique_kills(c))
  return table_text( [ 'Clan', 'Captain', 'Kills', 'Time' ],
                     ukills)

def clan_combo_highscores(c):
  return table_text( [ 'Clan', 'Captain', 'Scores' ],
                     fixup_clan_rows(query.get_top_clan_combos(c)),
                     place_column=2, skip=True )

def make_milestone_string(w, src, make_links=False):
  ago,new = how_old(w[0])
  if ago == None:
    return None
  if make_links:
    plink = crawl_utils.linked_text(w[1], crawl_utils.player_link)
  else:
    plink = w[1]
  if w[5] == None:
    god_phrase = ''
  else:
    god_phrase = ' of %s' % w[5]
  where_nice = (ago, plink) + w[2:5] + (god_phrase, ) + w[6:9] + (pretty_dur(w[9]),src)
  return ("%s ago: %s the %s (L%d %s%s) %s (%s, turn %d, dur %s, %s)<br />" % where_nice)

def whereis(c, *players):
  where_data = []
  for p in players:
    for src in ['cao','cbr2','cdi','cdo', 'cpo', 'cnc','cue','cxc','lld']:
      where = query.whereis_player(c, p, src)
      if not where:
        continue
      mile_string = make_milestone_string(where, src)
      if not mile_string:
        continue
      where_data.append([where[0], mile_string])
  where_data.sort(key=lambda e: e[0], reverse=True)
  where_string = ""
  for w in where_data:
    where_string += w[1]
  return where_string

def whereis_table(c):
  where_data = []
  for w in query.whereis_all_players(c):
    where = w[1]
    if w[0] == 'csz':
      pretty_src = 'cszo'
    elif w[0] == 'cbr':
      pretty_src = 'cbr2'
    else:
      pretty_src = w[0]
    ago,new = how_old(where[0],1)
    if ago == None:
      continue
    if where[5] == None:
      god_phrase = ''
    else:
      god_phrase = ' of %s' % where[5]
    mile_data = [where[1], where[7], where[3], '%s%s' % (where[4], god_phrase), where[2], where[6], '%s ago' % ago, pretty_src.upper()]
    where_data.append([where[7], where[3], where[0], mile_data])
  where_data.sort(key=lambda e: (e[0],e[1],e[2]), reverse=True)

  where_list = []
  for w in where_data:
    where_list.append(w[3])
    if where_list[-1][1] == 0:
      where_list[-1][1] = ''
  return _table([
      PseudoCol("Player", False,
      lambda player: crawl_utils.linked_text(key=player,
          link_fn=crawl_utils.player_link)),
      PseudoCol("Runes", False, None),
      PseudoCol('Level', False, None),
      PseudoCol('Character', False, None),
      PseudoCol('Title', False, None),
      PseudoCol('Location', False, None),
      PseudoCol('Time', False, None),
      PseudoCol('Server', False, None) ], where_list)

def _scored_win_text(g, text):
  if g['killertype'] == 'winning':
    text += '*'
  return text

def player_combo_scores(c, player):
  games = query.get_combo_scores(c, player=player)
  games = [ [ crawl_utils.linked_text(g, crawl_utils.morgue_link,
                                      _scored_win_text(g, g['charabbrev'])),
              g['score'] ]
            for g in games ]
  return games

def player_species_scores(c, player):
  games = query.game_hs_species(c, player)

  games = [
    [ crawl_utils.linked_text(g, crawl_utils.morgue_link,
                              _scored_win_text(g, g['charabbrev'][:2])),
      g['score'] ]
    for g in games ]
  return games

def player_class_scores(c, player):
  games = query.game_hs_classes(c, player)
  games = [
    [ crawl_utils.linked_text(g, crawl_utils.morgue_link,
                              _scored_win_text(g, g['charabbrev'][2:])),
      g['score'] ]
    for g in games ]
  return games

def clan_combo_scores(c, captain):
  games = [i[1] for i in query.get_clan_combo_scores(c, captain=captain)]
  games = [ [ crawl_utils.linked_text(g, crawl_utils.morgue_link,
                                      _scored_win_text(g, g['charabbrev'])),
              g['score'] ]
            for g in games ]
  return games

def player_scores_block(c, scores, title):
  asterisk = [ s for s in scores if '*' in s[0] ]
  score_table = (scores
                 and (", ".join([ "%s&nbsp;(%d)" % (s[0], s[1])
                                  for s in scores ]))
                 or "None")
  text = """<h3>%(title)s</h3>
              <div class="inset inline bordered">
                %(score_table)s
              </div>
         """ % {'title': title, 'score_table': score_table}
  if asterisk:
    text += "<p class='fineprint'>* Winning Game</p>"
  return text

def english_join(items, final="and"):
  """Join a list of items with an oxford comma and joining word.

  eg [1,2,3] => "1, 2, and 3".
  """
  # type: (Sequence[str], str) -> str
  if not items:
    return ""
  if len(items) == 1:
    return items[0]
  elif len(items) == 2:
    return "%s %s %s" % (items[0], final, items[1])
  else:
    items[-1] = "%s %s" % (final, items[-1])
    return ", ".join(str(item) for item in items)

def category_column_title(cat):
    if cat.proportional:
        return "%s (max %d)" % (cat.name, cat.max)
    else:
        return cat.name
