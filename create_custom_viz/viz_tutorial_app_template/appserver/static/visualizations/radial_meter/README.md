# Splunk Visualization App Template

This is the basic template for a splunk visualization app. This teamplate is meant to be edited to build custom visualizations. It contains:

- The relevant directory structure for a visuzliation app
- A standin visualization package directory with a standin visualiztion and a basic webpack configuration
- Relevant .conf files for the visualization

## Building the visualization

	NOTE: You must have npm installed in oder to build. If you do not have npm installed, install it and come back. 
	
The visualization contained in this app must be built using web pack in order to run it on Splunk. There is a basic webpack configuration built in to the app. To build from the command line, first, cd to the *visualization/standin* directory. On the first run you will have to install the dependeincies with npm:

```
$ npm install
```
Once you done that, you can build the viz with the provided build task:

```
$ npm run build
```

This will create a *visualization.js* file in the visualization directory. 

## Adding Your Own Code

The standin viz isn't very interesting, so you will want to add your own code. You should rename the *visualization/src/standin.js* file to something appropriate, then you can edit it as you see fit. To build, you will have to change the `entry` variable in *visualization/webpack.config* to corespond to your new file name. Then you can run the build task again.

## More Information
For more information on building custom visualizations including a tutorial, API overview, and more see:

http://docs.splunk.com/Documentation/Splunk/6.5.0/AdvancedDev/CustomVizDevOverview
