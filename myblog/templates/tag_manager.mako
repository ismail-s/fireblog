<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="content">
<p>These are all the tags that are used on this blog. Uncheck a checkbox to delete that tag. Change the text in a textbox to rename a tag.</p>
<p><i>Please note that deleting a tag is irreversible.</i></p>
<form id = "tag-manager" action = "${save_url}" method = "post">
<table class="table table-striped table-bordered">
<thead>
<tr>
<th>Keep tag</th>
<th>Tag name</th>
<th>No. of posts that use this tag</th>
</tr>
</thead>

<tbody>
% for tag, no_of_posts in tags:
<tr>
<th>
    <input type="checkbox" name="check-${tag}" checked>
</th>
<th>
<input type="text" name = "text-${tag}"
id="tag-${tag}"
value = "${tag}"
class="form-control">
</th>
<th>
<a href = "${request.route_url('tag_view', tag_name = tag)}">${no_of_posts}</a>
</th>
</tr>
% endfor

</tbody>
</table>

<div class="form-group">
    <input type = "submit" name = "form.submitted"
        value = "Submit" class = "form-control"/>
</div>

</form>
</%block>