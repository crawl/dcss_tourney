<%
   import loaddb, query

   c = attributes['cursor']
%>

<html>
  <head>
    <link rel="stylesheet" type="text/css" href="tourney-score.css"/>
  </head>
  <body>
    <table class="overview">
      <tr>
        <td class="tdover">
          <%include file="overall-scores.mako"/>
        </td>
      </tr>
    </table>
  </body>
</html>
