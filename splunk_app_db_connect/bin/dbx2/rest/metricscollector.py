from __future__ import absolute_import
import json
import sys
import os.path as op

import splunk
import splunk.entity as entity
import splunk.rest as rest
import splunklib.results as results

from dbx2.splunk_client.splunk_service_factory import SplunkServiceFactory


"""
ApimetricscollectorRestHandler
"""

DEFAULT_HOST_PORT = '127.0.0.1:8089'


class ApimetricscollectorRestHandler(rest.BaseRestHandler):

    def __init__(self, *args, **kwargs):
        rest.BaseRestHandler.__init__(self, *args, **kwargs)
        self.context = ContextUtil.get_context(request=self.request,
                                               sessionKey=self.sessionKey,
                                               pathParts=self.pathParts)
        self.response.setHeader('Content-Type', 'application/json')

    def handle_GET(self):
        results = self._format_results(self._get_data())
        self.response.write(json.dumps(results))

    def _get_data(self):
        indexName, reportName = self._get_summary_index()
        spl = 'search index={} earliest=-7d@d latest=@d report={} | timechart span=1d useother=f max(sum_mb) as volume by series | fillnull value=0 | eval time = strftime(_time, "%F") | fields - _time, _span, _spandays'.format(indexName, reportName)
        job = self._get_svc().jobs.oneshot(spl)
        return list(results.ResultsReader(job))

    def _get_svc(self):
        return SplunkServiceFactory.create(session_key=self.sessionKey,
                                           app=self.context['app'],
                                           owner=self.context['user'])

    def _get_summary_index(self):
        defaultIndex = 'summary'
        defaultReport = 'ui_metrics_collector_indexed_data_volumes'

        searchName = '{}.apimetricscollector: calculate indexed data volume'.format(self.context['app'])

        savedSearch = entity.getEntity(
            'configs/conf-savedsearches',
            searchName,
            sessionKey = self.sessionKey,
            namespace = self.context['app'],
            owner = self.context['user']
        )
        index = savedSearch.get('action.summary_index._name', defaultIndex)
        report = savedSearch.get('action.summary_index.report', defaultReport)
        return (index, report)

    def _format_results(self, entities):
        if len(entities) == 1 and isinstance(entities[0], results.Message):
            raise ApimetricscollectorException(500, entities[0].message)

        usages = []
        for data_per_day in entities:
            usage = dict()
            usage['time'] = data_per_day.pop('time')
            usage['volumes'] = data_per_day
            usages.append(usage)
        all_usage = dict()
        all_usage['usage'] = usages
        return all_usage

class ContextUtil:

    def __init__(self):
        pass

    @staticmethod
    def get_context(**kwargs):
        request = kwargs.get('request', None)
        session = kwargs.get('sessionKey', None)
        path = kwargs.get('pathParts', None)

        if request is None or '':
            raise ApimetricscollectorException(400, "Request is empty")

        """
        # API --> services/app/version/api/id/action
        # Required --> services, version, app, api
        # Optional --> id, action
        """

        context = dict()
        context['request'] = request
        context['user'] = request['userName']
        context['session'] = session
        context['app'] = path[1] if len(path) > 1 else None
        context['api'] = path[3] if len(path) > 3 else None
        context['collection'] = path[1] + '_' + path[3] if len(path) > 3 else None
        if request['payload'] is not None and not '' and len(request['payload']) > 0:
            context['payload'] = json.loads(request['payload'])
        else:
            context['payload'] = None
        context['id'] = path[4] if len(path) > 4 else None
        context['action'] = path[5] if len(path) > 5 else None
        context['version'] = path[2] if len(path) > 2 else None
        context['query'] = request['query']

        return context

class ApimetricscollectorException(splunk.RESTException):
    def __init__(self, status_code, msg):
        splunk.RESTException.__init__(self, status_code, msg)
