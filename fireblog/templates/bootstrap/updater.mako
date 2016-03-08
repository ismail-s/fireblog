<%inherit file="navbar.mako"/>

<%block name="header">Update check</%block>

<%block name="content">

% if update_available and not db_upgrade_required:
<p>Updates are available, and can be installed automatically. To install them,
please click the button below, which will do the following:</p>

<ol>
    ## Yes, it is misleading to say we will be downloading the latest code
    ## when it already has been downloaded, but meh, it is conceptually
    ## simpler.
    <li>Download the latest version of the code</li>
    <li>Switch to the new code</li>
    <li>Restart the website</li>
</ol>

<p>If the website fails to restart, then you will want to undo the update.
Assuming that you are familiar with using the terminal, simply <b>cd</b> to the
folder where the blog source code is, and then run
<b>git branch</b> to see what branch you are on, and then
<b>git reset --hard branch_name^</b> (the ^ is important) to undo the update.
Then, to restart the blog, see the commands on the
<a href="//ismail-s.github.io/fireblog/">fireblog homepage</a></p>

<form id = "update-blog" action = "${save_url}" method = "post">
    <button type="submit"
            name="form.submitted"
            class="btn btn-danger">
        Update this blog</button>
</form>
% endif

% if update_available and db_upgrade_required:
<p>Updates are available, but they cannot be installed automatically.
This is because the database will need to updated during the update.
To do this, you will need to run the following commands on the server in the
folder containing the source code for this blog:</p>

<ol>
    <li><b>git pull</b> to update to the latest code</li>
    <li><b>alembic upgrade head</b> to update the db. If this doesn't work,
    then you may want to contact me. See
    <a href="//www.github.com/ismail-s/fireblog">the Github page</a> for
    contact details.</li>
    <li>Then just restart the blog (using the reload link in the navbar on
    this page).</li>
</ol>
% endif

% if not update_available:
<p>No updates for the blog are available at the moment.</p>
% endif

</%block>
