%def stage():
	<article>
		
		<header>
			<h1><img src="{{user.photo}}">{{user.firstName}} {{user.lastName}}</h1>
			<p><a href="{{user.link}}">Foursquare Profile</a></p>
			<p>{{user.email}}</p>
		</header>
		
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
		
		<h2>Times when you checkin</h2>
		<div class="flexbox btn-group">
	%for g in range(len(groups)):
			<div class="btn" style="-webkit-box-flex: {{groups[g]['width']}};
  -moz-box-flex: {{groups[g]['width']}};
  box-flex: {{groups[g]['width']}};%">
				{{groups[g]['len']}}
				<br>
				{{groups[g]['start']}}-{{groups[g]['end']}}
			</div>
	%end
		</div>
		
	</article>
%end

%def script():
	$('.btn').button()
%end

%rebase main stage=stage, debug=get('debug', None), script=script
