<%
   import loaddb, query, crawl_utils, html

   c = attributes['cursor']
   captain = attributes['captain']

   cinfo = query.get_clan_info(c, captain)
   stats = query.get_clan_stats(c, captain)

   name = cinfo[0]
   won_games = query.find_clan_games(c, captain,
                                     killertype = 'winning',
                                     sort_max = 'end_time',
                                     limit=None)
   recent_games = query.find_clan_games(c, captain,
                                        sort_max = 'end_time', limit = 20)

   won_html = html.ext_games_table(won_games)
   recent_html = html.ext_games_table(recent_games, win=False)

   clan_player_points = query.audit_clan_player_points(c, captain)
   clan_points = query.audit_clan_points(c, captain)

   clan_players = cinfo[1]
   clan_whereis = html.whereis(c, *clan_players)

   def player_point_breakdown():
     text = ''
     total = 0
     for name, score in clan_player_points:
       text += '''<tr class="point_temp">
                    <td>%s</td>
                    <td class="numeric">%s</td>
                  </tr>''' % (name, score)
       total += score
     text += '''<tr><th>Total</th><th class="numeric">%s</th></tr>''' % total
     return text

   def clan_point_breakdown():
     text = ''
     total = 0
     for source, points in clan_points:
       text += '''<tr class="point_temp">
                    <td>%s</td>
                    <td class="numeric">%s</td>
                  </tr>''' % (source, points)
       total += points
     text += '''<tr><th>Total</th><th class="numeric">%s</th></tr>''' % total
     return text

   blank_row = '''<tr>
                    <td class="blank">&nbsp;</td>
                    <td class="blank">&nbsp;</td>
                  </tr>'''


   grand_total = sum( [ x[1] for x in clan_player_points ] +
                      [ x[1] for x in clan_points ] )

   banners = html.banner_images(query.get_clan_banners(c, captain))
 %>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>${name}</title>
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
          <h1>${name.replace('_', ' ')}</h1>
        </div>

        <hr>

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

          %if clan_whereis:
            <h3>Ongoing Games</h3>
            <div>
	      ${clan_whereis}
            </div>
          %endif

          <div class="game_table">
            <h3>Wins</h3>
            ${won_html}
          </div>

          <div class="game_table">
            <h3>Recent Games</h3>
            ${recent_html}
          </div>

          <hr>

          <div class="audit_table">
            <h3>Score Breakdown</h3>
            <table class="bordered">
              %if clan_player_points:
              <tr>
                <th>Player</th> <th>Points</th>
              </tr>
              ${player_point_breakdown()}
                %if clan_points:
                  ${blank_row}
                %endif
              %endif
              %if clan_points:
              <tr>
                <th>Source</th> <th>Points</th>
              </tr>
              ${clan_point_breakdown()}
              %endif
              %if clan_points and clan_player_points:
                ${blank_row}
                <tr>
                  <th>Grand Total</th>
                  <th class="numeric">${grand_total}</th>
                </tr>
              %endif
            </table>
          </div>
        </div>
      </div>
    </div> <!-- page -->

    ${html.update_time()}
  </body>
</html>
