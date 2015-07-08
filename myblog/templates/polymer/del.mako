<%inherit file="navbar.mako"/>

<%block name="head">
${parent.head()}
<link rel="import" href="${request.static_url('myblog:static/form-submit.html')}">
</%block>

<%block name="header">${title}</%block>

<%block name="content">
<p>Are you sure you want to delete this page? If so, click the button below.</p>

<form id = "del-post" action = "${save_url}" method = "post">
<input type="hidden" name="form.submitted">
<form-submit-button>Delete this post</form-submit-button>
</form>

</%block>
