%def stage():
	<article>
		
		<header>
			<h1><img src="{{user.photo}}">{{user.first}} {{user.last}}</h1>
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
		
		<h2>Areas where you checkin</h2>
		<div class="row">
			<div class="span6" style="height: 500px">
				<div id="map_canvas" style="width: 100%; height: 100%"></div>
			</div>
			<div class="span6">Venues go over here</div>
		</div>
		
	</article>
%end

%def script():
	$().ready(function(){
		$('.btn').button()
	
		var map = new google.maps.Map($("#map_canvas")[0], {
			mapTypeId: google.maps.MapTypeId.ROADMAP
		});
		var bounds = new google.maps.LatLngBounds();
		var ne = new google.maps.LatLng({{most['north']}},{{most['east']}});
		var sw = new google.maps.LatLng({{most['south']}},{{most['west']}});
		bounds.extend(ne);
		bounds.extend(sw);
		map.fitBounds(bounds);
		var markers = [];
		var rectangles = [];
	%for a in areas:
		//markers.push(new google.maps.Marker({
		//	position: new google.maps.LatLng({{a['lat_mid']}},{{a['lng_mid']}}),
		//	map:map
		//}));
		var rbounds = new google.maps.LatLngBounds();
		var rne = new google.maps.LatLng({{a['lat_max']}},{{a['lng_max']}});
		var rsw = new google.maps.LatLng({{a['lat_min']}},{{a['lng_min']}});
		rbounds.extend(rne);
		rbounds.extend(rsw);
		rectangles.push(new google.maps.Rectangle({
			strokeWeight:1,
			fillOpacity:{{a['opacity']}},
			bounds:rbounds,
			map:map
		}))
	%end
	});
	
%end

%rebase main user=user, stage=stage, debug=get('debug', None), script=script
