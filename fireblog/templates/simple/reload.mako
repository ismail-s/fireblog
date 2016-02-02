<%inherit file="navbar.mako" />

<%block name="head">
    ${parent.head()}
    <meta http-equiv="refresh" content="2;url=${request.route_url('home')}" />
</%block>

<%block name="header">Restarting the website</%block>

<%block name="content">
    <p>The blog is currently restarting. You are being redirected to the homepage, which will load once the blog has restarted.</p>
</%block>
