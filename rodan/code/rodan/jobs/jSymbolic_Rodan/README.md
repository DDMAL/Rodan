jSymbolic-Rodan
===============
jSymbolic-Rodan is a Rodan Job Package which acts as a wrapper around
the jSymbolic software. This allows access to all of the jSymbolic
functionality through the Rodan UI. In turn, one can access jSymbolic
through the Rodan Client. jSymbolic-Rodan is implemented as an
automatic phase job within the Rodan framework. Therefore, the job
does not wait for any manual input from the user, it simply runs given
the specified input and output type files.

In particular, the default command of jSymbolic-Rodan (i.e. without a
configuration file) will run the default command line of jSymbolic.
This command involves extracting all default features from
jSymbolic and also outputs the CSV and ARFF file formats for
the users convenience. A configuration file can also be specified
in the jSymbolic-Rodan job and this is discussed in the next section.

In order to add this to a Rodan implementation, it is required that
a qualified Rodan administrator install and deploy this as a Rodan
job in the appropriate fashion.

### jSymbolic-Rodan with Configuration File
If the configuration file import port is included, then the
jSymbolic-Rodan job can be run with a specified configuration file.
This configuration file must conform to the jSymbolic configuration
file standards (which can be found in the jSymbolic 2.0 manual),
otherwise, an error will be shown to the user. In particular,
the configuration file must only include the feature and option headers.
Other headers interact with the file system which is dealt with by
Rodan for Rodan job packages.

Once a valid configuration file is passed with a corresponding music
file, then Rodan will run jSymbolic with the settings allocated in the
given configuration file. jSymbolic will run and output all
of the data (i.e. features and file formats) specified in the given
configuration file.

WARNING: Because there are optional formats in the jSymbolic-Rodan job,
a user can choose to have file format conversion output ports or not. 
If a user specifies to convert to a file format in the configuration 
file but does not specify the corresponding output port, then the file 
will not be accessible by the user. If the user does not want a 
particular file conversion in the configuration file, but does include 
the corresponding output port, then the jSymbolic-Rodan job will force 
the configuration file to output the file format of the given output 
port. This is done to create consistency and reduce error within the 
Rodan framework.

### jSymbolic-Rodan Input File Formats
jSymbolic-Rodan can currently take in both MEI XML, MusicXML and MIDI 
music file formats. These are both validated and parsed by jSymbolic.

### Installations
jSymbolic.jar file path must be specified in the Rodan Django settings
in the file django.conf.settings under the setting name : JSYMBOLIC_JAR
Note: only add path to file and not file itself
(e.g. /tmp/java/jsymbolic/)

The remainder of jSymbolic-Rodan is implemented as per the
specifications that are outlined on the Rodan Wiki. This can be found
at https://github.com/DDMAL/Rodan/wiki/Write-a-Rodan-job-package.

### Detailed Description of jSymbolic Wrapper
extract_features.py :
This is where the main logic of the jSymbolic wrapper is held. The 
input_port_types and output_port_types define what the input and 
output files that the jSymbolic wrapper can take. This is supplied in
the format required by Rodan jobs. The run_my_task function is used
by Rodan to validate file inputs (i.e. music files and configuration
files) for jSymbolic. jSymbolic run using the configuration file and
if none is provided, then the default jSymbolic process is run
as described in the jSymbolic manual. The returned output files are
then placed in the proper placeholders for Rodan to show to the user.

resource_types.yaml:
All of the available file types for jSymbolic (input and output) are
specified here as per Rodan specifications. Note that this these
can be found in the URL in the installation section of this README.

jsymbolic_utilities.py:
This is used to abstract out common functions used in the jSymbolic
wrapper. This includes an execution function which runs the given
command line command in the given working directory and then parses
error in a convenient way by returning system and java errors as a
string instead of throwing exceptions back to the user level. This is
then displayed int the my_error_information function in the 
extract_features.py class. The parse_convert_from_config_file deals with
conversion issues since it was a design decision to always output
csv and arff files for the jSymbolic wrapper. This is required by Rodan
since all output files must be specified and so we output everything
in order to appease this constraint.