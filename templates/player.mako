<%
   import loaddb, query, crawl_utils, html

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

   portals_entered,portals_unentered = query.get_portals_entered(c, player)

   audit = query.audit_trail_player_points(c, player)
   audit_team = query.audit_trail_player_team_points(c, player)

   whereis = html.whereis(c, player)

   def point_breakdown(audit):
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
     return text

   uniq_slain = query.player_uniques_killed(c, player)
   uniq_unslain = query.uniques_unkilled(uniq_slain)
   banners = html.banner_images(query.get_player_banners(c, player))

   combo_highscores = html.player_combo_scores(c, player)
   species_highscores = html.player_species_scores(c, player)
   class_highscores = html.player_class_scores(c, player)
   asterisk = """<p class='fineprint'>* Winning Game</p>"""
 %>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>${player}</title>
    <link rel="stylesheet" type="text/css" href="../tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page bannered">
      <%include file="toplink.mako"/>

      <div id="player-banners">
        ${html.banner_div(banners)}
      </div>

      <div class="page_content content-bannered">
        <div class="heading_left">
          <h1>Player information for ${player}</h1>
        </div>

        <hr>

        <div class="content">
          <div class="player_clan">
            <span class="inline_heading">Clan: </span>
            ${html.clan_affiliation(c, player)}
          </div>

          <div class="player_status">
            <table class="bordered">
              <tr>
                <th>Tourney points total</th>
                <td class="numeric">${stats['points']}</td>
              </tr>

              <tr>
                <th>Tourney team points</th>
                <td class="numeric">${stats['team_points']}</td>
              </tr>
              <tr>
                <th>Games won / played</th>
                <td>${stats['won']} / ${stats['played']}
                  (${stats['win_perc']})</td>
              </tr>
            </table>
          </div>

          %if whereis:
            <h3>Ongoing Game</h3>
            <div>
              ${whereis}
            </div>
          %endif

          <div class="game_table">
            <h3>Wins</h3>
            ${html.full_games_table(won_games, count=False)}
          </div>

          % if streak_games:
          <div class="game_table">
            <h3>Longest streak of wins</h3>
            ${html.full_games_table(streak_games)}
          </div>
          % endif

          %if best_games:
          <div class="game_table">
            <h3>Best Games</h3>
            ${html.full_games_table(best_games, win=False)}
          </div>
          %endif

          % if won_gods:
          <div id="won-gods">
            <h3>Winning Gods:</h3>
            <div class="bordered inline">
              ${", ".join(won_gods)}
            </div>

            <p class="fineprint">
              All gods that ${player} has won games with, without changing
              gods (or renouncing and rejoining gods) during the game.
            </p>

            <h3>Remaining Gods:</h3>
            <div class="bordered inline">
              ${", ".join(query.find_remaining_gods(won_gods)) or 'None'}
            </div>
          </div>
          % endif

          <div class="game_table">
            <h3>Recent Games</h3>
            ${html.full_games_table(recent_games, count=False, win=False)}
          </div>

          <hr>

          % if uniq_slain:
          <div>
            <table class="bordered">
              <colgroup>
                 <col width="10%">
                 <col width="85%">
              </colgroup>
              <tr>
                <th>Uniques Slain</th>
                <td>${", ".join(uniq_slain)}</td>
              </tr>
              % if len(uniq_slain) > len(uniq_unslain):
                <tr>
                  <th>Uniques Left</th>
                  % if uniq_unslain:
                  <td>${", ".join(uniq_unslain)}</td>
                  % else:
                  <td>None</td>
                  % endif
                </tr>
              % endif
            </table>
          </div>
          <hr>
          % endif

          % if portals_entered and portals_unentered:
          <div>
            <table class="bordered">
              <colgroup>
                 <col width="10%">
                 <col width="85%">
              </colgroup>
              <tr>
                <th>Portals Entered</th>
                <td>${", ".join(portals_entered)}</td>
              </tr>
              <tr>
                <th>Portals Not Yet Entered</th>
                <td>${", ".join(portals_unentered)}</td>
              </tr>
            </table>
          </div>
          <hr>
          % endif   

          % if combo_highscores or species_highscores or class_highscores:
            <div>
              ${html.player_scores_block(c, combo_highscores,
                                         'Combo Highscores')}
              ${html.player_scores_block(c, species_highscores,
                                         'Species Highscores')}
              ${html.player_scores_block(c, class_highscores,
                                         'Class Highscores')}
            </div>
            <hr>
          % endif

          <div class="audit_table">
            <h3>Score Breakdown</h3>
            <table class="grouping">
              <tr>
                <td>
                  <h4>Player points</h4>
                  <table class="bordered">
                    <tr>
                      <th>N</th> <th>Points</th> <th>Source</th>
                    </tr>
                    ${point_breakdown(audit)}
                  </table>
                </td>

                <td>
                  <h4>Team points</h4>
                  <table class="bordered">
                    <tr>
                      <th>N</th> <th>Points</th> <th>Source</th>
                    </tr>
                    ${point_breakdown(audit_team)}
                  </table>
                </td>

                <td class="legend">
                  <h4>Legend</h4>
                  <table class="bordered">
                    <tr class="point_perm">
                      <td>Permanent points</td>
                    </tr>
                    <tr class="point_temp">
                      <td>Provisional points</td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </div>
        </div>
      </div> <!-- content -->
    </div> <!-- page -->

    ${html.update_time()}
  </body>
</html>
