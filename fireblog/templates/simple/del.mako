<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="content">
    <p>Are you sure you want to delete this page? If so, click the button below.</p>

    <form id="del-post" action="${save_url}" method="post">
        <input type="hidden" name="form.submitted">
        <input type="submit" value="Delete this post">
    </form>
</%block>
