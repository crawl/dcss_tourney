<%
   import loaddb, query, crawl_utils, htmlgen
   from outline import compute_stepdown

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

   won_html = htmlgen.ext_games_table(won_games)
   recent_html = htmlgen.ext_games_table(recent_games, win=False)

   clan_player_points = query.audit_adjusted_clan_player_points(c, captain)
   clan_points = query.audit_clan_points(c, captain)
   clan_category_points = query.audit_clan_category_points(c, captain)
   clan_stepdown_points = query.audit_clan_stepdown_points(c, captain)

   clan_players = cinfo[1]
   clan_whereis = htmlgen.whereis(c, *clan_players)

   won_gods = [x[0] for x in query.clan_god_wins(c, captain)]
   won_gods.sort()

   uniq_slain = query.clan_uniques_killed(c, captain)
   uniq_unslain = query.uniques_unkilled(uniq_slain)

   combo_highscores = htmlgen.clan_combo_scores(c, captain)
   asterisk = """<p class='fineprint'>* Winning Game</p>"""

   def player_point_breakdown():
     text = ''
     total = 0
     for name, score in clan_player_points:
       text += '''<tr class="point_perm">
                    <td>%s</td>
                    <td class="numeric">%s</td>
                  </tr>''' % (name, score)
       total += score
     text += '''<tr><th>Total</th><th class="numeric">%s</th></tr>''' % total
     return text

   def clan_point_breakdown(c_points, with_stepdown=False):
     text = ''
     total = 0
     for source, points in c_points:
       text += '''<tr class="point_perm">
                    <td>%s</td>
                    <td class="numeric">%s</td>
                  </tr>''' % (source, points)
       total += points
     text += '''<tr><th>Total</th><th class="numeric">%s</th></tr>''' % total
     if with_stepdown:
       text += '</tr>\n'
       text += '''<tr><th>Adjusted Total</th>
                    <th class="numeric">%d</th>''' % compute_stepdown(total)
     return text

   blank_row = '''<tr>
                    <td class="blank">&nbsp;</td>
                    <td class="blank">&nbsp;</td>
                  </tr>'''


   grand_total = sum( [ x[1] for x in clan_player_points ] +
                      [ x[1] for x in clan_points ] )

   banners = htmlgen.banner_images(query.get_clan_banners(c, captain))
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
        ${htmlgen.banner_div(banners)}
      </div>

      <div class="page_content content-bannered">
        <div class="heading_left">
          <h1>${name.replace('_', ' ')}</h1>
        </div>

        <hr>

        <div class="content">
          <div class="player_clan">
            <span class="inline_heading">Clan: </span>
            ${htmlgen.clan_affiliation(c, captain)}
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
            ${recent_html}
          </div>

          % if uniq_slain:
          <hr>
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
          % endif

          % if combo_highscores:
            <hr>
            <div>
              ${htmlgen.player_scores_block(c, combo_highscores,
                                         'Combo Highscores')}
            </div>
          % endif
          <hr>

          <div class="audit_table">
            <h3>Score Breakdown</h3>
            <table class="grouping">
              <tr>
                <td>
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
                    ${clan_point_breakdown(clan_points)}
                    %endif
                    %if clan_points and clan_player_points:
                      ${blank_row}
                      <tr>
                        <th>Grand Total</th>
                        <th class="numeric">${grand_total}</th>
                      </tr>
                    %endif
                  </table>
                </td>
                %if len(clan_stepdown_points) > 0:
                <td></td><td></td>
                <td>
                  <h4>Combo/God Points Breakdown</h4>
                  <table class="bordered">
                    %if clan_points:
                    <tr>
                      <th>Source</th> <th>Points</th>
                    </tr>
                    ${clan_point_breakdown(clan_stepdown_points, True)}
                    %endif
                  </table>
                </td>
                %endif
              </tr>
            </table>
          </div>
        </div>
      </div>
    </div> <!-- page -->

    ${htmlgen.update_time()}
  </body>
</html>
