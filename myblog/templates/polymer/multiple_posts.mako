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
<paper-material class="card">
    <a href = "${request.route_url('view_post', postname = post["name"])}">
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


% if uuid:
<p style="text-align: center"><small>
<a href="${request.route_url('uuid', uuid = uuid)}">Permalink</a>
</small></p>
% endif

</%block>
