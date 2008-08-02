<%
   import loaddb, query, crawl_utils, html

   c = attributes['cursor']
   player = attributes['player']

   stats = query.get_player_stats(c, player)

   won_games = query.find_games(c, player = player, killertype = 'winning',
                                sort_max = 'end_time')
   recent_games = query.find_games(c, player = player, sort_max = 'end_time',
                                   limit = 15)

   streak_games = query.get_player_best_streak_games(c, player)

   audit = query.audit_trail_player_points(c, player)

   def point_breakdown():
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

          <div class="game_table">
            <h3>Games won (reverse chronological)</h3>
            ${html.full_games_table(won_games, count=False)}
          </div>

          % if streak_games:
          <div class="game_table">
            <h3>Longest streak of wins</h3>
            ${html.full_games_table(streak_games)}
          </div>
          % endif

          <div class="game_table">
            <h3>Recent Games</h3>
            ${html.full_games_table(recent_games, count=False, win=False)}
          </div>

          <hr/>
          <div class="audit_table">
            <h3>Points Breakdown</h3>
            <table class="grouping">
              <tr>
                <td>
                  <table class="bordered">
                    <tr>
                      <th>N</th> <th>Points</th> <th>Source</th>
                    </tr>
                    ${point_breakdown()}
                  </table>
                </td>
                <td class="legend">
                  <table class="bordered">
                    <tr>
                      <th>Legend</th>
                    </tr>
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
