<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">


    <title>${settings_dict['persona.siteName']}</title>
  <%block name = "head">
    <!-- Latest compiled and minified CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
    <link rel="stylesheet" href="${request.get_bower_url('simplemde/dist/simplemde.min.css')}">
    <script src="${request.get_bower_url('simplemde/dist/simplemde.min.js')}"></script>

    <!-- Custom styles for this template -->
    <style>
        <%include file="fireblog:static/custom-theme.css"/>
    </style>

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
    <script src='https://www.google.com/recaptcha/api.js'></script>
    </%block>
  </head>
  <body>

<%block name = "navbar"/>

% for error in request.session.pop_flash():
<div class="alert alert-danger alert-dismissible" role="alert">
  <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
  ${error}
</div>
% endfor

</div>
<div class="page-header">
  <h1>${settings_dict['persona.siteName']} ${request.persona_button}</h1>
</div>
    <div class="container">
        <h1><%block name = "header"/></h1>
        <%block name = "content"/>
        <footer><a href = "${request.route_url('rss')}">rss</a></footer>
    </div><!-- /.container -->


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <!-- Latest compiled and minified JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
    <script src="https://login.persona.org/include.js" type="text/javascript"></script>
    <script type="text/javascript">${request.persona_js}</script>
    <%block name = "navbar_js"/>
  </body>
</html>
