<!doctype html>
<html class="no-js" lang="en" itemscope itemtype="http://schema.org/CreativeWork">
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">

	<title itemprop="name">Yes, Let's</title>
	<meta name="description" itemprop="description" content="Find a time and place to hang out with your friends based on your Foursquare checkins.">
	<meta name="author" content="Jesse Hattabaugh<arkanciscan@gmail.com>">
	<link rel="canonical" href="http://yes-lets.appspot.com">
	
	<meta name="viewport" content="width=device-width,initial-scale=1">

	<link rel="stylesheet" href="/bootstrap.css">
	<style>
	body {
		padding-top: 60px;
		padding-bottom: 40px;
	}
	</style>
	<link rel="stylesheet" href="/bootstrap-responsive.css">
	<link rel="stylesheet" href="/style.css">

	<script src="modernizr-2.5-respond-1.1.0.min.js"></script>
</head>
<body>
<!--[if lt IE 7]><p class=chromeframe>Your browser is <em>ancient!</em> <a href="http://browsehappy.com/">Upgrade to a different browser</a> or <a href="http://www.google.com/chromeframe/?redirect=true">install Google Chrome Frame</a> to experience this site.</p><![endif]-->

	<header class="navbar navbar-fixed-top">
		<div class="navbar-inner">
			<div class="container">
				<a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
					<span class="i-bar"></span>
					<span class="i-bar"></span>
					<span class="i-bar"></span>
				</a>
				<a class="brand" href="/">Yes, Let's!</a>
				<div class="nav-collapse">
					<nav class="nav">
						<li class="active"><a href="/">Home</a></li>
						<li><a href="/invite">Invite</a></li>
						<li><a href="/about">About</a></li>
					</nav>
				</div><!--/.nav-collapse -->
			</div>
		</div>
	</header>

	<div class="container">
%if defined('stage'):
	%stage()
%else:
	Nothing Here
%end
		
		<hr>

		<footer>
			&copy; 2012 <a href="mailto:arkancsican@gmail.com">Jesse Hattabaugh</a>
			<img style="width:250px" src="https://playfoursquare.s3.amazonaws.com/press/logo/poweredByFoursquare_gray.png">
			<img src="//code.google.com/appengine/images/appengine-silver-120x30.gif" 
alt="Powered by Google App Engine">
			<div class="g-plusone" data-annotation="inline" data-width="200"></div>
		</footer>

	</div> <!-- /container -->
	
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
	<script>window.jQuery || document.write('<script src="/jquery-1.7.1.min.js"><\/script>')</script>

	<script src="/transition.js"></script>
	<script src="/collapse.js"></script>
	<script src="/collapse.js"></script>
	
	<script src="/plugins.js"></script>
	<script src="/main.js"></script>
%if defined('script'):
	<script type="text/javascript">
		%script()
	</script>
%end
	
	<script>
		var _gaq=[['_setAccount','UA-XXXXX-X'],['_trackPageview']];
		(function(d,t){var g=d.createElement(t),s=d.getElementsByTagName(t)[0];
		g.src=('https:'==location.protocol?'//ssl':'//www')+'.google-analytics.com/ga.js';
		s.parentNode.insertBefore(g,s)}(document,'script'));
	</script>
	
	<script type="text/javascript">
		(function() {
			var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
			po.src = 'https://apis.google.com/js/plusone.js';
			var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
		})();
	</script>

%if defined('debug') and debug:
	<pre>
		{{debug}}
	</pre>
%end

</body>
</html>
