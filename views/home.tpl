%def unauthed():

	<article class="hero-unit" role="main">
		<h1>Lets hang out sometime!</h1>
		<p>You and your friends always say that, but everybody's so busy 
		it's hard to find a time to meet up. Using your Foursquare 
		checkins we can tell where you and your friends hang out 
		and what time you're there. So lets get started. Shall we!?</p>
		<p><a href="https://foursquare.com/oauth2/authenticate?client_id={{client_id}}&response_type=code&redirect_uri={{redirect_uri}}"><img src="https://playfoursquare.s3.amazonaws.com/press/logo/connect-blue@2x.png"></a></p>
	</article>

	<div class="row">
		<div class="span4">
			<h2>Everybody flakes.</h2>
			<p>It's not their fault though. Sometimes you just need a little nudge to get the party started.</p>
			<p><a class="btn" href="#">View details &raquo;</a></p>
		</div>
		<div class="span4">
			<h2>Who has the time?</h2>
			<p>People's work and school schedules make it hard to find a time when you're both available. If you're checking in maybe you have time to hang out.</p>
			<p><a class="btn" href="#">View details &raquo;</a></p>
		</div>
		<div class="span4">
			<h2>That's so far!</h2>
			<p>Using the geolocation of your checkins we can find places nearby where you already go.</p>
			<p><a class="btn" href="#">View details &raquo;</a></p>
		</div>
	</div>
%end

%def authed():
	<article>
		
		<h1><img src="{{user['photo']}}">{{user['firstName']}} {{user['lastName']}}</h1>
		<h2>{{user['homeCity']}}</h2>
		<p><a href="{{user['canonicalUrl']}}">Foursquare Profile</a></p>
		<p>{{user['contact']['email']}}</p>
		
	</article>
%end

%if defined('user'):
	%rebase main stage=authed, debug=get('debug', None)
%else:
	%rebase main stage=unauthed, debug=get('debug', None)
%end
