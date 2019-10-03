var SDC = require('statsd-client'),
    sdc = new SDC({host: 'localhost', port: 8125});
sdc.raw('server.request:26|c|@0.5|#region:us-east-1,datacenter:us-east-1a,rack:63,os:Ubuntu16.10,arch:x64,team:LON,service:6,service_version:0,service_environment:test, path:/dev/sdal,fstype:ext3');