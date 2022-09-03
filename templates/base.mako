## Base template for all pages. Use this template by inheriting it, and define
## all the blocks required below.
<%!
  import tourney_html as html
  from crawl_utils import XXX_TOURNEY_BASE, XXX_IMAGE_BASE
  from loaddb import T_VERSION
  import scoring_data

  individual_cat_menu = []
  for c in scoring_data.INDIVIDUAL_CATEGORIES:
    link = scoring_data.individual_category_link(c)
    if link:
      individual_cat_menu.append((link, c.name))

  clan_cat_menu = []
  for c in scoring_data.CLAN_CATEGORIES:
    link = scoring_data.clan_category_link(c)
    if link:
      clan_cat_menu.append((link, c.name))

  menu_items = (
    (XXX_TOURNEY_BASE + "/overview.html", "Home"),
    (XXX_TOURNEY_BASE + "", "Rules"),
    (XXX_TOURNEY_BASE + "/all-players-ranks.html", "Players"),
    (XXX_TOURNEY_BASE + "/teams.html", "Clans"),
    ("#", "Player Categories", individual_cat_menu),
    ("#", "Clan Categories", clan_cat_menu),
    (XXX_TOURNEY_BASE + "/current-games.html", "Ongoing Games"),
    (XXX_TOURNEY_BASE + "/combo-scoreboard.html", "Combo Scoreboard"),
    (XXX_TOURNEY_BASE + "/search.html", "Search"),
  )
%>
<%block name="preprocess"/>
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    ## "This page has a mobile view"
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>
      <%block name="title"/>
    </title>

    ## Bootstrap
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" integrity="sha384-9aIt2nRpC12Uk9gS9baDl411NQApFmC26EwAOH8WgZl5MYYxFfc+NcPb1dKGj7Sk" crossorigin="anonymous">
    ## Datatables
    <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/dataTables.bootstrap4.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/fixedcolumns/3.3.1/css/fixedColumns.bootstrap4.min.css"/>
    ## Our custom styles
    <link rel="stylesheet" href="${XXX_TOURNEY_BASE}/style.css">
  </head>

  <body class="text-light">
    <a class="sr-only sr-only-focusable" href="#content">Skip to main content</a>
    <nav class="navbar navbar-dark navbar-expand-lg">
      <a class="navbar-brand overflow-hidden" href="${XXX_TOURNEY_BASE}">
        <img src="${XXX_IMAGE_BASE}/stone_soup_icon-32x32.png" class="pixel-art mr-1 align-top" width="32" height="32" alt="">
        Dungeon Crawl Stone Soup ${T_VERSION} Tournament
      </a>
    </nav>
    ## The background of this bar is deliberately different
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top">
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
            % if len(menu_item) == 2:
              <li class="nav-item">
                <a class="nav-link ${active_class}" href=${menu_item[0]}>${menu_item[1]}</a>
              </li>
            % else:
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle ${active_class}" data-toggle="dropdown" href="${menu_item[0]}" role="button">${menu_item[1]}</a>
                <ul class="dropdown-menu bg-dark">
                % for subitem in menu_item[2]:
                  <li><a class="dropdown-item" href="${subitem[0]}">${subitem[1]}</a></li>
                % endfor
                </ul>
              </li>
            % endif
          % endfor
        </ul>
      </div>
    </nav>

    <div class="container my-3" id="content">
      <%block name="main"/>
      ${html.update_time()}
    </div>

    ## Bootstrap
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js" integrity="sha384-OgVRvuATP1z7JjHLkuOU7Xw704+h835Lr+6QL9UvYjZE3Ipu6Tp75j7Bh/kR0JKI" crossorigin="anonymous"></script>
    ## moment.js
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.26.0/moment.min.js"></script>
    ## DataTables
    <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script>
    <script src="https://cdn.datatables.net/fixedcolumns/3.3.1/js/dataTables.fixedColumns.min.js"></script>
    ## Our custom code
    <script src="${XXX_TOURNEY_BASE}/script.js"></script>
  </body>
</html>
