<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="head">
${parent.head()}
<link rel="import" href="${request.static_url('myblog:static/form-submit.html')}">
<link rel="import" href="${request.get_bower_url('paper-checkbox/paper-checkbox.html')}">
<link rel="import" href="${request.get_bower_url('paper-input/paper-input.html')}">
</%block>

<%block name="content">
<paper-material class="card" elevation = "2">
    <p>These are all the tags that are used on this blog. Uncheck a checkbox to delete that tag. Change the text in a textbox to rename a tag.</p>
    <p><i>Please note that deleting a tag is irreversible.</i></p>

    <form id = "tag-manager" action = "${save_url}" method = "post">
        <table>
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
                        <paper-input type="text" name = "text-${tag}"
                            id="tag-${tag}"
                            value = "${tag}"></paper-input>
                    </th>
                    <th>
                        <a href = "${request.route_url('tag_view', tag_name = tag)}">${no_of_posts}</a>
                    </th>
                </tr>
% endfor

            </tbody>
        </table>
        <input type="hidden" name="form.submitted">
        <form-submit-button>Submit</form-submit-button>
    </form>
</paper-material>
</%block>
