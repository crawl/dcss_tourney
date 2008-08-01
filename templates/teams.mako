<%
   import loaddb, query
   c = attributes['cursor']
%>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <title>Teams</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css"/>
  </head>
  <body>
    <table class="overview">
    <thead>
      <tr>
        <th>Teamname</th>
        <th>Captain</th>
        <th>Members</th>
      </tr>
    <thead>
    <tbody>
      <%
        players = query.query_rows(c, '''SELECT teams.owner, teams.name, players.name FROM players, teams WHERE players.team_captain != players.name AND players.team_captain = teams.owner''')
        teamnames = {}
        teammembers = {}
        for row in players:
          teamnames[row[0]] = row[1]
          teammembers.setdefault(row[0], []).append(row[2])
      %>
      % for captain in teamnames.iterkeys():
      <tr>
        <td>${teamnames[captain]}</td>
        <td>${captain}</td>
        <td>${teammembers[captain]}</td>
      </tr>
      % endfor
    </tbody>
    </table>
  </body>
</html>
