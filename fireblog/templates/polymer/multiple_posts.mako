<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="head">
${parent.head()}
<link rel="import" href="${get_bower_url('paper-dropdown-menu/paper-dropdown-menu.html')}">
<link rel="import" href="${get_bower_url('paper-item/paper-item.html')}">
<link rel="import" href="${get_bower_url('paper-menu/paper-menu.html')}">
</%block>

<%block name="content">

<%
if code_styles:
     from pygments.formatters import HtmlFormatter
     extra_styles = HtmlFormatter.get_style_defs(HtmlFormatter())
else:
    extra_styles = None
%>

% if extra_styles:
<style>
${extra_styles}
</style>
% endif

## Sort order dropdown
<paper-dropdown-menu label="Sort Order">
  <paper-menu class="dropdown-content">
    <a href="${oldest_first_url}">
        <paper-item>Oldest First</paper-item>
    </a>
    <a href="${newest_first_url}">
        <paper-item>Newest First</paper-item>
    </a>
  </paper-menu>
</paper-dropdown-menu>

## Pager
<div class="center">${pager|n}</div>

## All the posts that are to be displayed
% for post in posts:
<paper-material class="card">
    <a href = "${request.route_url('view_post', id=post["id"], postname = urlify(post["name"]))}">
        <h1 class="center">
                ${post["name"]} <small>Created ${post["date"]}</small>
        </h1>
    </a>
    <div class="panel-body">
        ${post["html"]|n}
    </div>
</paper-material>
</a>
% endfor

## Pager
<div class="center">${pager|n}</div>

## uuid
% if uuid:
<p style="text-align: center"><small>
<a href="${request.route_url('uuid', uuid = uuid)}">Permalink</a>
</small></p>
% endif

</%block>
