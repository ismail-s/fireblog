<%inherit file="navbar.mako"/>

<%block name="header">${title}</%block>

<%block name="head">
    ${parent.head()}
    <style>
        th, td {
            border: 1px solid black;
        }
    </style>
</%block>

<%block name="content">
    <p>These are all the tags that are used on this blog. Uncheck a checkbox to delete that tag. Change the text in a textbox to rename a tag.</p>
    <p><i>Please note that deleting a tag is irreversible.</i></p>

    <form id="tag-manager" action="${save_url}" method="post">
        <table>
            <thead><tr>
                    <th>Keep tag</th>
                    <th>Tag name</th>
                    <th>No. of posts that use this tag</th>
            </tr></thead>
            <tbody>
                % for tag, no_of_posts in tags:
                    <tr>
                        <th>
                            <input type="checkbox" name="check-${tag}" checked>
                        </th>
                        <th>
                            <input type="text" name="text-${tag}"
                            id="tag-${tag}"
                            value="${tag}">
                        </th>
                        <th>
                            <a href="${request.route_url('tag_view', tag_name=tag)}">${no_of_posts}</a>
                        </th>
                    </tr>
                % endfor
            </tbody>
        </table>
        <input type="hidden" name="form.submitted">
        <input type="submit" value="Submit">
    </form>
</%block>
