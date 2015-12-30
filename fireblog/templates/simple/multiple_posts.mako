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
        <style>${extra_styles}</style>
    % endif

    <div>${pager|n}</div>

    % for post in posts:
        <a href="${request.route_url('view_post', id=post["id"], postname=urlify(post["name"]))}">
            <h1>
                ${post["name"]} <small>Created ${post["date"]}</small>
            </h1>
        </a>
        <div>${post["html"]|n}</div>
        <hr>
    </a>
% endfor

<div>${pager|n}</div>

% if uuid:
    <p style="text-align: center"><small>
            <a href="${request.route_url('uuid', uuid=uuid)}">Permalink</a>
    </small></p>
% endif

</%block>
