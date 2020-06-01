<%inherit file="base.mako"/>

## Run on template load (no render context)
<%!
  import scoring_data
  import html
  from crawl_utils import XXX_IMAGE_BASE, base_link

  active_menu_item = "Rules"
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
  DCSS v${scoring_data.TOURNAMENT_VERSION} Tournament
</%block>

<%block name="main">
  <div class="row">
    <div class="col">
      <h1 id="introduction">
        Dungeon Crawl Stone Soup v${scoring_data.TOURNAMENT_VERSION} Tournament
      </h1>
      <p class="lead">
        Welcome! The tournament starts
        ## TODO: These get updated by momentjs
        <span class="font-weight-bold" id="tournament-start-time">
          ${scoring_data.START_TIME.strftime("at %I:%M%p %A %d %B %Z UTC")}
        </span>
        and runs for 16 days until
        <span class="font-weight-bold" id="tournament-end-time">
          ${scoring_data.END_TIME.strftime("%I:%M%p %A %d %B %Z UTC")}
        </span>.
    </div>
  </div>

  <!-- Contents -->
  <div class="row">
    <div class="col">
      <h2>Contents</h2>
      <ol>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#how-to-play">How To Play</a></li>
        <li><a href="#scoring">Scoring</a>
          <ol>
            <li><a href="#individual-categories">Individual Categories</a></li>
            <li><a href="#clan-categories">Clan Categories</a></li>
            <li><a href="#banners">Banners</a></li>
          </ol>
        </li>
      </ol>
    </div>
  </div>

  <!-- How To Play -->
  <div class="row">
    <div class="col">
      <h2 id="how-to-play">How To Play</h2>
      <p>
        <%
          server_list = html.english_join(['<a href="%s">%s</a>' % (server[1], server[0]) for server in sorted(scoring_data.SERVERS.items())])
        %>
        All games of DCSS v${scoring_data.TOURNAMENT_VERSION} played on official servers (${server_list}) will count for the tournament!
      </p>
      <h3>Playing in a Clan</h3>
      <p>
        If you would like to create a clan, add the following as the first lines in your v${scoring_data.TOURNAMENT_VERSION} rc file:
        <pre class="text-light">
        # TEAMNAME nameofteam
        # TEAMMEMBERS player1 player2 player3 player4 player5
        </pre>
        Clan names can contain letters, numbers, underscores, and hyphens. There can be a maximum of six people (including the captain) in a clan.
      </p>
      <p>
        If you'd like to play in an existing clan, add <code># TEAMCAPTAIN nameofcaptain</code> as the first line of your v${scoring_data.TOURNAMENT_VERSION} rc file.
        <div class="alert alert-dark text-dark" role="alert">
          The captain doesn't need a <code># TEAMCAPTAIN</code> line in their rc file!
        </div>
      </p>
      <p>
        You can create, join, and leave clans for the first seven days of the tournament, until
        ## TODO: This gets updated by momentjs
        <span class="font-weight-bold" id="clan-end-time">
          ${scoring_data.CLAN_CUTOFF_TIME.strftime("%h:%M%p %A %d %B %Z UTC")}
        </span>
        .
      </p>
      <p>
        If you're looking for a clan (or players to fill out your clan), try <a href="https://www.reddit.com/r/DCSStourney/">Reddit's /r/dcsstourney</a>.
    </div>
  </div>

  <!-- Scoring -->
  <div class="row">
    <div class="col">
      <h2 id="scoring">Scoring</h2>
      <p>
        Players are ranked across a number of categories (listed below). Your rank in a category determines how many point you win from it. The points received are: <code>${"{:,}".format(scoring_data.MAX_CATEGORY_SCORE)} / rank in category</code>. Your overall rank is based on the total number of points gained across all categories.
        <div class="alert alert-dark text-dark" role="alert">
          If you place last in a category, you will always receive 0 points.
        </div>
        <div class="alert alert-dark text-dark" role="alert">
          Your ranking for each category may change as the tournament progresses. Therefore the points you receive for each category may change too!
        </div>
      </p>
      <p>
        Clans are scored separately using the same system, except with clan categories instead of individual categories.
      </p>
    </div>
  </div>

  <!-- Individual Categories -->
  <div class="row my-2">
    <div class="col">
      <h2 id="individual-categories">Individual Categories</h2>
    </div>
  </div>
  <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4">
    % for category in scoring_data.INDIVIDUAL_CATEGORIES:
    <div class="col mb-4">
      <div class="card h-100 bg-dark text-light">
        <img
        ## A couple of these images are actually JPEGs. Shhh!
          src="${XXX_IMAGE_BASE}/individual/${html.slugify(category.name)}.png"
          alt=""
          ## mx-auto class + max-width = prevent crazy big images on xs display
          class="card-img-top mx-auto"
          ## for transparent images
          style="background: black; max-width: 300px;"
          loading="lazy"
        >
        <div class="card-body">
          <h3 class="card-title">${category.name}</h3>
          <p class="card-text small">
            ${category.desc}
          </p>
        </div>
        <div class="card-footer">
          % if category.source_table:
          <a href="${base_link(html.slugify(category.name))}.html">
            View full ranking.
          </a>
          % else:
          Full ranking not available.
          % endif
        </div>
      </div>
    </div>
    % endfor
  </div>

  <!-- Clan Categories -->
  <div class="row my-2">
    <div class="col">
      <h2 id="clan-categories">Clan Categories</h2>
    </div>
  </div>
  <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4">
    % for category in scoring_data.CLAN_CATEGORIES:
    <div class="col mb-4">
      <div class="card h-100 bg-dark text-light">
        <img
        ## A couple of these images are actually JPEGs. Shhh!
          src="${XXX_IMAGE_BASE}/clan/${html.slugify(category.name)}.png"
          alt=""
          ## mx-auto class + max-width = prevent crazy big images on xs display
          class="card-img-top mx-auto"
          ## for transparent images
          style="background: black; max-width: 300px;"
          loading="lazy"
        >
        <div class="card-body">
          <h3 class="card-title">${category.name}</h3>
          <p class="card-text small">
            ${category.desc}
          </p>
        </div>
        <div class="card-footer">
          % if category.url:
          <a href="${category.url}">
            View full ranking.
          </a>
          % else:
          Full ranking not available.
          % endif
        </div>
      </div>
    </div>
    % endfor
  </div>

  <!-- Banners -->
  <div class="row">
    <div class="col">
      <h2 id="banners">Banners</h2>
      <p>
        Banners give points in the individual & clan banner categories described
        above. Banner tiers are worth 1, 2, and 4 points for tiers one, two, and
        three respectively.
      </p>
    </div>
  </div>
  <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4">
  % for banner in scoring_data.BANNERS:
  <div class="col mb-4">
    <div class="card h-100 banner bg-dark text-light">
      <img
        src="${XXX_IMAGE_BASE}/altar/${html.slugify(banner.god)}.png"
        alt="${banner.god}"
        class="card-img-top pixel-art px-5 mt-3 mx-auto"
        loading="lazy"
      >
      <div class="card-body">
        <h2 class="card-title">${banner.name}</h2>
        <ul class="list-group list-group-flush">
          % for tier in (0, 1, 2):
          <li class="list-group-item bg-dark px-0 py-1">
            <p class="small mb-0">
              <b>
                Tier ${tier + 1}:
              </b>
              ${banner.tiers[tier]}
            </p>
          </li>
          % endfor
        </ul>
      </div>
    </div>
  </div>
  % endfor
  </div>

  <!-- Credits -->
  <div class="row">
    <div class="col">
      <h2>Credits</h2>
      <p>
        This tournament exists thanks to the work of
        <a href="https://github.com/crawl/dcss_tourney/graphs/contributors">
          many people
        </a>
        , but one person was especially pivotal. <b>ebering</b> designed a new
        scoring system for this tournament, based on broad consultation with
        players and other devs over several months. Then he coded it up (which
        required rewriting almost all of the scoring code) in a matter of weeks.
        Thank you, ebering!
      </p>
    </div>
  </div>

</%block>
