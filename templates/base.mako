## Base template for all pages. Use this template by inheriting it, and define
## all the blocks required below.
<%!
  from html import update_time
  from crawl_utils import XXX_TOURNEY_BASE
  from loaddb import T_VERSION

  menu_items = (
    (XXX_TOURNEY_BASE + "/overview.html", "Overview"),
    (XXX_TOURNEY_BASE + "/banners.html", "Banners"),
    (XXX_TOURNEY_BASE + "/all-players.html", "Players"),
    (XXX_TOURNEY_BASE + "/teams.html", "Clans"),
    (XXX_TOURNEY_BASE + "/combo-leaders.html", "Combo Standings"),
    (XXX_TOURNEY_BASE + "/combo-scoreboard.html", "Combo Scoreboard"),
    (XXX_TOURNEY_BASE + "/species-backgrounds.html", "Species/Backgrounds/Gods"),
    (XXX_TOURNEY_BASE + "/wins-and-kills.html", "Wins & Kills"),
    (XXX_TOURNEY_BASE + "/current-games.html", "Current Games"),
    (XXX_TOURNEY_BASE + "", "Rules"),
  )
%>
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

    <title>
      <%block name="title"/>
    </title>

    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
    <link rel="stylesheet" href="${XXX_TOURNEY_BASE}/style.css">
  </head>

  <body class="text-light">
    <nav class="navbar navbar-dark navbar-expand-lg" style="background-color: #1a1a1a;">
      <a class="navbar-brand overflow-hidden" href="${XXX_TOURNEY_BASE}">Dungeon Crawl Stone Soup ${T_VERSION} Tournament</a>
    </nav>
    ## The background of this bar is deliberately different
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: black;">
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav mr-auto">
          % for menu_item in menu_items:
          <%
            # Every page needs to set active_menu_item in a <%! %> module block.
            # If the value matches the name of a menu item, it will be shown as
            # the active nav item. If there's no applicable menu item, use None.
            active_class = "active" if self.attr.active_menu_item == menu_item[1] else ""
          %>
          <li class="nav-item">
            <a class="nav-link ${active_class}" href=${menu_item[0]}>${menu_item[1]}</a>
          </li>
          % endfor
        </ul>
      </div>
    </nav>

    <div class="container">
      <%block name="main"/>
      ${update_time()}
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
  </body>
</html>
