<%
   import loaddb, query, crawl_utils, html
   from outline import compute_stepdown

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
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>${player}</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
  </head>

  <body class="page_back">
    <div class="container">
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
                <th>Rank</th>
                <td>${stats['rank1']} / ${stats['rank2']}</td>
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
            <h3>Ongoing Games</h3>
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
              We say that a game is won using a (non-Gozag, non-Xom) god if the player reaches
              ****** piety with that god without worshipping any
              other god first; this is not necessarily the same god worshipped at the end of the game. A game is won using Gozag or Xom if the player never worships another god. A game is won using 'No God' only if the player
              never worships a god.
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

          </div>

          % if combo_highscores or species_highscores or class_highscores:
            <div>
              ${html.player_scores_block(c, combo_highscores,
                                         'Combo Highscores')}
              ${html.player_scores_block(c, species_highscores,
                                         'Species Highscores')}
              ${html.player_scores_block(c, class_highscores,
                                         'Background Highscores')}
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
                %if len(audit_category)+1 < len(audit):
                <td>
                  <h4>Category Breakdown</h4>
                  <table class="bordered">
                    <tr>
                      <th>N</th> <th>Points</th> <th>Source</th>
                    </tr>
                    ${point_breakdown(audit_category)}
                  </table>

                %if len(audit_stepdown) > 0:
                  <h4>Combo/God Points Breakdown</h4>
                  <table class="bordered">
                    <tr>
                      <th>N</th> <th>Points</th> <th>Source</th>
                    </tr>
                    ${point_breakdown(audit_stepdown, True)}
                  </table>
                %endif

                </td>
                %endif

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

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
  </body>
</html>
