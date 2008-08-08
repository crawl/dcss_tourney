<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<%
   import crawl_utils, loaddb, query, html
   c = attributes['cursor']
%>
<html>
  <head>
    <title>Teams</title>
    <link rel="stylesheet" type="text/css" href="tourney-score.css"/>
  </head>
  <body class="page_back">
    <div class="page">
      <%include file="toplink.mako"/>
      <div class="page_content">
        <%
           teams = \
              query.query_rows(c,
                               '''SELECT total_score, name, owner
                                  FROM teams
                                  ORDER BY total_score DESC, name''')
           teams = [ list(x) for x in teams ]

           for team in teams:
             captain = team.pop()
             team[1] = html.linked_text(captain, crawl_utils.clan_link,
                                        team[1])
             team.append( html.clan_affiliation(c, captain, False) )

           table = html.table_text( [ 'Score', 'Team', 'Players' ],
                                    teams, cls='bordered_centered' )
        %>

        <div class="content_centered">
          <div class="centerable">
            <h2>Teams</h2>
            ${table}
          </div>
        </div>
      </div>
    </div>
    ${html.update_time()}
  </body>
</html>
