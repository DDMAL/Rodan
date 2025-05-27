/*******************************************************************************
 * PREVERSION
 *
 * We only allow new versions from master.
 ******************************************************************************/
const path = require('path');
const projectPath = path.resolve(__dirname, '../');
const git = require('simple-git')(projectPath);

git.status(function(error, data)
{
	// Check if master.
	if (data.current !== 'master')
	{
	    console.log("Must be on master branch with no changes to update version.");
	    process.exit(1);
	}

	// Check if credential helper.
	git.raw(['config', 'credential.helper'], function(error, data)
	{
		if (!data || data === '')
		{
	    	console.log('No git credential.helper detected. You need to set this up to version this package.');
			process.exit(1);
		}
		else
		{
			process.exit();
		}
	});
});