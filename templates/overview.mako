<html>
  <head>
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

      <%doc>
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
      </%doc>

    </table>
  </body>
</html>
