#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
  import json
except ImportError:
  import simplejson as json
import logging
import re
import os

from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_permission
from jobsub.management.commands import jobsub_setup
from jobsub.models import OozieDesign
from liboozie import oozie_api
from liboozie.conf import OOZIE_URL
from liboozie.oozie_api_test import OozieServerProvider
from liboozie.types import WorkflowList, Workflow as OozieWorkflow, Coordinator as OozieCoordinator,\
  CoordinatorList, WorkflowAction

from oozie.models import Workflow, Node, Kill, Link, Job, Coordinator, History,\
  find_parameters, NODE_TYPES
from oozie.conf import SHARE_JOBS
from oozie.utils import workflow_to_dict, model_to_dict
from oozie.import_workflow import import_workflow


LOG = logging.getLogger(__name__)


_INITIALIZED = False


class MockOozieApi:
  JSON_WORKFLOW_LIST = [{u'status': u'RUNNING', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:35:48 GMT', u'appName': u'WordCount1', u'lastModTime': u'Mon, 30 Jul 2012 22:37:00 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': 'job_201208072118_0044', u'consoleUrl': u'http://runreal:11000/oozie?job=0000012-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:35:48 GMT', u'toString': u'Workflow id[0000012-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:37:00 GMT', u'id': u'0000012-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'},
                        {u'status': u'KILLED', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:31:08 GMT', u'appName': u'WordCount2', u'lastModTime': u'Mon, 30 Jul 2012 22:32:20 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': '-', u'consoleUrl': u'http://runreal:11000/oozie?job=0000011-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:31:08 GMT', u'toString': u'Workflow id[0000011-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:32:20 GMT', u'id': u'0000011-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'},
                        {u'status': u'SUCCEEDED', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:20:48 GMT', u'appName': u'WordCount3', u'lastModTime': u'Mon, 30 Jul 2012 22:22:00 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': '', u'consoleUrl': u'http://runreal:11000/oozie?job=0000009-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:20:48 GMT', u'toString': u'Workflow id[0000009-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:22:00 GMT', u'id': u'0000009-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'},
                        {u'status': u'SUCCEEDED', u'run': 0, u'startTime': u'Mon, 30 Jul 2012 22:16:58 GMT', u'appName': u'WordCount4', u'lastModTime': u'Mon, 30 Jul 2012 22:18:10 GMT', u'actions': [], u'acl': None, u'appPath': None, u'externalId': None, u'consoleUrl': u'http://runreal:11000/oozie?job=0000008-120725142744176-oozie-oozi-W', u'conf': None, u'parentId': None, u'createdTime': u'Mon, 30 Jul 2012 22:16:58 GMT', u'toString': u'Workflow id[0000008-120725142744176-oozie-oozi-W] status[SUCCEEDED]', u'endTime': u'Mon, 30 Jul 2012 22:18:10 GMT', u'id': u'0000008-120725142744176-oozie-oozi-W', u'group': None, u'user': u'test'}]
  WORKFLOW_IDS = [wf['id'] for wf in JSON_WORKFLOW_LIST]
  WORKFLOW_DICT = dict([(wf['id'], wf) for wf in JSON_WORKFLOW_LIST])

  JSON_COORDINATOR_LIST = [{u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[0000041-120717205528122-oozie-oozi-C] status[RUNNING]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'RUNNING', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/test/demo2', u'timeUnit': u'DAY', u'coordJobId': u'0000041-120717205528122-oozie-oozi-C', u'coordJobName': u'DailyWordCount1', u'nextMaterializedTime': u'Wed, 04 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Wed, 04 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 00:00:00 GMT'},
                           {u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[0000011-120706144403213-oozie-oozi-C] status[DONEWITHERROR]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'DONEWITHERROR', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/hue/jobsub/_romain_-design-2', u'timeUnit': u'DAY', u'coordJobId': u'0000011-120706144403213-oozie-oozi-C', u'coordJobName': u'DailyWordCount2', u'nextMaterializedTime': u'Thu, 05 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Thu, 05 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 18:54:00 GMT'},
                           {u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[0000010-120706144403213-oozie-oozi-C] status[DONEWITHERROR]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'DONEWITHERROR', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/hue/jobsub/_romain_-design-2', u'timeUnit': u'DAY', u'coordJobId': u'0000010-120706144403213-oozie-oozi-C', u'coordJobName': u'DailyWordCount3', u'nextMaterializedTime': u'Thu, 05 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Thu, 05 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 18:54:00 GMT'},
                           {u'startTime': u'Sun, 01 Jul 2012 00:00:00 GMT', u'actions': [], u'frequency': 1, u'concurrency': 1, u'pauseTime': None, u'group': None, u'toString': u'Coornidator application id[0000009-120706144403213-oozie-oozi-C] status[DONEWITHERROR]', u'consoleUrl': None, u'mat_throttling': 0, u'status': u'DONEWITHERROR', u'conf': None, u'user': u'test', u'timeOut': 120, u'coordJobPath': u'hdfs://localhost:8020/user/hue/jobsub/_romain_-design-2', u'timeUnit': u'DAY', u'coordJobId': u'0000009-120706144403213-oozie-oozi-C', u'coordJobName': u'DailyWordCount4', u'nextMaterializedTime': u'Thu, 05 Jul 2012 00:00:00 GMT', u'coordExternalId': None, u'acl': None, u'lastAction': u'Thu, 05 Jul 2012 00:00:00 GMT', u'executionPolicy': u'FIFO', u'timeZone': u'America/Los_Angeles', u'endTime': u'Wed, 04 Jul 2012 18:54:00 GMT'}]
  COORDINATOR_IDS = [coord['coordJobId'] for coord in JSON_COORDINATOR_LIST]
  COORDINATOR_DICT = dict([(coord['coordJobId'], coord) for coord in JSON_COORDINATOR_LIST])

  WORKFLOW_ACTION = {u'status': u'OK', u'retries': 0, u'transition': u'end', u'stats': None, u'startTime': u'Fri, 10 Aug 2012 05:24:21 GMT', u'toString': u'Action name[WordCount] status[OK]', u'cred': u'null', u'errorMessage': None, u'errorCode': None, u'consoleUrl': u'http://localhost:50030/jobdetails.jsp?jobid=job_201208072118_0044', u'externalId': u'job_201208072118_0044', u'externalStatus': u'SUCCEEDED', u'conf': u'<map-reduce xmlns="uri:oozie:workflow:0.2">\r\n  <job-tracker>localhost:8021</job-tracker>\r\n  <name-node>hdfs://localhost:8020</name-node>\r\n  <configuration>\r\n    <property>\r\n      <name>mapred.mapper.regex</name>\r\n      <value>dream</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.input.dir</name>\r\n      <value>/user/test/words/20120702</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.output.dir</name>\r\n      <value>/user/test/out/rrwords/20120702</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.mapper.class</name>\r\n      <value>org.apache.hadoop.mapred.lib.RegexMapper</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.combiner.class</name>\r\n      <value>org.apache.hadoop.mapred.lib.LongSumReducer</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.reducer.class</name>\r\n      <value>org.apache.hadoop.mapred.lib.LongSumReducer</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.output.key.class</name>\r\n      <value>org.apache.hadoop.io.Text</value>\r\n    </property>\r\n    <property>\r\n      <name>mapred.output.value.class</name>\r\n      <value>org.apache.hadoop.io.LongWritable</value>\r\n    </property>\r\n  </configuration>\r\n</map-reduce>', u'type': u'map-reduce', u'trackerUri': u'localhost:8021', u'externalChildIDs': None, u'endTime': u'Fri, 10 Aug 2012 05:24:38 GMT', u'data': None, u'id': u'0000012-120725142744176-oozie-oozi-W@WordCount', u'name': u'WordCount'}

  def __init__(self, *args, **kwargs):
    pass

  def setuser(self, user):
    pass

  def submit_job(self, properties):
    return 'ONE-OOZIE-ID-W'

  def get_workflows(self, **kwargs):
    workflows = MockOozieApi.JSON_WORKFLOW_LIST
    if 'user' in kwargs:
      workflows = filter(lambda wf: wf['user'] == kwargs['user'], workflows)

    return WorkflowList(self, {'offset': 0, 'total': 4, 'workflows': workflows})

  def get_coordinators(self, **kwargs):
    coordinatorjobs = MockOozieApi.JSON_COORDINATOR_LIST
    if 'user' in kwargs:
      coordinatorjobs = filter(lambda coord: coord['user'] == kwargs['user'], coordinatorjobs)

    return CoordinatorList(self, {'offset': 0, 'total': 5, 'coordinatorjobs': coordinatorjobs})

  def get_job(self, job_id):
    if job_id in MockOozieApi.WORKFLOW_DICT:
      return OozieWorkflow(self, MockOozieApi.WORKFLOW_DICT[job_id])
    else:
      return OozieWorkflow(self, {'id': job_id, 'actions': []})

  def get_coordinator(self, job_id):
    if job_id in MockOozieApi.COORDINATOR_DICT:
      return OozieCoordinator(self, MockOozieApi.COORDINATOR_DICT[job_id])
    else:
      return OozieCoordinator(self, {'id': job_id, 'actions': []})

  def get_action(self, action_id):
    return WorkflowAction(MockOozieApi.WORKFLOW_ACTION)

  def job_control(self, job_id, action):
    return 'Done'

  def get_job_definition(self, jobid):
    return '<xml></xml>'

  def get_job_log(self, jobid):
    return '<xml></xml>'


class OozieMockBase(object):

  def setUp(self):
    # Beware: Monkey patch Oozie/LibOozie with Mock API
    if not hasattr(oozie_api, 'OriginalOozieApi'):
      oozie_api.OriginalOozieApi = oozie_api.OozieApi
    if not hasattr(Workflow.objects, 'original_check_workspace'):
      Workflow.objects.original_check_workspace = Workflow.objects.check_workspace
    Workflow.objects.check_workspace = lambda a, b: None
    oozie_api.OozieApi = MockOozieApi
    oozie_api._api_cache = None

    Coordinator.objects.all().delete()

    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "oozie")
    self.user = User.objects.get(username='test')
    self.wf = create_workflow(self.c)


  def tearDown(self):
    oozie_api.OozieApi = oozie_api.OriginalOozieApi
    Workflow.objects.check_workspace = Workflow.objects.original_check_workspace
    oozie_api._api_cache = None


  def setup_simple_workflow(self):
    """ Creates a linear workflow """
    Link.objects.filter(parent__workflow=self.wf).delete()
    Link(parent=self.wf.start, child=self.wf.end, name="related").save()

    action1 = add_node(self.wf, 'action-name-1', 'mapreduce', [self.wf.start], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    action2 = add_node(self.wf, 'action-name-2', 'mapreduce', [action1], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    action3 = add_node(self.wf, 'action-name-3', 'mapreduce', [action2], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })

    Link(parent=action3, child=self.wf.end, name="ok").save()


  def setup_forking_workflow(self):
    """ Creates a workflow with a fork """
    Link.objects.filter(parent__workflow=self.wf).delete()
    Link(parent=self.wf.start, child=self.wf.end, name="related").save()
    fork1 = add_node(self.wf, 'fork-name-1', 'fork', [self.wf.start])
    action1 = add_node(self.wf, 'action-name-1', 'mapreduce', [fork1])
    action2 = add_node(self.wf, 'action-name-2', 'mapreduce', [fork1])
    join1 = add_node(self.wf, 'join-name-1', 'join', [action1, action2])
    Link(parent=fork1, child=join1, name="related").save()
    action3 = add_node(self.wf, 'action-name-3', 'mapreduce', [join1])
    Link(parent=action3, child=self.wf.end, name="ok").save()


class OozieBase(OozieServerProvider):
  requires_hadoop = True

  def setUp(self):
    OozieServerProvider.setup_class()
    self.c = make_logged_in_client(is_superuser=False)
    self.user = User.objects.get(username="test")
    grant_access("test", "test", "oozie")
    self.cluster = OozieServerProvider.cluster
    self.install_examples()

    # Ensure access to MR folder
    self.cluster.fs.do_as_superuser(self.cluster.fs.chmod, '/tmp', 0777, recursive=True)


  def install_examples(self):
    global _INITIALIZED
    if _INITIALIZED:
      return

    self.c.post(reverse('oozie:setup_app'))
    self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')
    self.cluster.fs.do_as_superuser(self.cluster.fs.chmod, '/user/test', 0777, True)
    hue = User.objects.create_user('hue', 'hue' + '@localhost', 'hue')
    Workflow.objects.update(owner=hue)

    _INITIALIZED = True


  def setup_simple_workflow(self):
    """ Creates a linear workflow """
    Link.objects.filter(parent__workflow=self.wf).delete()
    Link(parent=self.wf.start, child=self.wf.end, name="related").save()
    action1 = add_node(self.wf, 'action-name-1', 'mapreduce', [self.wf.start], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    action2 = add_node(self.wf, 'action-name-2', 'mapreduce', [action1], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    action3 = add_node(self.wf, 'action-name-3', 'mapreduce', [action2], {
      'description': '',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name":"sleep","value":"${SLEEP}"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    Link(parent=action3, child=self.wf.end, name="ok").save()


  def setup_forking_workflow(self):
    """ Creates a workflow with a fork """
    Link.objects.filter(parent__workflow=self.wf).delete()
    Link(parent=self.wf.start, child=self.wf.end, name="related").save()
    fork1 = add_node(self.wf, 'fork-name-1', 'fork', [self.wf.start])
    action1 = add_node(self.wf, 'action-name-1', 'mapreduce', [fork1])
    action2 = add_node(self.wf, 'action-name-2', 'mapreduce', [fork1])
    join1 = add_node(self.wf, 'join-name-1', 'join', [action1, action2])
    Link(parent=fork1, child=join1, name="related").save()
    action3 = add_node(self.wf, 'action-name-3', 'mapreduce', [join1])
    Link(parent=action3, child=self.wf.end, name="ok").save()


class TestAPI(OozieMockBase):

  def setUp(self):
    OozieMockBase.setUp(self)

    # When updating wf, update wf_json as well!
    self.wf = Workflow.objects.get(name='wf-name-1')

  def test_workflow_save(self):
    self.setup_simple_workflow()

    workflow_dict = workflow_to_dict(self.wf)
    workflow_dict = remove_related_fields( workflow_dict )
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json})
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(0, test_response_json_object['status'])

    # Change property and save
    workflow_dict = workflow_to_dict(self.wf)
    workflow_dict = remove_related_fields( workflow_dict )
    workflow_dict['description'] = 'test'
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json})
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(0, test_response_json_object['status'])

    wf = Workflow.objects.get(id=self.wf.id)
    assert_equal('test', wf.description)
    assert_equal(self.wf.name, wf.name)

    # Change node and save
    workflow_dict = workflow_to_dict(self.wf)
    workflow_dict = remove_related_fields( workflow_dict )
    workflow_dict['nodes'][2]['name'] = 'new-name'
    node_id = workflow_dict['nodes'][2]['id']
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json})
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(0, test_response_json_object['status'])

    node = Node.objects.get(id=node_id)
    assert_equal('new-name', node.name)

  def test_workflow_save_fail(self):
    self.setup_simple_workflow()

    # Bad workflow name
    workflow_dict = workflow_to_dict(self.wf)
    del workflow_dict['name']
    workflow_dict = remove_related_fields( workflow_dict )
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(400, response.status_code)

    # Bad node name
    workflow_dict = workflow_to_dict(self.wf)
    del workflow_dict['nodes'][2]['name']
    workflow_dict = remove_related_fields( workflow_dict )
    workflow_json = json.dumps(workflow_dict)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(400, response.status_code)

  def test_workflow(self):
    response = self.c.get(reverse('oozie:workflow', kwargs={'workflow': self.wf.pk}))
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)

    assert_equal(0, test_response_json_object['status'])


class TestApiPermissionsWithOozie(OozieBase):

  def setUp(self):
    OozieBase.setUp(self)

    # When updating wf, update wf_json as well!
    self.wf = Workflow.objects.get(name='MapReduce').clone(self.cluster.fs, self.user)

  def test_workflow_save(self):
    # Share
    self.wf.is_shared = True
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    workflow_dict = workflow_to_dict(self.wf)
    workflow_dict = remove_related_fields(workflow_dict)
    workflow_json = json.dumps(workflow_dict)

    response = client_not_me.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(401, response.status_code, response.status_code)

    response = self.c.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(200, response.status_code, response)
    assert_equal(0, test_response_json_object['status'])

  def test_workflow_save_fail(self):
    # Unshare
    self.wf.is_shared = False
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    workflow_dict = workflow_to_dict(self.wf)
    del workflow_dict['name']
    workflow_dict = remove_related_fields( workflow_dict )
    workflow_json = json.dumps(workflow_dict)

    response = client_not_me.post(reverse('oozie:workflow_save', kwargs={'workflow': self.wf.pk}), data={'workflow': workflow_json}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(401, response.status_code, response)

  def test_workflow(self):
    # Share
    self.wf.is_shared = True
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    response = client_not_me.get(reverse('oozie:workflow', kwargs={'workflow': self.wf.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    test_response_json = response.content
    test_response_json_object = json.loads(test_response_json)
    assert_equal(200, response.status_code, response)
    assert_equal(0, test_response_json_object['status'])

  def test_workflow_fail(self):
    # Unshare
    self.wf.is_shared = False
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    response = client_not_me.get(reverse('oozie:workflow', kwargs={'workflow': self.wf.pk}), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(401, response.status_code)



class TestEditor(OozieMockBase):

  def setUp(self):
    super(TestEditor, self).setUp()
    self.setup_simple_workflow()


  def test_find_parameters(self):
    jobs = [Job(name="$a"),
            Job(name="foo ${b} $$"),
            Job(name="${foo}", description="xxx ${foo}")]

    result = [find_parameters(job, ['name', 'description']) for job in jobs]
    assert_equal(set(["b", "foo"]), reduce(lambda x, y: x | set(y), result, set()))


  def test_find_all_parameters(self):
    assert_equal([{'name': u'output', 'value': u''}, {'name': u'SLEEP', 'value': ''}, {'name': u'market', 'value': u'US'}],
                 self.wf.find_all_parameters())


  def test_workflow_has_cycle(self):
    action1 = Node.objects.get(name='action-name-1')
    action3 = Node.objects.get(name='action-name-3')

    assert_false(self.wf.has_cycle())

    ok = action3.get_link('ok')
    ok.child = action1
    ok.save()

    assert_true(self.wf.has_cycle())


  def test_workflow_gen_xml(self):
    assert_equal(
        '<workflow-app name="wf-name-1" xmlns="uri:oozie:workflow:0.2">\n'
        '    <global>\n'
        '        <job-xml>jobconf.xml</job-xml>\n'
        '        <configuration>\n'
        '            <property>\n'
        '                <name>sleep-all</name>\n'
        '                <value>${SLEEP}</value>\n'
        '            </property>\n'
        '         </configuration>\n'
        '    </global>\n'
        '    <start to="action-name-1"/>\n'
        '    <action name="action-name-1">\n'
        '        <map-reduce>\n'
        '           <job-tracker>${jobTracker}</job-tracker>\n'
        '            <name-node>${nameNode}</name-node>\n'
        '            <prepare>\n'
        '                <delete path="${nameNode}${output}"/>\n'
        '                <mkdir path="${nameNode}/test"/>\n'
        '            </prepare>\n'
        '            <configuration>\n'
        '                <property>\n'
        '                    <name>sleep</name>\n'
        '                    <value>${SLEEP}</value>\n'
        '                </property>\n'
        '            </configuration>\n'
        '        </map-reduce>\n'
        '        <ok to="action-name-2"/>\n'
        '        <error to="kill"/>\n'
        '    </action>\n'
        '    <action name="action-name-2">\n'
        '        <map-reduce>\n'
        '            <job-tracker>${jobTracker}</job-tracker>\n'
        '            <name-node>${nameNode}</name-node>\n'
        '            <prepare>\n'
        '                <delete path="${nameNode}${output}"/>\n'
        '                <mkdir path="${nameNode}/test"/>\n'
        '            </prepare>\n'
        '            <configuration>\n'
        '                <property>\n'
        '                    <name>sleep</name>\n'
        '                    <value>${SLEEP}</value>\n'
        '                </property>\n'
        '            </configuration>\n'
        '        </map-reduce>\n'
        '        <ok to="action-name-3"/>\n'
        '        <error to="kill"/>\n'
        '    </action>\n'
        '    <action name="action-name-3">\n'
        '        <map-reduce>\n'
        '            <job-tracker>${jobTracker}</job-tracker>\n'
        '            <name-node>${nameNode}</name-node>\n'
        '            <prepare>\n'
        '                <delete path="${nameNode}${output}"/>\n'
        '                <mkdir path="${nameNode}/test"/>\n'
        '            </prepare>\n'
        '            <configuration>\n'
        '                <property>\n'
        '                    <name>sleep</name>\n'
        '                    <value>${SLEEP}</value>\n'
        '                </property>\n'
        '            </configuration>\n'
        '        </map-reduce>\n'
        '        <ok to="end"/>\n'
        '        <error to="kill"/>\n'
        '    </action>\n'
        '    <kill name="kill">\n'
        '        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>\n'
        '    </kill>\n'
        '    <end name="end"/>\n'
        '</workflow-app>'.split(), self.wf.to_xml().split())

  def test_workflow_shell_gen_xml(self):
    self.wf.node_set.filter(name='action-name-1').delete()

    action1 = add_node(self.wf, 'action-name-1', 'shell', [self.wf.start], {
        u'job_xml': 'my-job.xml',
        u'files': '["hello.py"]',
        u'name': 'Shell',
        u'job_properties': '[]',
        u'capture_output': 'on',
        u'command': 'hello.py',
        u'archives': '[]',
        u'prepares': '[]',
        u'params': '[{"value":"World!","type":"argument"}]',
        u'description': 'Execute a Python script printing its arguments'
    })
    Link(parent=action1, child=self.wf.end, name="ok").save()

    xml = self.wf.to_xml()

    assert_true("""
        <shell xmlns="uri:oozie:shell-action:0.1">
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
              <job-xml>my-job.xml</job-xml>
            <exec>hello.py</exec>
              <argument>World!</argument>
            <file>hello.py#hello.py</file>
              <capture-output/>
        </shell>""" in xml, xml)

    action1.capture_output = False
    action1.save()

    xml = self.wf.to_xml()

    assert_true("""
        <shell xmlns="uri:oozie:shell-action:0.1">
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
              <job-xml>my-job.xml</job-xml>
            <exec>hello.py</exec>
              <argument>World!</argument>
            <file>hello.py#hello.py</file>
        </shell>""" in xml, xml)


  def test_workflow_flatten_list(self):
    assert_equal('[<Start: start>, <Mapreduce: action-name-1>, <Mapreduce: action-name-2>, <Mapreduce: action-name-3>, '
                 '<Kill: kill>, <End: end>]',
                 str(self.wf.node_list))

    # 1 2
    #  3
    self.setup_forking_workflow()

    assert_equal('[<Start: start>, <Fork: fork-name-1>, <Mapreduce: action-name-1>, <Mapreduce: action-name-2>, '
                 '<Join: join-name-1>, <Mapreduce: action-name-3>, <Kill: kill>, <End: end>]',
                 str(self.wf.node_list))


  def test_create_coordinator(self):
    create_coordinator(self.wf, self.c)


  def test_clone_coordinator(self):
    coord = create_coordinator(self.wf, self.c)
    coordinator_count = Coordinator.objects.count()

    response = self.c.post(reverse('oozie:clone_coordinator', args=[coord.id]), {}, follow=True)

    coord2 = Coordinator.objects.latest('id')
    assert_not_equal(coord.id, coord2.id)
    assert_equal(coordinator_count + 1, Coordinator.objects.count(), response)

    assert_equal(coord.dataset_set.count(), coord2.dataset_set.count())
    assert_equal(coord.datainput_set.count(), coord2.datainput_set.count())
    assert_equal(coord.dataoutput_set.count(), coord2.dataoutput_set.count())

    ds_ids = set(coord.dataset_set.values_list('id', flat=True))
    for node in coord2.dataset_set.all():
      assert_false(node.id in ds_ids)

    data_input_ids = set(coord.datainput_set.values_list('id', flat=True))
    for node in coord2.datainput_set.all():
      assert_false(node.id in data_input_ids)

    data_output_ids = set(coord.dataoutput_set.values_list('id', flat=True))
    for node in coord2.dataoutput_set.all():
      assert_false(node.id in data_output_ids)

    assert_not_equal(coord.deployment_dir, coord2.deployment_dir)
    assert_not_equal('', coord2.deployment_dir)


  def test_coordinator_workflow_access_permissions(self):
    self.wf.is_shared = True
    self.wf.save()

    # Login as someone else not superuser
    client_another_me = make_logged_in_client(username='another_me', is_superuser=False, groupname='test')
    grant_access("another_me", "test", "oozie")
    coord = create_coordinator(self.wf, client_another_me)

    response = client_another_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
    assert_true('Editor' in response.content, response.content)
    assert_true('value="Save"' in response.content, response.content)

    # Check can schedule a non personal/shared workflow
    workflow_select = '%s</option>' % self.wf
    response = client_another_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
    assert_true(workflow_select in response.content, response.content)

    self.wf.is_shared = False
    self.wf.save()

    response = client_another_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
    assert_false(workflow_select in response.content, response.content)

    self.wf.is_shared = True
    self.wf.save()

    # Edit
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_another_me.post(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_true(workflow_select in response.content, response.content)
      assert_true('value="Save"' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_another_me.post(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_true('This field is required' in response.content, response.content)
      assert_false(workflow_select in response.content, response.content)
      assert_true('value="Save"' in response.content, response.content)
    finally:
      finish()


  def test_coordinator_gen_xml(self):
    coord = create_coordinator(self.wf, self.c)

    assert_equal(
        '<coordinator-app name="MyCoord"\n'
        '  frequency="${coord:days(1)}"\n'
        '  start="2012-07-01T00:00Z" end="2012-07-04T00:00Z" timezone="America/Los_Angeles"\n'
        '  xmlns="uri:oozie:coordinator:0.1">\n'
        '  <controls>\n'
        '    <timeout>100</timeout>\n'
        '    <concurrency>3</concurrency>\n'
        '    <execution>FIFO</execution>\n'
        '    <throttle>10</throttle>\n'
        '  </controls>\n'
        '  <action>\n'
        '    <workflow>\n'
        '      <app-path>${wf_application_path}</app-path>\n'
        '   </workflow>\n'
        '  </action>\n'
        '</coordinator-app>\n'.split(), coord.to_xml().split())


  def test_coordinator_with_data_input_gen_xml(self):
    coord = create_coordinator(self.wf, self.c)
    create_dataset(coord, self.c)
    create_coordinator_data(coord, self.c)

    assert_equal(
        ['<coordinator-app', 'name="MyCoord"', 'frequency="${coord:days(1)}"', 'start="2012-07-01T00:00Z"', 'end="2012-07-04T00:00Z"',
         'timezone="America/Los_Angeles"',
         'xmlns="uri:oozie:coordinator:0.1">',
         '<controls>',
         '<timeout>100</timeout>',
         '<concurrency>3</concurrency>',
         '<execution>FIFO</execution>',
         '<throttle>10</throttle>',
         '</controls>',
         '<datasets>',
         '<dataset', 'name="MyDataset"', 'frequency="${coord:days(1)}"', 'initial-instance="2012-07-01T00:00Z"', 'timezone="America/Los_Angeles">',
         '<uri-template>/data/${YEAR}${MONTH}${DAY}</uri-template>',
         '<done-flag></done-flag>',
         '</dataset>',
         '</datasets>',
         '<input-events>',
         '<data-in', 'name="input_dir"', 'dataset="MyDataset">',
         '<instance>${coord:current(0)}</instance>',
         '</data-in>',
         '</input-events>',
         '<action>',
         '<workflow>',
         '<app-path>${wf_application_path}</app-path>',
         '<configuration>',
         '<property>',
         '<name>input_dir</name>',
         "<value>${coord:dataIn('input_dir')}</value>",
         '</property>',
         '</configuration>',
         '</workflow>',
         '</action>',
         '</coordinator-app>'], coord.to_xml().split())


  def test_create_coordinator_dataset(self):
    coord = create_coordinator(self.wf, self.c)
    create_dataset(coord, self.c)


  def test_create_coordinator_input_data(self):
    coord = create_coordinator(self.wf, self.c)
    create_dataset(coord, self.c)

    create_coordinator_data(coord, self.c)


  def test_setup_app(self):
    self.c.post(reverse('oozie:setup_app'))


  def test_workflow_prepare(self):
    action1 = Node.objects.get(name='action-name-1').get_full_node()

    action1.prepares = json.dumps([
                           {"type": "delete","value": "${output}"},
                           {"type": "delete","value": "out"},
                           {"type": "delete","value": "/user/test/out"},
                           {"type": "delete","value": "hdfs://localhost:8020/user/test/out"}])
    action1.save()

    xml = self.wf.to_xml()

    assert_true('<delete path="${nameNode}${output}"/>' in xml, xml)
    assert_true('<delete path="${nameNode}/user/${wf:user()}/out"/>' in xml, xml)
    assert_true('<delete path="${nameNode}/user/test/out"/>' in xml, xml)
    assert_true('<delete path="hdfs://localhost:8020/user/test/out"/>' in xml, xml)


  def test_get_workflow_parameters(self):
    assert_equal([{'name': u'output', 'value': ''}, {'name': u'SLEEP', 'value': ''}, {'name': u'market', 'value': u'US'}],
                 self.wf.find_all_parameters())


  def test_get_coordinator_parameters(self):
    coord = create_coordinator(self.wf, self.c)

    create_dataset(coord, self.c)
    create_coordinator_data(coord, self.c)

    assert_equal([{'name': u'output', 'value': ''}, {'name': u'SLEEP', 'value': ''}, {'name': u'market', 'value': u'US,France'}],
                 coord.find_all_parameters())


  def test_import_workflow_basic(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/0.4/test-basic.xml')
    import_workflow(workflow, f.read(), schema_version=0.4)
    f.close()
    workflow.save()
    assert_equal(2, len(Node.objects.filter(workflow=workflow)))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal('done', Node.objects.get(workflow=workflow, node_type='end').name)
    workflow.delete()


  def test_import_workflow_decision(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/0.4/test-decision.xml')
    import_workflow(workflow, f.read(), schema_version=0.4)
    f.close()
    workflow.save()
    assert_equal(11, len(Node.objects.filter(workflow=workflow)))
    assert_equal(19, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', comment='${1 gt 2}', name='start')))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', comment='', name='start')))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', name='default')))
    assert_equal(1, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='decision', child__node_type='end', name='related')))
    workflow.delete()


  def test_import_workflow_distcp(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/0.4/test-distcp.0.1.xml')
    import_workflow(workflow, f.read(), schema_version=0.4)
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(3, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal('[{"type":"arg","value":"-overwrite"},{"type":"arg","value":"-m"},{"type":"arg","value":"${MAP_NUMBER}"},{"type":"arg","value":"/user/hue/oozie/workspaces/data"},{"type":"arg","value":"${OUTPUT}"}]', Node.objects.get(workflow=workflow, node_type='distcp').get_full_node().params)
    workflow.delete()


  def test_import_workflow_forks(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/0.4/test-forks.xml')
    import_workflow(workflow, f.read(), schema_version=0.4)
    f.close()
    workflow.save()
    assert_equal(12, len(Node.objects.filter(workflow=workflow)))
    assert_equal(19, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal(6, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='fork')))
    assert_equal(4, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='fork', name='start')))
    assert_equal(2, len(Link.objects.filter(parent__workflow=workflow, parent__node_type='fork', child__node_type='join', name='related')))
    workflow.delete()


  def test_import_workflow_mapreduce(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/0.4/test-mapreduce.xml')
    import_workflow(workflow, f.read(), schema_version=0.4)
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(3, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal('[{"name":"mapred.reduce.tasks","value":"1"},{"name":"mapred.mapper.class","value":"org.apache.hadoop.examples.SleepJob"},{"name":"mapred.reducer.class","value":"org.apache.hadoop.examples.SleepJob"},{"name":"mapred.mapoutput.key.class","value":"org.apache.hadoop.io.IntWritable"},{"name":"mapred.mapoutput.value.class","value":"org.apache.hadoop.io.NullWritable"},{"name":"mapred.output.format.class","value":"org.apache.hadoop.mapred.lib.NullOutputFormat"},{"name":"mapred.input.format.class","value":"org.apache.hadoop.examples.SleepJob$SleepInputFormat"},{"name":"mapred.partitioner.class","value":"org.apache.hadoop.examples.SleepJob"},{"name":"mapred.speculative.execution","value":"false"},{"name":"sleep.job.map.sleep.time","value":"0"},{"name":"sleep.job.reduce.sleep.time","value":"1"}]', Node.objects.get(workflow=workflow, node_type='mapreduce').get_full_node().job_properties)
    workflow.delete()


  def test_import_workflow_pig(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/0.4/test-pig.xml')
    import_workflow(workflow, f.read(), schema_version=0.4)
    f.close()
    workflow.save()
    node = Node.objects.get(workflow=workflow, node_type='pig').get_full_node()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(3, len(Link.objects.filter(parent__workflow=workflow)))
    assert_equal('aggregate.pig', node.script_path)
    assert_equal('[{"type":"argument","value":"-param"},{"type":"argument","value":"INPUT=/user/hue/oozie/workspaces/data"},{"type":"argument","value":"-param"},{"type":"argument","value":"OUTPUT=${output}"}]', node.params)
    workflow.delete()


  def test_import_workflow_sqoop(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/0.4/test-sqoop.0.2.xml')
    import_workflow(workflow, f.read(), schema_version=0.4)
    f.close()
    workflow.save()
    assert_equal(4, len(Node.objects.filter(workflow=workflow)))
    assert_equal(3, len(Link.objects.filter(parent__workflow=workflow)))
    node = Node.objects.get(workflow=workflow, node_type='sqoop').get_full_node()
    assert_equal('["db.hsqldb.properties#db.hsqldb.properties","db.hsqldb.script#db.hsqldb.script"]', node.files)
    assert_equal('import --connect jdbc:hsqldb:file:db.hsqldb --table TT --target-dir ${output} -m 1', node.script_path)
    workflow.delete()


  def test_import_workflow_java(self):
    workflow = Workflow.objects.new_workflow(self.user)
    workflow.save()
    f = open('apps/oozie/src/oozie/test_data/0.4/test-java.xml')
    import_workflow(workflow, f.read(), schema_version=0.4)
    f.close()
    workflow.save()
    assert_equal(5, len(Node.objects.filter(workflow=workflow)))
    assert_equal(5, len(Link.objects.filter(parent__workflow=workflow)))
    nodes = [Node.objects.filter(workflow=workflow, node_type='java')[0].get_full_node(),
             Node.objects.filter(workflow=workflow, node_type='java')[1].get_full_node()]
    assert_equal('org.apache.hadoop.examples.terasort.TeraGen', nodes[0].main_class)
    assert_equal('["${records}","${output_dir}/teragen"]', nodes[0].args)
    assert_equal('org.apache.hadoop.examples.terasort.TeraSort', nodes[1].main_class)
    assert_equal('["${output_dir}/teragen","${output_dir}/terasort"]', nodes[1].args)
    workflow.delete()


class TestPermissions(OozieBase):

  def setUp(self):
    self.c = make_logged_in_client()
    self.wf = create_workflow(self.c)
    self.setup_simple_workflow()


  def test_workflow_permissions(self):
    response = self.c.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
    assert_true('Editor' in response.content, response.content)
    assert_true('Save' in response.content, response.content)
    assert_false(self.wf.is_shared)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_workflows'))
      assert_false('wf-name-1' in response.content, response.content)
    finally:
      finish()
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:list_workflows'))
      assert_false('wf-name-1' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    # Share it !
    self.wf = Workflow.objects.get(name='wf-name-1')
    self.wf.is_shared = True
    self.wf.save()
    Workflow.objects.check_workspace(self.wf, self.cluster.fs)

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_workflows'))
      assert_equal(200, response.status_code)
      assert_true('wf-name-1' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
      assert_false('Permission denied' in response.content, response.content)
      assert_true('Save' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_workflow', args=[self.wf.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    # Submit
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:submit_workflow', args=[self.wf.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(True)
    try:
      try:
        response = client_not_me.post(reverse('oozie:submit_workflow', args=[self.wf.id]))
        assert_false('Permission denied' in response.content, response.content)
      except IOError:
        pass
    finally:
      finish()

    # Delete
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:delete_workflow', args=[self.wf.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    response = self.c.post(reverse('oozie:delete_workflow', args=[self.wf.id]), follow=True)
    assert_equal(200, response.status_code)


  def test_coordinator_permissions(self):
    coord = create_coordinator(self.wf, self.c)

    response = self.c.get(reverse('oozie:edit_coordinator', args=[coord.id]))
    assert_true('Editor' in response.content, response.content)
    assert_true('value="Save"' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "oozie")

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_coordinators'))
      assert_false('MyCoord' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:list_coordinators'))
      assert_false('MyCoord' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_false('MyCoord' in response.content, response.content)
    finally:
      finish()

    # Share it !
    wf = Workflow.objects.get(id=coord.workflow.id)
    wf.is_shared = True
    wf.save()
    Workflow.objects.check_workspace(wf, self.cluster.fs)

    post = COORDINATOR_DICT.copy()
    post.update({
                 u'datainput_set-TOTAL_FORMS': [u'0'], u'datainput_set-INITIAL_FORMS': [u'0'], u'dataset_set-INITIAL_FORMS': [u'0'],
                 u'dataoutput_set-INITIAL_FORMS': [u'0'], u'datainput_set-MAX_NUM_FORMS': [u'0'], u'output-MAX_NUM_FORMS': [u''],
                 u'output-INITIAL_FORMS': [u'0'], u'dataoutput_set-TOTAL_FORMS': [u'0'], u'input-TOTAL_FORMS': [u'0'],
                 u'dataset_set-MAX_NUM_FORMS': [u'0'], u'dataoutput_set-MAX_NUM_FORMS': [u'0'], u'input-MAX_NUM_FORMS': [u''],
                 u'dataset_set-TOTAL_FORMS': [u'0'], u'input-INITIAL_FORMS': [u'0'], u'output-TOTAL_FORMS': [u'0']})

    post['is_shared'] = [u'on']
    post['workflow'] = coord.workflow.id
    self.c.post(reverse('oozie:edit_coordinator', args=[coord.id]), post)
    coord = Coordinator.objects.get(id=coord.id)
    assert_true(coord.is_shared)

    # List
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:list_coordinators'))
      assert_equal(200, response.status_code)
      assert_true('MyCoord' in response.content, response.content)
    finally:
      finish()

    # View
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_false('Permission denied' in response.content, response.content)
      assert_false('value="Save"' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    # Edit
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.post(reverse('oozie:edit_coordinator', args=[coord.id]))
      assert_false('MyCoord' in response.content, response.content)
      assert_true('Not allowed' in response.content, response.content)
    finally:
      finish()

    # Submit
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:submit_coordinator', args=[coord.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(True)
    try:
      try:
        response = client_not_me.post(reverse('oozie:submit_coordinator', args=[coord.id]))
        assert_false('Permission denied' in response.content, response.content)
      except IOError:
        pass
    finally:
      finish()

    # Resubmit
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      history, created = History.objects.get_or_create(job=coord, oozie_job_id=MockOozieApi.COORDINATOR_IDS[0],
                                                       defaults={'submitter': User.objects.get(username='test'), 'properties': '[]'})
      oozie_job_id = history.oozie_job_id
      response = client_not_me.post(reverse('oozie:resubmit_coordinator', args=[oozie_job_id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(True)
    try:
      try:
        history, created = History.objects.get_or_create(job=coord, oozie_job_id=MockOozieApi.COORDINATOR_IDS[0],
                                                         defaults={'submitter': User.objects.get(username='test'), 'properties': '[]'})
        oozie_job_id = history.oozie_job_id
        response = client_not_me.post(reverse('oozie:resubmit_coordinator', args=[oozie_job_id]))
        assert_false('Permission denied' in response.content, response.content)
      except IOError:
        pass
    finally:
      finish()

    # Delete
    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post(reverse('oozie:delete_coordinator', args=[coord.id]))
      assert_true('Permission denied' in response.content, response.content)
    finally:
      finish()

    response = self.c.post(reverse('oozie:delete_coordinator', args=[coord.id]), follow=True)
    assert_equal(200, response.status_code)


class TestEditorWithOozie(OozieBase):

  def setUp(self):
    self.c = make_logged_in_client()
    self.wf = create_workflow(self.c)
    self.setup_simple_workflow()


  def tearDown(self):
    self.wf.delete()


  def test_create_workflow(self):
    dir_stat = self.cluster.fs.stats(self.wf.deployment_dir)
    assert_equal('test', dir_stat.user)
    assert_equal('hue', dir_stat.group)
    assert_equal('40711', '%o' % dir_stat.mode)


  def test_clone_workflow(self):
    workflow_count = Workflow.objects.count()

    response = self.c.post(reverse('oozie:clone_workflow', args=[self.wf.id]), {}, follow=True)

    assert_equal(workflow_count + 1, Workflow.objects.count(), response)

    wf2 = Workflow.objects.latest('id')
    assert_not_equal(self.wf.id, wf2.id)
    assert_equal(self.wf.node_set.count(), wf2.node_set.count())

    node_ids = set(self.wf.node_set.values_list('id', flat=True))
    for node in wf2.node_set.all():
      assert_false(node.id in node_ids)

    assert_not_equal(self.wf.deployment_dir, wf2.deployment_dir)
    assert_not_equal('', wf2.deployment_dir)


  def test_import_action(self):
    raise SkipTest

    # Setup jobsub examples
    if not jobsub_setup.Command().has_been_setup():
      jobsub_setup.Command().handle()

    # There should be 3 from examples
    jobsub_design = OozieDesign.objects.all()[0]
    node_size = len(Node.objects.all())
    kwargs = dict(workflow=self.wf.id, parent_action_id=self.wf.end.get_parents()[0].id)
    response = self.c.post(reverse('oozie:import_action', kwargs=kwargs), {'action_id': jobsub_design.id})
    assert_equal(302, response.status_code)
    assert_equal(node_size + 1, len(Node.objects.all()))

    # There should now be an imported action at the end of Node list
    # Need to test properties to make sure we got it right
    # Must also make sure that jobsub field values are translated
    translation_regex = re.compile('(?<!\$)\$(\w+)')
    node = Node.objects.all()[len(Node.objects.all())-1].get_full_node()
    for field in node.PARAM_FIELDS:
      assert_equal(translation_regex.sub(r'${\1}', getattr(jobsub_design.get_root_action(), field)), getattr(node, field))


  def test_import_workflow(self):
    workflow_count = Workflow.objects.count()

    # Create
    filename = os.path.abspath(os.path.dirname(__file__) + "/test_data/0.4/test-mapreduce.xml")
    fh = open(filename)
    response = self.c.post(reverse('oozie:import_workflow'), {
      'job_xml': [''],
      'name': ['test_workflow'],
      'parameters': ['[{"name":"oozie.use.system.libpath","value":"true"}]'],
      'deployment_dir': [''],
      'job_properties': ['[]'],
      'schema_version': ['0.4'],
      'definition_file': [fh],
      'description': ['']
    }, follow=True)
    fh.close()
    assert_equal(workflow_count + 1, Workflow.objects.count(), response)


class TestOozieSubmissions(OozieBase):

  def test_submit_mapreduce_action(self):
    wf = Workflow.objects.get(name='MapReduce')
    post_data = {u'form-MAX_NUM_FORMS': [u''], u'form-INITIAL_FORMS': [u'1'],
                 u'form-0-name': [u'REDUCER_SLEEP_TIME'], u'form-0-value': [u'1'], u'form-TOTAL_FORMS': [u'1']}

    response = self.c.post(reverse('oozie:submit_workflow', args=[wf.id]), data=post_data, follow=True)
    job = OozieServerProvider.wait_until_completion(response.context['oozie_workflow'].id)
    assert_equal('SUCCEEDED', job.status)

    # Rerun with default options
    post_data.update({u'rerun_form_choice': [u'skip_nodes']})

    response = self.c.post(reverse('oozie:rerun_oozie_job', kwargs={'job_id': job.id, 'app_path': job.appPath}), data=post_data, follow=True)
    job = OozieServerProvider.wait_until_completion(response.context['oozie_workflow'].id)
    assert_equal('SUCCEEDED', job.status)

    # Rerun with skip OK actions skipped
    post_data.update({u'rerun_form_choice': [u'skip_nodes'], u'skip_nodes': [u'Sleep']})

    response = self.c.post(reverse('oozie:rerun_oozie_job', kwargs={'job_id': job.id, 'app_path': job.appPath}), data=post_data, follow=True)
    job = OozieServerProvider.wait_until_completion(response.context['oozie_workflow'].id)
    assert_equal('SUCCEEDED', job.status)

    # Rerun with failed nodes too
    post_data.update({u'rerun_form_choice': [u'failed_nodes']})

    response = self.c.post(reverse('oozie:rerun_oozie_job', kwargs={'job_id': job.id, 'app_path': job.appPath}), data=post_data, follow=True)
    job = OozieServerProvider.wait_until_completion(response.context['oozie_workflow'].id)


  def test_submit_java_action(self):
    wf = Workflow.objects.get(name='Sequential Java')

    response = self.c.post(reverse('oozie:submit_workflow', args=[wf.id]),
                           data={u'form-MAX_NUM_FORMS': [u''],
                                u'form-0-name': [u'records'], u'form-0-value': [u'10'],
                                u'form-1-name': [u' output_dir '], u'form-1-value': [u'${nameNode}/user/test/out/terasort'],
                                u'form-INITIAL_FORMS': [u'2'], u'form-TOTAL_FORMS': [u'2']},
                           follow=True)
    job = OozieServerProvider.wait_until_completion(response.context['oozie_workflow'].id)
    assert_equal('SUCCEEDED', job.status)


  def test_submit_distcp_action(self):
    wf = Workflow.objects.get(name='DistCp')

    response = self.c.post(reverse('oozie:submit_workflow', args=[wf.id]),
                           data={u'form-MAX_NUM_FORMS': [u''],
                                u'form-0-name': [u'MAP_NUMBER'], u'form-0-value': [u'5'],
                                u'form-1-name': [u'OUTPUT '], u'form-1-value': [u'${nameNode}/user/test/out/distcp'],
                                u'form-INITIAL_FORMS': [u'2'], u'form-TOTAL_FORMS': [u'2']},
                           follow=True)
    job = OozieServerProvider.wait_until_completion(response.context['oozie_workflow'].id)
    assert_equal('SUCCEEDED', job.status)


class TestDashboardNoMocking:

  def test_oozie_not_running_message(self):
    c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "oozie")

    finish = OOZIE_URL.set_for_testing('http://not_localhost:11000/bad')
    try:
      response = c.get(reverse('oozie:list_oozie_workflows'))
      assert_true('The Oozie server is not running' in response.content, response.content)
    finally:
      finish()


class TestDashboard(OozieMockBase):

  def test_manage_workflow_dashboard(self):
    # Kill button in response
    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]), {}, follow=True)
    assert_true(('%s/kill' % MockOozieApi.WORKFLOW_IDS[0]) in response.content, response.content)
    assert_false('Rerun' in response.content, response.content)

    # Rerun button in response
    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[1]]), {}, follow=True)
    assert_false(('%s/kill' % MockOozieApi.WORKFLOW_IDS[1]) in response.content, response.content)
    assert_true('Rerun' in response.content, response.content)


  def test_manage_coordinator_dashboard(self):
    # Kill button in response
    response = self.c.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[0]]), {}, follow=True)
    assert_true(('%s/kill' % MockOozieApi.COORDINATOR_IDS[0]) in response.content, response.content)
    assert_false('Rerun' in response.content, response.content)

    # Rerun button in response
    response = self.c.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[1]]), {}, follow=True)
    assert_false(('%s/kill' % MockOozieApi.COORDINATOR_IDS[1]) in response.content, response.content)
    assert_true('Resubmit' in response.content, response.content)


  def test_list_workflows(self):
    response = self.c.get(reverse('oozie:list_oozie_workflows'))
    for wf_id in MockOozieApi.WORKFLOW_IDS:
      assert_true(wf_id in response.content, response.content)


  def test_list_coordinators(self):
    response = self.c.get(reverse('oozie:list_oozie_coordinators'))
    for coord_id in MockOozieApi.COORDINATOR_IDS:
      assert_true(coord_id in response.content, response.content)


  def test_list_workflow(self):
    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]))
    assert_true('Workflow WordCount1' in response.content, response.content)
    assert_true('Workflow' in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0], MockOozieApi.COORDINATOR_IDS[0]]))
    assert_true('Workflow WordCount1' in response.content, response.content)
    assert_true('Workflow' in response.content, response.content)
    assert_true('DailyWordCount1' in response.content, response.content)
    assert_true('Coordinator' in response.content, response.content)


  def test_list_coordinator(self):
    response = self.c.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[0]]))
    assert_true('Coordinator DailyWordCount1' in response.content, response.content)
    assert_true('Workflow' in response.content, response.content)


  def test_manage_oozie_jobs(self):
    try:
      self.c.get(reverse('oozie:manage_oozie_jobs', args=[MockOozieApi.COORDINATOR_IDS[0], 'kill']))
      assert False
    except:
      pass

    response = self.c.post(reverse('oozie:manage_oozie_jobs', args=[MockOozieApi.COORDINATOR_IDS[0], 'kill']))
    data = json.loads(response.content)
    assert_equal(0, data['status'])


  def test_workflows_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_workflows'))
    assert_true('WordCount1' in response.content, response.content)

    # Rerun
    response = self.c.get(reverse('oozie:rerun_oozie_job', kwargs={'job_id': MockOozieApi.WORKFLOW_IDS[0],
                                                                   'app_path': MockOozieApi.JSON_WORKFLOW_LIST[0]['appPath']}))
    assert_false('Permission denied.' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_workflows'))
    assert_false('WordCount1' in response.content, response.content)

    # Rerun
    response = client_not_me.get(reverse('oozie:rerun_oozie_job', kwargs={'job_id': MockOozieApi.WORKFLOW_IDS[0],
                                                                          'app_path': MockOozieApi.JSON_WORKFLOW_LIST[0]['appPath']}))
    assert_true('Permission denied.' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_workflows'))
    assert_true('WordCount1' in response.content, response.content)

    # Rerun
    response = client_not_me.get(reverse('oozie:rerun_oozie_job', kwargs={'job_id': MockOozieApi.WORKFLOW_IDS[0],
                                                                          'app_path': MockOozieApi.JSON_WORKFLOW_LIST[0]['appPath']}))
    assert_false('Permission denied.' in response.content, response.content)

  def test_workflow_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]))
    assert_true('WordCount1' in response.content, response.content)
    assert_false('Permission denied' in response.content, response.content)

    response = self.c.get(reverse('oozie:list_oozie_workflow_action', args=['XXX']))
    assert_false('Permission denied' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]))
    assert_true('Permission denied' in response.content, response.content)

    response = client_not_me.get(reverse('oozie:list_oozie_workflow_action', args=['XXX']))
    assert_true('Permission denied' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_workflow', args=[MockOozieApi.WORKFLOW_IDS[0]]))
    assert_false('Permission denied' in response.content, response.content)


  def test_coordinators_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_coordinators'))
    assert_true('DailyWordCount1' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_coordinators'))
    assert_false('DailyWordCount1' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_coordinators'))
    assert_true('DailyWordCount1' in response.content, response.content)


  def test_coordinator_permissions(self):
    response = self.c.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[0]]))
    assert_true('DailyWordCount1' in response.content, response.content)
    assert_false('Permission denied' in response.content, response.content)

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test', recreate=True)
    grant_access("not_me", "not_me", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[0]]))
    assert_true('Permission denied' in response.content, response.content)

    # Add read only access
    add_permission("not_me", "dashboard_jobs_access", "dashboard_jobs_access", "oozie")

    response = client_not_me.get(reverse('oozie:list_oozie_coordinator', args=[MockOozieApi.COORDINATOR_IDS[0]]))
    assert_false('Permission denied' in response.content, response.content)


class TestUtils(OozieMockBase):

  def setUp(self):
    OozieMockBase.setUp(self)

    # When updating wf, update wf_json as well!
    self.wf = Workflow.objects.get(name='wf-name-1')


  def test_workflow_to_dict(self):
    workflow_dict = workflow_to_dict(self.wf)

    # Test properties
    assert_true('job_xml' in workflow_dict, workflow_dict)
    assert_true('is_shared' in workflow_dict, workflow_dict)
    assert_true('end' in workflow_dict, workflow_dict)
    assert_true('description' in workflow_dict, workflow_dict)
    assert_true('parameters' in workflow_dict, workflow_dict)
    assert_true('is_single' in workflow_dict, workflow_dict)
    assert_true('deployment_dir' in workflow_dict, workflow_dict)
    assert_true('schema_version' in workflow_dict, workflow_dict)
    assert_true('job_properties' in workflow_dict, workflow_dict)
    assert_true('start' in workflow_dict, workflow_dict)
    assert_true('nodes' in workflow_dict, workflow_dict)
    assert_true('id' in workflow_dict, workflow_dict)
    assert_true('name' in workflow_dict, workflow_dict)

    # Check links
    for node in workflow_dict['nodes']:
      assert_true('child_links' in node, node)

      for link in node['child_links']:
        assert_true('name' in link, link)
        assert_true('comment' in link, link)
        assert_true('parent' in link, link)
        assert_true('child' in link, link)


  def test_model_to_dict(self):
    node_dict = model_to_dict(self.wf.node_set.filter(node_type='start')[0])

    # Test properties
    assert_true('id' in node_dict)
    assert_true('name' in node_dict)
    assert_true('description' in node_dict)
    assert_true('node_type' in node_dict)
    assert_true('workflow' in node_dict)


# Utils
WORKFLOW_DICT = {u'deployment_dir': [u''], u'name': [u'wf-name-1'], u'description': [u''],
                 u'schema_version': [u'uri:oozie:workflow:0.2'],
                 u'parameters': [u'[{"name":"market","value":"US"}]'],
                 u'job_xml': [u'jobconf.xml'],
                 u'job_properties': [u'[{"name":"sleep-all","value":"${SLEEP}"}]']
}
COORDINATOR_DICT = {u'name': [u'MyCoord'], u'description': [u'Description of my coodinator'],
                    u'workflow': [u'1'],
                    u'frequency_number': [u'1'], u'frequency_unit': [u'days'],
                    u'start_0': [u'07/01/2012'], u'start_1': [u'12:00 AM'],
                    u'end_0': [u'07/04/2012'], u'end_1': [u'12:00 AM'],
                    u'timezone': [u'America/Los_Angeles'],
                    u'parameters': [u'[{"name":"market","value":"US,France"}]'],
                    u'timeout': [u'100'],
                    u'concurrency': [u'3'],
                    u'execution': [u'FIFO'],
                    u'throttle': [u'10'],
                    u'schema_version': [u'uri:oozie:coordinator:0.1']
}


def remove_related_fields(workflow_dict):
  """
  workflow_dict is a workflow that has been converted into a dictionary via workflow_to_dict
  """

  del workflow_dict['owner']
  del workflow_dict['job_ptr']
  for node in workflow_dict['nodes']:
    del node['node_ptr']
  return workflow_dict


def add_node(workflow, name, node_type, parents, attrs={}):
  """
  create a node of type node_type and associate the listed parents.
  """
  NodeClass = NODE_TYPES[node_type]
  node = NodeClass(workflow=workflow, node_type=node_type, name=name)
  for attr in attrs:
    setattr(node, attr, attrs[attr])
  node.save()

  # Add parent
  # If skipped, remember to preserve order: regular links first, then error link
  if parents:
    for parent in parents:
      name = 'ok'
      if parent.node_type == 'start' or parent.node_type == 'join':
        name = 'to'
      elif parent.node_type == 'fork' or parent.node_type == 'decision':
        name = 'start'
      link = Link(parent=parent, child=node, name=name)
      link.save()

  # Create error link
  if node_type != 'fork' and node_type != 'decision' and node_type != 'join':
    link = Link(parent=node, child=Kill.objects.get(name='kill', workflow=workflow), name="error")
  link.save()

  return node


def create_workflow(client, workflow_dict=WORKFLOW_DICT):
  name = str(workflow_dict['name'][0])

  Node.objects.filter(workflow__name=name).delete()
  Workflow.objects.filter(name=name).delete()

  workflow_count = Workflow.objects.count()
  response = client.get(reverse('oozie:create_workflow'))
  assert_equal(workflow_count, Workflow.objects.count(), response)

  response = client.post(reverse('oozie:create_workflow'), workflow_dict, follow=True)
  assert_equal(200, response.status_code)
  assert_equal(workflow_count + 1, Workflow.objects.count(), response)

  wf = Workflow.objects.get(name=name)
  assert_not_equal('', wf.deployment_dir)

  return wf


def create_coordinator(workflow, client):
  coord_count = Coordinator.objects.count()
  response = client.get(reverse('oozie:create_coordinator'))
  assert_equal(coord_count, Coordinator.objects.count(), response)

  post = COORDINATOR_DICT.copy()
  post['workflow'] = workflow.id
  response = client.post(reverse('oozie:create_coordinator'), post)
  assert_equal(coord_count + 1, Coordinator.objects.count(), response)

  return Coordinator.objects.get(name='MyCoord')


def create_dataset(coord, client):
  response = client.post(reverse('oozie:create_coordinator_dataset', args=[coord.id]), {
                        u'create-name': [u'MyDataset'], u'create-frequency_number': [u'1'], u'create-frequency_unit': [u'days'],
                        u'create-uri': [u'/data/${YEAR}${MONTH}${DAY}'],
                        u'create-start_0': [u'07/01/2012'], u'create-start_1': [u'12:00 AM'],
                        u'create-timezone': [u'America/Los_Angeles'], u'create-done_flag': [u''],
                        u'create-description': [u'']})
  data = json.loads(response.content)
  assert_equal(0, data['status'], data['data'])


def create_coordinator_data(coord, client):
  response = client.post(reverse('oozie:create_coordinator_data', args=[coord.id, 'input']),
                         {u'input-name': [u'input_dir'], u'input-dataset': [u'1']})
  data = json.loads(response.content)
  assert_equal(0, data['status'], data['data'])
