<%inherit file="navbar.mako"/>

<%block name="head">
${parent.head()}
<link rel="import" href="${request.static_url('myblog:static/form-submit.html')}">
<link rel="import" href="${request.get_bower_url('paper-item/paper-item.html')}">
<link rel="import" href="${request.get_bower_url('paper-item/paper-item-body.html')}">
<link rel="import" href="${request.get_bower_url('paper-input/paper-textarea.html')}">
<link rel="import" href="${request.get_bower_url('paper-button/paper-button.html')}">
</%block>

<%block name="content">

<%
if 'class="codehilite"' in html:
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

<paper-material class="card" elevation = "2">
<h1 class="center">${title}</h1>
<div class = "post">${html|n}</div>

<p style="text-align: center"><small>Created ${post_date}.
% if tags:
Tags: ${tags|n}
% endif
<a href="${request.route_url('uuid', uuid = uuid)}">Permalink</a>
</small></p>
<div class="flex-horizontal-center">

% if prev_page:
  <a href="${prev_page}"><paper-button raised class="blue">Older</paper-button></a>
% endif

<a href="${request.route_url('view_all_posts')}"><paper-button raised>All Posts</paper-button></a>

% if next_page:
  <a href="${next_page}"><paper-button raised class="blue">Newer</paper-button></a>
% endif

</div>
</paper-material>


% for section in bottom_of_page_sections:
<paper-material class="card">
    ${section|n}
</paper-material>
% endfor
</%block>
