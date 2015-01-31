<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

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

<div class = "post">
${html|n}
</div>
<p style="text-align: center"><small>Created ${post_date}.
% if tags:
Tags: ${tags}
% endif
</small></p>
<ul class="pager">

% if prev_page:
  <li><a href="${prev_page}">Older</a></li>
% endif

<li><a href="${request.route_url('view_all_posts')}">All Posts</a></li>

% if next_page:
  <li><a href="${next_page}">Newer</a></li>
% endif

</ul>

</%block>
