import query

def games_table(columns, games, cls=None, count=True):
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
      val = game.get(c[0]) or ''
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
