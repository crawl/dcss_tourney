<%
   import loaddb, query, crawl_utils, html

   c = attributes['cursor']
   player = attributes['player']

   stats = query.get_player_stats(c, player)

   won_games = query.find_games(c, player = player, killertype = 'winning',
                                sort_max = 'end_time')
   recent_games = query.find_games(c, player = player, sort_max = 'end_time',
                                   limit = 15)
 %>
<html>
  <head>
    <title>${player}</title>
    <link rel="stylesheet" type="text/css" href="../tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      
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

        <div class="game_table">
          <h3>Recent Games</h3>
          ${html.full_games_table(recent_games, count=False, win=False)}
        </div>
      </div>

    </div> <!-- page -->
  </body>
</html>
