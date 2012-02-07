%def auth():
	%if get('no_email', False):
		<h1>Welcome so and so</h1>
		<p>We can't wait to help you make plans with your friends, but first we need to know how to get in touch with you.</p>
		<form>
			<label>Email <input name=email></label>
			<input type=submit> 
		</form>
	%end
	<h2>Don't worry</h2>
	<p>We only use your personal information for our records and to send you notifications from your friends. We won't send you spam, or sell your information to third parties. You can <a href="delete">delete your account and all your data</a> at any time.</p>
%end

%rebase main stage=auth
