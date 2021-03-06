<%inherit file="base.mako"/>
<%block name="navbar">
% if request.authenticated_userid:
<nav class="navbar navbar-default navbar-fixed-top" role="navigation">
  <div class="container-fluid">
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="/">Home</a>
      <p class="navbar-text">Signed in as ${get_username(request.authenticated_userid)} (${request.authenticated_userid})</p>
    </div>

    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <ul class="nav navbar-nav">
% if request.has_permission('add'):
      <form class="navbar-form navbar-left" role="search">
        <div class="form-group">
          <input type="text" id="page_to_add" class="form-control" placeholder="Title of post">
        </div>
        <button type="Submit" id="add_button" class="btn btn-default">Add</button>
      </form>
% endif
% if request.matched_route.name in ('view_post', 'home'):
% if request.has_permission('edit'):
        <li><a href="${request.route_url('change_post', postname = urlify(title), id = post_id, action = 'edit')}">Edit this page</a></li>
% endif
% if request.has_permission('del'):
        <li><a href="${request.route_url('change_post', postname = urlify(title), id = post_id, action = 'del')}">Delete this page</a></li>
% endif
% endif
% if 'g:admin' in request.effective_principals:
        <li class="dropdown">
          <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">Manage blog <span class="caret"></span></a>
          <ul class="dropdown-menu" role="menu">
            <li><a href="${request.route_url('tag_manager')}">Manage tags</a></li>
            <li><a href="#">Manage users</a></li>
            <li><a href="#">Manage comments</a></li>
            <li><a href="${request.route_url('settings')}">Settings</a></li>
            <li><a href="${request.route_url('update_check')}">Check for updates</a></li>
          </ul>
        </li>
% endif
      </ul>
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>
% endif
</%block>

<%block name="navbar_js">
<script type="text/javascript">
$(document).ready(function(){
    $("#add_button").click(function(event){
        var page_to_add = $("#page_to_add").val();
        if (page_to_add != ""){
            window.location.href = "/add_post/"+page_to_add;
        }
        event.preventDefault();
    });
});
</script>
</%block>
