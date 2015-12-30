<%inherit file="navbar.mako"/>

<%block name="content">

    <%
        if 'class="codehilite"' in html:
            from pygments.formatters import HtmlFormatter
            extra_styles = HtmlFormatter.get_style_defs(HtmlFormatter())
        else:
                extra_styles = None
    %>

    % if extra_styles:
        <style>${extra_styles}</style>
    % endif

    <h2>${title}</h2>
    <div>${html|n}</div>

    <p style="text-align: center"><small>Created ${post_date}.
            % if tags:
                Tags: ${tags|n}
            % endif
            <a href="${request.route_url('uuid', uuid = uuid)}">Permalink</a>
    </small></p>
    <div>
        % if prev_page:
            <a href="${prev_page}">Older</a>
        % endif
        <a href="${request.route_url('view_all_posts')}">All Posts</a>
        % if next_page:
            <a href="${next_page}">Newer</a>
        % endif
    </div>


    % for section in bottom_of_page_sections:
        <p>${section|n}</p>
    % endfor
</%block>
