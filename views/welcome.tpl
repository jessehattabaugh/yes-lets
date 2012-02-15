%def stage():
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
%end

%rebase main stage=stage