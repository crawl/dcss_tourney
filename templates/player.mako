<%
   import loaddb, query, crawl_utils, html

   c = attributes['cursor']
   player = attributes['player']

   stats = query.get_player_stats(c, player)

   won_games = query.find_games(c, player = player, killertype = 'winning',
                                sort_max = 'end_time', limit=None)
   recent_games = query.find_games(c, player = player, sort_max = 'end_time',
                                   limit = 15)

   streak_games = query.get_player_best_streak_games(c, player)

   won_gods = query.get_player_won_gods(c)

   audit = query.audit_trail_player_points(c, player)
   audit_team = query.audit_trail_player_team_points(c, player)

   whereis = html.whereis(False, player)

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

 %>
<html>
  <head>
    <title>${player}</title>
    <link rel="stylesheet" type="text/css" href="../tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>
      <div class="page_content">
        <div class="heading_left">
          <h1>Player information for ${player}</h1>
        </div>

        <hr/>

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
          <div class="game_table">
            <h3>Ongoing Game (cao)</h3>
            <div class="fineprint">
              On-going information is from the crawl.akrasiac.org server only,
              and may be inaccurate if the player is active on other
              servers.
            </div>
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

          % if won_gods:
          <div id="won-gods">
            <h3>Winning Gods:</h3>
            <p>
              ${", ".join(won_gods)}
            </p>
            <p class="fineprint">
              All gods that ${player} has won games with, without changing
              gods (or renouncing and rejoining gods) during the game.
            </p>

            <h3>Remaining Gods:</h3>
            <p>
              ${", ".join(query.find_remaining_gods(won_gods))}
            </p>
          </div>

          <div class="game_table">
            <h3>Recent Games</h3>
            ${html.full_games_table(recent_games, count=False, win=False)}
          </div>

          <hr/>

          % if uniq_slain:
          <div>
            <table class="bordered">
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
          <hr/>
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
