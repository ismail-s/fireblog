<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

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

% for post in posts:
<div class = "panel panel-default">
    <div class = "panel-heading all-posts-header">
    <a href = "${request.route_url('view_post', id=post["id"], postname = post["name"])}">
        <h2>
                ${post["name"]} <small>Created ${post["date"]}</small>
        </h2>
    </a>
    </div>
    <div class="panel-body">
        ${post["html"]|n}
    </div>
</div>
</a>
% endfor


% if uuid:
<p style="text-align: center"><small>
<a href="${request.route_url('uuid', uuid = uuid)}">Permalink</a>
</small></p>
% endif

</%block>
