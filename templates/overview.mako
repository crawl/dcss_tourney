<html>
  <head>
    <title>Crawl Tournament Leaderboard 2008</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css"/>
  </head>
  <body>
    <table class="overview">
      <tr>
        <td class="tdover">
          <h3>Leading Players</h3>
          <%include file="overall-scores.mako"/>
        </td>

        <td class="tdover">
          <h3>First Victory</h3>
          <%include file="first-victory.mako"/>
        </td>
      </tr>

      <tr>
        <td class="tdover">
          <h3>Fastest win (turn count)</h3>
          <%include file="fastest-turn.mako"/>
        </td>

        <td class="tdover">
          <h3>Fastest Win (real time)</h3>
          <%include file="fastest-time.mako"/>
        </td>
      </tr>

      <tr>
        <td class="tdover">
          <h3>First all-rune wins</h3>
          <%include file="first-allrune.mako"/>
        </td>
      </tr>

      
    </table>
  </body>
</html>
