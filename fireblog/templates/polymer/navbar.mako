<%inherit file="base.mako"/>
<%block name="head">
${parent.head()}
<link rel="import" href="${request.get_bower_url('paper-icon-button/paper-icon-button.html')}">
<link rel="import" href="${request.get_bower_url('iron-icons/iron-icons.html')}">
<link rel="import" href="${request.get_bower_url('paper-fab/paper-fab.html')}">
<link rel="import" href="${request.get_bower_url('paper-input/paper-input.html')}">
<link rel="import" href="${request.get_bower_url('paper-dialog/paper-dialog.html')}">
</%block>

<%block name="header_toolbar">
% if request.authenticated_userid:

      <div><a class="navbar-brand" href="/"><paper-icon-button icon="home"></paper-icon-button></a></div>
${parent.header_toolbar()}
      <div class="flex-vertical flex-1">
        <div>Signed in as ${get_username(request.authenticated_userid)}</div>
        <div>(${request.authenticated_userid})</div>
      </div>
    % if request.matched_route.name in ('view_post', 'home'):
        % if request.has_permission('edit'):
        <div><a href="${request.route_url('change_post', postname = title, id = post_id, action = 'edit')}"><paper-icon-button icon="create"></paper-icon-button></a></div>
        % endif
        % if request.has_permission('del'):
        <div><a href="${request.route_url('change_post', postname = title, id = post_id, action = 'del')}"><paper-icon-button icon="delete"></paper-icon-button></a></div>
        % endif
    % endif
    % if 'g:admin' in request.effective_principals:
            <div><a href="${request.route_url('tag_manager')}"><paper-icon-button icon="label"></paper-icon-button></a></div>
    % endif
% else:
${parent.header_toolbar()}
% endif
</%block>

<%block name="main_body">
${parent.main_body()}
% if request.has_permission('add') and request.matched_route.name in ('view_post', 'home'):
<paper-fab icon="add" id="add"></paper-fab>
<paper-dialog modal id="add-dialog">
  <h2>Add a new post</h2>
  <paper-dialog-scrollable>
  <form>
    <paper-input id="page-to-add"
                label="Enter the post title">
    </paper-input></form>
  </paper-dialog-scrollable>
  <div class="buttons">
    <paper-button dialog-dismiss>Cancel</paper-button>
    <paper-button dialog-confirm id="add-post-button">Accept</paper-button>
  </div>
</paper-dialog>
% endif
</%block>
<%block name="footer_js">
${parent.footer_js()}
<script type="text/javascript">
$(document).ready(function(){
    $("#add-post-button").click(function(event){
        var page_to_add = $("#page-to-add").val();
        if (page_to_add != ""){
            window.location.href = "/posts/"+page_to_add+"/add";
        }
        event.preventDefault();
    });
    $("#add").click(function(){
        var x = $("#add-dialog")[0];
        x.open();
    });
});
</script>
</%block>
