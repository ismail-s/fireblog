<%inherit file="base.mako"/>

<%block name="header">${title}</%block>

<%block name="content">
<p>Are you sure you want to delete this page? If so, click the button below.</p>

<form action = "${save_url}" method = "post">
<button type="submit" name = "form.submitted" class="btn btn-danger">Delete this post</button>
</form>

</%block>
