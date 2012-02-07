%import time
%def unauthed():

	<article class="hero-unit" role="main">
		<h1>Lets hang out sometime!</h1>
		<p>You and your friends always say that, but everybody's so busy 
		it's hard to find a time to meet up. Using your Foursquare 
		checkins we can tell where you and your friends hang out 
		and what time you're there. So lets get started. Shall we!?</p>
		<p><a href="https://foursquare.com/oauth2/authenticate?client_id={{client_id}}&response_type=code&redirect_uri={{redirect_uri}}"><img src="https://playfoursquare.s3.amazonaws.com/press/logo/connect-blue@2x.png"></a></p>
		
		<h2>Don't worry</h2>
		<p>We only use your personal information for our records and to send you notifications from your friends. We won't send you spam, or sell your information to third parties.</p>
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
		
		<!--<ul class="nav nav-pills">
			<li class="active"><a href="#">Any Day</a></li>
			<li class="dropdown">
				<a class="dropdown-toggle" data-toggle="dropdown" href="#">
					Weekdays
					<i class="caret"></i>
				</a>
				<ul class="dropdown-menu">
					<li><a href="#">Mondays</a></li>
					<li><a href="#">Tuesdays</a></li>
					<li><a href="#">Wednesdays</a></li>
					<li><a href="#">Thursdays</a></li>
					<li><a href="#">Fridays</a></li>
				</ul>
			</li>
			<li class="dropdown">
				<a class="dropdown-toggle" data-toggle="dropdown" href="#">Weekends
					<i class="caret"></i></a>
				<ul class="dropdown-menu">
					<li><a href="#">Saturday</a></li>
					<li><a href="#">Sunday</a></li>
				</ul>
			</li>
			<li><a href="#">Today</a></li>
			<li><a href="#">Tomorrow</a></li>
		</ul>-->
		
		<p>These are the </p>
		<div class="flexbox btn-group">
	%for g in range(len(groups)):
			<div class="btn" style="-webkit-box-flex: {{groups[g]['width']}};
  -moz-box-flex: {{groups[g]['width']}};
  box-flex: {{groups[g]['width']}};%">
				{{groups[g]['len']}}
				<br>
				{{str(abs(int(time.strftime('%I',time.gmtime(groups[g]['tod_min'])))))+time.strftime('%p',time.gmtime(groups[g]['tod_min']))}}-{{str(abs(int(time.strftime('%I',time.gmtime(groups[g]['tod_max'])))))+time.strftime('%p',time.gmtime(groups[g]['tod_min']))}}
			</div>
	%end
		</div>
		
	</article>
%end

%def script():
	$('.btn').button()
%end

%if defined('user'):
	%rebase main stage=authed, debug=get('debug', None), script=script
%else:
	%rebase main stage=unauthed, debug=get('debug', None)
%end
