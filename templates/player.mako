<%
   import loaddb, query, crawl_utils, html
   from outline import compute_stepdown

   # NEW BOOTSTRAP DATA
   MAX_POINTS = 10000
   total_number_of_players = 1325
   overall_rank = 70
   categories = [
     {
       'name': 'The Shining One',
       'desc': 'The Shining One values perserverence and courage in the face of adversity. In this category, TSO will award players 10,000 points if they win two distinct character combos, 5,000 points for winning their first combo, and 0 otherwise.',
       'player_rank': 0,
       'rank_details': 'Won combos: <a href="http://example.com/morgue.txt">MiFi</a>'
     },
     {
       'name': 'Cheibriados',
       'desc': 'Cheibriados believes in being slow and steady, and will recognize players who are careful enough to excel consistently. This category ranks players by their adjusted win percentage, calculated as the number of wins divided by the number of games played plus 1.',
       'player_rank': 1,
       'rank_details': 'Adjusted win percentage: 32.14% (9 wins in 27 games)'
     },
     {
       'name': 'Jiyva',
       'desc': u'Jiyva is ranking players by their streak length. Jiyva favours the flexibility of a gelatinous body—the length of a streak is defined as the number of distinct species or backgrounds won consecutively (whichever is smaller). Every game in a streak must be the first game you start after winning the previous game in the streak. This will always be the case if you play all your games on one server.',
       'player_rank': 2,
       'rank_details': 'No wins yet.',
     },
     {
       'name': 'Nemelex Xobeh',
       'desc': u'''Nemelex Xobeh wants to see players struggle against randomness and will rank players who perservere with one of several combos randomly chosen and announced throughout the tournament. The first 8 players to win a given Nemelex' choice combo earn a point in this category and Nemelex will rank players by their score in this category.''',
       'player_rank': 10000,
       'rank_details': 'Won combos: <a href="http://example.com/morgue.txt">MiFi</a>, <a href="http://example.com/morgue.txt">FeWz</a>, <a href="http://example.com/morgue.txt">BaFE</a>, <a href="http://example.com/morgue.txt">NaEE</a>, <a href="http://example.com/morgue.txt">GnSu</a>, <a href="http://example.com/morgue.txt">DrWn</a>, <a href="http://example.com/morgue.txt">HaCj</a>, <a href="http://example.com/morgue.txt">KoAs</a>'
     }
   ]
   def css_slug(name):
    return name.lower().replace(' ', '-')

   def rank_ordinal(num):
    if num == 0:
      return u'∞'
    remainder = num % 10
    suffix = 'th'
    if remainder == 1:
      suffix = 'st'
    elif remainder == 2:
      suffix = 'nd'
    elif remainder == 3:
      suffix = 'rd'
    if (num % 100) in (11, 12, 13):
      suffix = 'th'
    return '%s%s' % (num, suffix)

   def points_for_rank(rank_num):
    if rank_num == 0:
      return "-"
    return str(int(round(MAX_POINTS / rank_num, 0)))

   def rank_description(rank_num):
    if rank_num == 0:
      return u"0 points<br><small>(rank: ∞)</small>"
    else:
      points = points_for_rank(rank_num)
      ordinal = rank_ordinal(rank_num)
      return "{points} point{s}<br><small>(rank: {ordinal})</small>".format(
        points=points,
        s="s" if points != '1' else "",
        ordinal=ordinal,
      )

   # END NEW BOOTSTRAP DATA

   c = attributes['cursor']
   player = attributes['player']

   stats = query.get_player_stats(c, player)

   won_games = query.find_games(c, player = player, killertype = 'winning',
                                sort_max = 'end_time', limit=None)
   best_games = []

   if len(won_games) < 5:
     best_games = query.find_games(c, player = player,
                                   sort_max = 'score',
                                   limit = 10)
     if len(best_games) < len(won_games):
       best_games = []

   recent_games = query.find_games(c, player = player, sort_max = 'end_time',
                                   limit = 9)

   streak_games = query.get_player_best_streak_games(c, player)

   won_gods = [x or 'No God' for x in query.get_player_won_gods(c, player)]

   audit = query.audit_trail_player_points(c, player)
   audit_team = query.audit_trail_player_team_points(c, player)
   audit_category = query.audit_trail_player_category_points(c, player)
   audit_stepdown = query.audit_trail_player_stepdown_points(c, player)
   whereis = html.whereis(c, player)

   def point_breakdown(audit, with_stepdown=False):
     if not audit:
       return '<tr><td colspan="3">No points</td></tr>'
     text = ''
     total = 0
     n = 0
     for entry in audit:
       cls = entry[0] and 'point_temp' or 'point_perm'
       text += '<tr class="%s">' % cls
       text += '''<td class="numeric">%s</td>
                  <td class="numeric">%s</td>
                  <td>%s</td>''' % \
               (entry[3], entry[2], entry[1])
       text += '</tr>\n'
       n += entry[3]
       total += entry[2]
     text += '''<tr><th class="numeric">%d</th>
                    <th class="numeric">%d</th>
                    <th>Total</th>''' % (n, total)
     if with_stepdown:
       text += '</tr>\n'
       text += '''<tr><th class="numeric"></th>
                    <th class="numeric">%d</th>
                    <th>Adjusted Total</th>''' % compute_stepdown(total)
     return text

   uniq_slain = query.player_uniques_killed(c, player)
   uniq_unslain = query.uniques_unkilled(uniq_slain)
   banners = html.banner_images(query.get_player_banners(c, player))

   combo_highscores = html.player_combo_scores(c, player)
   species_highscores = html.player_species_scores(c, player)
   class_highscores = html.player_class_scores(c, player)
   asterisk = """<p class='fineprint'>* Winning Game</p>"""
 %>
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>${player}</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
    <link rel="stylesheet" href="../style.css"
  </head>

  <body>
    <%include file="toplink-bootstrap.mako"/>

    <div class="container">
      <div class="row">
        <h1>
          ${player}<br>
          <small class="text-muted">Overall rank: ${overall_rank} <small>of ${total_number_of_players}</small></small>
        </h1>
      </div>

      <div class="row">
        <h2>Categories</h2>
      </div>
      % for category in categories:
      <%
        name = category['name']
        css_class = "category-%s" % css_slug(name)
        rank_desc = rank_description(category['player_rank'])
      %>
      <div class="row">
        <div class="jumbotron jumbotron-fluid category ${css_class} text-light p-3">
          <h2 class="text-outline-black-1">${name}</h2>
          <div class="row">
            <div class="col col-sm-4">
              <h3 class="text-outline-black-1">${rank_desc}</h3>
            </div>
            <div class="col-sm">
              <p>
                <i>${category['desc']}</i>
              </p>
              <p class="lead">
                ${category['rank_details']}
              </p>
            </div>
          </div>
        </div>
      </div>
      % endfor

    </div> <!-- container -->

    ${html.update_time()}

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
  </body>
</html>
