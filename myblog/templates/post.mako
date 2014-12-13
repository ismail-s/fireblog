<%inherit file="base.mako"/>

<%block name="header">${title}</%block>

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
      <p class="navbar-text">Signed in as ${request.authenticated_userid}</p>
    </div>

    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <ul class="nav navbar-nav">
      <form class="navbar-form navbar-left" role="search">
        <div class="form-group">
          <input type="text" class="form-control" placeholder="Title of post">
        </div>
        <button type="Submit" class="btn btn-default">Add</button>
      </form>
        <li><a href="${request.route_url('edit_post', postname = title)}">Edit this page</a></li>
        <li><a href="${request.route_url('del_post', postname = title)}">Delete this page</a></li>
        <li class="dropdown">
          <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-expanded="false">Manage blog <span class="caret"></span></a>
          <ul class="dropdown-menu" role="menu">
            <li><a href="#">Manage users</a></li>
            <li><a href="#">Manage comments</a></li>
          </ul>
        </li>
      </ul>
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>
% endif
</%block>

<%block name="content">
${html|n}

<ul class="pager">

% if prev_page:
  <li><a href="${prev_page}">Older</a></li>
% endif

% if next_page:
  <li><a href="${next_page}">Newer</a></li>
% endif

</ul>

</%block>
