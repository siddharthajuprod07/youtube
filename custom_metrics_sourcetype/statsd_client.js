var SDC = require('statsd-client'),
    sdc = new SDC({host: 'localhost', port: 8125});
sdc.raw('cpu1.percent.used.10.20.30.40.windows:39|g');