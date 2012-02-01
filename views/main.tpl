<!doctype html>
<html lang="en" itemscope itemtype="http://schema.org/CreativeWork">
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	
	<title itemprop="name">Yes, Let's!</title>
	<meta name="description" itemprop="description" content="Find a time and place to hang out with your friends based on your Foursquare checkins.">
	<meta name="author" content="Jesse Hattabaugh">
	
	<link rel="shortcut icon" href="favicon.ico">
	<link rel="apple-touch-icon" href="apple-touch-icon.png">
	<link rel="canonical" href="http://yes-lets.appspot.com">
	
	<link rel="stylesheet" href="boilerplate.min.css">
	<link rel="stylesheet" href="bootstrap.min.css">
	<link rel="stylesheet" href="main.css">
%if defined('style'):
	<style type="text/css">
		{{style}}
	</style>
%end
	
	<script src="modernizr-2.0.6.min.js"></script>
	<!--[if lt IE 9]>
		<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->
</head>

<body>

	<header class="navbar">
		<div class="navbar-inner">
			<div class="container">
				<a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</a>
				<a class="brand" href="#">Yes, Let's!</a>
				<nav class="nav nav-collapse">
					<li class="active"><a href="#">Home</a></li>
					<li><a href="#invite">Invite</a></li>
					<li><a href="#friends">Friends</a></li>
				</nav>
			</div>
		</div>
	</header>

	<div class="container-fluid">

		<article class="hero-unit" role="main">
			<h1>Lets hang out sometime!</h1>
			<p>You and your friends always say that, but everybody's so busy 
			it's hard to find a time to meet up. Using your Foursquare 
			checkins we can tell where you and your friends hang out 
			and what time you're there. So lets get started. Shall we!?</p>
			<p><a class="btn-info btn-large" href="https://foursquare.com/oauth2/authenticate?client_id=0PXXC32KMHDKTYBFT1WXIS14TIJAD03GFJXEWXTTLO2XL0ZV&response_type=code&redirect_uri=http://yes-lets.appspot.com/callback">Log in with Foursquare</a></p>
		</article>

		<div class="row-fluid">
			<div class="span3">
				<h2>Everybody's so flakey.</h2>
				<p>It's not their fault though. Sometimes you just need a little nudge to get the party started.</p>
				<p><a class="btn" href="#">View details &raquo;</a></p>
			</div>
			<div class="span3">
				<h2>Who has the time?</h2>
				<p>People's work and school schedules make it hard to find a time when you're both available. If you're checking in maybe you have time to hang out.</p>
				<p><a class="btn" href="#">View details &raquo;</a></p>
			</div>
			<div class="span3">
				<h2>That's so far!</h2>
				<p>Using the geolocation of your checkins we can find places nearby where you already go.</p>
				<p><a class="btn" href="#">View details &raquo;</a></p>
			</div>
		</div>
	
		<footer>
			&copy; 2012 <a href="mailto:arkancsican@gmail.com">Jesse Hattabaugh</a>
			<img src="//code.google.com/appengine/images/appengine-silver-120x30.gif" 
alt="Powered by Google App Engine" />
			<div class="g-plusone" data-annotation="inline" data-width="200"></div>
		</footer>
	
	</div> <!-- /container -->
	
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
	<script>window.jQuery || document.write('<script src="jquery-1.7.1.min.js"><\/script>')</script>
	
	<script defer src="plugins.js"></script>
	<script defer src="main.js"></script>
%if defined('script'):
	<script type="text/javascript">
		{{script}}
	</script>
%end
	
	<script>
		window._gaq = [['_setAccount','UAXXXXXXXX1'],['_trackPageview'],['_trackPageLoadTime']];
		Modernizr.load({
			load: ('https:' == location.protocol ? '//ssl' : '//www') + '.google-analytics.com/ga.js'
		});
	</script>
	
	<script type="text/javascript">
		(function() {
			var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
			po.src = 'https://apis.google.com/js/plusone.js';
			var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
		})();
	</script>
	
	<!--[if lt IE 7 ]>
		<script src="//ajax.googleapis.com/ajax/libs/chrome-frame/1.0.3/CFInstall.min.js"></script>
		<script>window.attachEvent('onload',function(){CFInstall.check({mode:'overlay'})})</script>
	<![endif]-->
</body>
</html>
