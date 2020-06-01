<%inherit file="base.mako"/>

## Run on template load (no render context)
<%!
  from crawl_utils import XXX_TOURNEY_BASE
  import html
  import scoring_data
  import query

  # Set active top level menu item
  active_menu_item = 'Players'

  def rank_ordinal(num):
    if num == 0:
      return u'∞'
    remainder = num % 10
    suffix = 'th'
    if remainder == 1:
      suffix = 'st'
    elif remainder == 2:
      suffix = 'nd'
    elif remainder == 3:
      suffix = 'rd'
    if (num % 100) in (11, 12, 13):
      suffix = 'th'
    return '%s<sup>%s</sup>' % (num, suffix)

  def points_for_rank(rank_num):
    if not rank_num:
      return "-"
    return str(int(round(scoring_data.MAX_CATEGORY_SCORE / rank_num, 0)))

  def pretty_points(points):
    return '{:,}'.format(int(points))

  def rank_description(rank_num):
    if rank_num is None:
      return u"0 points <small>(rank: ∞)</small>"
    else:
      points = points_for_rank(rank_num)
      ordinal = rank_ordinal(rank_num)
      return u"{points} point{s} <small>(rank: {ordinal})</small>".format(
        points=pretty_points(points),
        s="s" if points != '1' else "",
        ordinal=ordinal,
      )
%>

## Runs on render. Variables set in here are not accessible to <%blocks>. To
## make data available, write it to a key in the empty dict 'attributes', which
## was passed in at template render time.
## <%
## %>

## The rest of the template is blocks or body (an implicit block called body).
## Access any top level variables passed in as render args, including the dict
## 'attributes' mentioned in the <% %> section comments above.
<%block name="title">
  ${player}
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h1>
        ${player}<br>
        <small class="text-muted">
            Overall rank:
            <a href="${XXX_TOURNEY_BASE}/all-players-ranks.html">
              ${overall_rank}
              <small>
                of ${total_number_of_players}
              </small>
            </a>
        </small>
      </h1>
      % if clan_name is not None:
      <p>
        Clan: <a href="clans/${html.slugify(clan_name)}.html">${clan_name}</a>. Members: ${html.english_join(clan_members)}.
      </p>
      % endif
    </div>
  </div>

  <hr>

  <%
    whereis = html.whereis(cursor, player)
  %>
  % if len(whereis) > 0:
  <div class="row">
    <div class="col">
      <h2>Ongoing Games</h2>
      <p>${whereis}</p>
    </div>
  </div> 
  <hr>
  % endif

  <div class="row">
    <div class="col">
      <ul class="nav nav-tabs mb-2" role="tablist">
        <li class="nav-item" role="presentation">
	  <a class="nav-link active" id="games-tab" data-toggle="tab"
	  href="#games" role="tab" aria-controls="games"
	  aria-selected="true">Games</a>
	</li>
        <li class="nav-item" role="presentation">
          <a class="nav-link" id="individual-categories-tab"
	  data-toggle="tab" href="#individual-categories" role="tab"
	  aria-controls="individual-categories" aria-selected="false">Individual Categories</a>
        </li>
        <li class="nav-item" role="presentation">
          <a class="nav-link" id="banners-tab" data-toggle="tab" href="#banners" role="tab" aria-controls="banners" aria-selected="false">Banners</a>
        </li>
      </ul>
      <div class="tab-content">
        <div class="tab-pane show active" id="games" role="tabpanel"
	aria-labelledby="games-tab">
	  <%include file="player-games.mako" args="cursor=cursor,
	  player=player"/>
	</div>
        <div class="tab-pane" id="individual-categories" role="tabpanel" aria-labelledby="individual-categories-tab">
          <%include file="player-individual-categories.mako" args="points_for_rank=points_for_rank"/>
        </div>
        <div class="tab-pane" id="banners" role="tabpanel" aria-labelledby="banners-tab">
          <%include file="player-banners.mako"/>
        </div>
      </div>
    </div>
  </div>
</%block>
