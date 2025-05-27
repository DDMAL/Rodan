/*******************************************************************************
 * PRESTART
 *
 * Checks to see if 'configuration.json' exists. If not, it will help the user
 * create one.
 ******************************************************************************/

process.stdin.setEncoding('utf8');

const fs = require('fs');
const path = require('path');
const prompt = require('prompt-sync')({sigint: true});

const projectRoot = path.resolve(__dirname, '../');

// Check for file. If exists, we're good. Else, ask if they want to create.
fs.readFile(projectRoot + '/configuration.json', 'utf8', function(error, data)
{
    if (error)
    {
        if (error.errno !== -2)
        {
            throw error; 
        }
        console.log('File "configuration.json" NOT found.');
        console.log('You will need one to run the dev server.');

        var createConfig = promptCreateConfig();
        while(createConfig < 0)
        {
            createConfig = promptCreateConfig();
        }

        // Check for exit.
        if (createConfig === 0)
        {
            process.exit();
        }

        // Ask for IP/domain.
        var ipDomain = promptIPDomain();
        while (ipDomain === null)
        {
            ipDomain = promptIPDomain();
        }

        // Create config file.
        var config = require(projectRoot + '/configuration.example.json');
        config.SERVER_HOST = ipDomain;
        fs.writeFileSync(projectRoot + '/configuration.json', JSON.stringify(config, null, 4));
        console.log('Wrote ' + projectRoot + '/configuration.json');
    }
    else
    {
        console.log('File ' + projectRoot + '/configuration.json found');
    }

    // Check for plugins.json.
    var pluginsInclusionFile = projectRoot + '/plugins.json'; 
    try
    {
        var plugins = require(pluginsInclusionFile);
    }
    catch (error)
    {
        console.log('');
        console.log('Could not read ' + pluginsInclusionFile);
        console.log('If you wish to include plugins in the build, make sure they are declared in ' + pluginsInclusionFile + ' in JSON format.');
        console.log('');
        console.log('Example:');
        console.log('');
        console.log('{');
        console.log('  "some-plugin": {},');
        console.log('  "some-other-plugin": {}');
        console.log('}');
        console.log('');
        console.log('Please see the README for more info.');
        var input = prompt('Press return/enter to continue.');
        console.log('');
    }
    process.exit();
});

/**
 * Get config creation response.
 * 
 * @return {int} 0 if no, 1 if yes, -1 if error
 */
function promptCreateConfig()
{
    var input = prompt('Would you like to create it now? (y/n): ', 'y');
    input = input.toLowerCase();
    if (input === 'y')
    {
        return 1;
    }
    else if (input === 'n')
    {
        return 0;
    }
    console.log('invalid response');
    return -1;
}

/**
 * IP/domain string.
 * 
 * @return {string} null if invalid response/error
 */
function promptIPDomain()
{
    var input = prompt('Please enter IP or domain name of the Rodan server you wish the client to connect to: ');
    input = input.trim();
    if (input === '')
    {
        console.log('invalid response');
        return null;
    }
    return input;
}