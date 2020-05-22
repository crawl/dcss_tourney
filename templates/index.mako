<%inherit file="base.mako"/>

## Run on template load (no render context)
<%!
  import scoring_data
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
</%block>
