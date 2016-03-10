<%inherit file="base.mako"/>
<%block name="style">
    ${parent.style()}
        .navbar {
            display: flex;
            flex-direction: row;
            flex-wrap: wrap;
            justify-content: space-around;
            width: inherit;
        }
</%block>

<%block name="header_toolbar">
    <div class="navbar">
        % if request.authenticated_userid:

            <div><a href="/">Home</a></div>
            ${parent.header_toolbar()}
            <div>Signed in as ${get_username(request.authenticated_userid)} (${request.authenticated_userid})</div>
            % if request.has_permission('add') and request.matched_route.name in ('view_post', 'home'):
                <div>
                    <form role="search">
                        <input type="text" id="page_to_add" placeholder="Title of post" size="10">
                        <button type="Submit" id="add_button">Add</button>
                    </form>
                </div>
            % endif

            % if request.matched_route.name in ('view_post', 'home'):
                % if request.has_permission('edit'):
                    <div><a href="${request.route_url('change_post', postname=urlify(title), id=post_id, action='edit')}">Edit post</a></div>
                % endif
                % if request.has_permission('del'):
                    <div><a href="${request.route_url('change_post', postname=urlify(title), id=post_id,
                            action='del')}">Delete post</a></div>
                % endif
            % endif
            % if 'g:admin' in request.effective_principals:
                <div><a href="${request.route_url('tag_manager')}">Manage tags</a></div>
                <div><a href="${request.route_url('settings')}">Settings</a></div>
                <div><a href="${request.route_url('update_check')}">Check for Updates</a></div>
            % endif
        % else:
            ${parent.header_toolbar()}
        % endif
    </div>
</%block>

<%block name="footer_js">
    ${parent.footer_js()}
    % if request.has_permission('add') and request.matched_route.name in ('view_post', 'home'):
        <script type="text/javascript">
            $(document).ready(function(){
                $("#add_button").click(function(event){
                    var page_to_add = $("#page_to_add").val();
                    if (page_to_add != ""){
                        window.location.href = "/add_post/"+page_to_add;
                    }
                    event.preventDefault();
            });});
        </script>
    % endif
</%block>
