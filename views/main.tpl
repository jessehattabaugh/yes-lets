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
				<a class="brand" href="/">Yes, Let's!</a>
				<nav class="nav nav-collapse">
					<li class="active"><a href="/">Home</a></li>
					<li><a href="#invite">Invite</a></li>
					<li><a href="#friends">Friends</a></li>
				</nav>
			</div>
		</div>
	</header>

	<div class="container">
%if defined('stage'):
	%stage()
%else:
	Nothing Here
%end
	
		<footer>
			&copy; 2012 <a href="mailto:arkancsican@gmail.com">Jesse Hattabaugh</a>
			<img style="width:250px" src="https://playfoursquare.s3.amazonaws.com/press/logo/poweredByFoursquare_gray.png">
			<img src="//code.google.com/appengine/images/appengine-silver-120x30.gif" 
alt="Powered by Google App Engine">
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
	
%if defined('debug') and debug:
	<pre>
		{{debug}}
	</pre>
%end
</body>
</html>
