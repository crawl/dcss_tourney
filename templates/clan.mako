<%
   import loaddb, query, crawl_utils, html

   c = attributes['cursor']
   captain = attributes['captain']

   cinfo = query.get_clan_info(c, captain)
   stats = query.get_clan_stats(c, captain)

   name = cinfo[0]
   won_games = query.find_clan_games(c, captain,
                                     killertype = 'winning',
                                     sort_max = 'end_time')
   recent_games = query.find_clan_games(c, captain,
                                        sort_max = 'end_time', limit = 20)

   won_html = html.games_table(won_games, columns=html.EXT_WIN_COLUMNS,
                             including=[(1, ('player', 'Player'))],
                             count=False)

   recent_html = html.games_table(recent_games, columns=html.EXT_COLUMNS,
                             including=[(1, ('player', 'Player'))],
                             count=False)
 %>
<html>
  <head>
    <title>${name}</title>
    <link rel="stylesheet" type="text/css" href="../tourney-score.css">
  </head>

  <body class="page_back">
    <div class="page">
      <div class="heading_left">
        <h1>Clan ${name}</h1>
      </div>

      <hr/>

      <div class="content">
        <div class="player_clan">
          <span class="inline_heading">Clan: </span>
          ${html.clan_affiliation(c, captain)}
        </div>

        <div class="player_status">
          <table class="bordered">
            <tr>
              <th>Tourney points total</th>
              <td class="numeric">${stats['points']}</td>
            </tr>

            <tr>
              <th>Games won / played</th>
              <td>${stats['won']} / ${stats['played']}
                (${stats['win_perc']})</td>
            </tr>
          </table>
        </div>

        <div class="game_table">
          <h3>Games won</h3>
          ${won_html}
        </div>

        <div class="game_table">
          <h3>Recent Games</h3>
          ${recent_html}
        </div>
      </div>
    </div> <!-- page -->

    ${html.update_time()}
  </body>
</html>
