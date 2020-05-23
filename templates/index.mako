<%inherit file="base.mako"/>

## Run on template load (no render context)
<%!
  import scoring_data

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
      <h1>
        Dungeon Crawl Stone Soup v${scoring_data.TOURNAMENT_VERSION} Tournament
      </h1>
    </div>
  </div>

  <div class="row">
    <div class="col">
      <h2>Contents</h2>
      <ul>
        <li><a href="#introduction">Introduction</a></li>
        <li><a href="#individual-categories">Individual Categories</a></li>
        <li><a href="#individual-banners">Individual Banners</a></li>
        <li><a href="#clan-categories">Clan Categories</a></li>
      </ul>
    </div>
  </div>

  <div class="row">
    <div class="col">
      <h2 id="individual-categories">Individual Categories</h2>
      % for category in scoring_data.INDIVIDUAL_CATEGORIES:
      <div class="row">
        <div class="col">
          <p>
            <b>${category.name}:</b> ${category.desc}
          </p>
        </div>
      </div>
      % endfor
    </div>
  </div>

  <div class="row">
    <div class="col">
      <h2 id="individual-banners">Individual Banners</h2>
      % for banner in scoring_data.BANNERS:
      <div class="row">
        <div class="col">
          <p>
            <b>${banner.name} (${banner.god})</b>
          </p>
          <ol>
            % for num, desc in enumerate(banner.tiers):
              <li><b>Tier ${num + 1}:</b> ${desc}</li>
            % endfor
          </ol>
        </div>
      </div>
      % if banner.notes:
      <p><i>${banner.notes}</i></p>
      % endif
      % endfor
    </div>
  </div>

  <div class="row">
    <div class="col">
      <h2 id="clan-categories">Clan Categories</h2>
      % for category in scoring_data.CLAN_CATEGORIES:
      <div class="row">
        <div class="col">
          <p>
            <b>${category.name}:</b> ${category.desc}
          </p>
        </div>
      </div>
      % endfor
    </div>
  </div>

</%block>
