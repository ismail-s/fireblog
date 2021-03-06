<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>


<%block name="style">
    ${parent.style()}
    <%
        if code_styles:
            from pygments.formatters import HtmlFormatter
            extra_styles = HtmlFormatter.get_style_defs(HtmlFormatter())
        else:
            extra_styles = None
    %>
    % if extra_styles:
        ${extra_styles}
    % endif
</%block>

<%block name="content">

<select name="select" onchange="window.location.href=this.value">
    <option disabled selected>Sort Order</option>
    <option value="${oldest_first_url}">Oldest First</option>
    <option value="${newest_first_url}">Newest First</option>
</select>

<div>${pager|n}</div>

% for post in posts:
    <a href="${request.route_url('view_post', id=post["id"], postname=urlify(post["name"]))}">
        <h1>
            ${post["name"]} <small>Created ${post["date"]}</small>
        </h1>
    </a>
    <div>${post["html"]|n}</div>
    <hr>
% endfor

<div>${pager|n}</div>

% if uuid:
    <p style="text-align: center"><small>
            <a href="${request.route_url('uuid', uuid=uuid)}">Permalink</a>
    </small></p>
% endif

</%block>
