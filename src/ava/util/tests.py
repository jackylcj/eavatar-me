# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

"""
Support for functional tests
"""

import os
import unittest
import gevent
import shutil
import tempfile
import pytest

from ava.core.defines import AVA_SWARM_SECRET, AVA_AGENT_SECRET
from ava.util import base_path

from gevent import monkey
monkey.patch_all(thread=False)


def prepare_agent_test_env():
    """
    Constructs the skeleton of directories if it not there already.
    :return:
    """
    pod_folder = tempfile.mkdtemp()
    os.environ.setdefault('AVA_POD', pod_folder)

    base_dir = os.path.dirname(base_path())

    src_dir = os.path.join(base_dir, 'pod')

    # copy files from base_dir to user_dir
    subdirs = os.listdir(src_dir)
    for d in subdirs:
        src_path = os.path.join(src_dir, d)
        dst_path = os.path.join(pod_folder, d)
        ignore_pattern = shutil.ignore_patterns("__init__.py")

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, ignore=ignore_pattern)
        else:
            shutil.copy2(src_path, dst_path)

    return pod_folder

user_xid = b'AYPwK3c3VK7ZdBvKfcbV5EmmCZ8zSb9viZ288gKFBFuE92jE'
user_key = b'Kd2xqKsjTnhhqXjY64eeSEyS1i9kSGTHt9S57sqeK51bkPRh'
swarm_secret = b'SVQh1mgbdvuFoZihYH8urZyBGpfZ4PJnn8af2R9MuqZyktHa'

agent_secret = b'SYNmgyQqhAnVwKLrmSmYzahkzH3V51qdShL41JFPnmsZob96'


class AgentTest(unittest.TestCase):
    """
    For functional tests which require a running agent.
    """
    agent = None
    pod_folder = None

    @classmethod
    def setUpClass(cls):
        cls.pod_folder = prepare_agent_test_env()

        from ava.runtime import settings
        from ava.core.agent import Agent

        settings['debug'] = True
        os.environ.setdefault(AVA_SWARM_SECRET, swarm_secret)
        os.environ.setdefault(AVA_AGENT_SECRET, agent_secret)
        AgentTest.agent = Agent(None, None)
        agent_greenlet = gevent.spawn(AgentTest.agent.run)
        while not AgentTest.agent.running:
            gevent.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        AgentTest.agent.interrupted = True
        while AgentTest.agent.running:
            gevent.sleep(0.5)

        shutil.rmtree(cls.pod_folder)



@pytest.fixture(scope='module')
def agent(request):
    from ava.runtime import settings
    from ava.core.agent import Agent

    settings['debug'] = True
    os.environ.setdefault(AVA_SWARM_SECRET, swarm_secret)
    os.environ.setdefault(AVA_AGENT_SECRET, agent_secret)
    agent = Agent(None, None)
    agent_greenlet = gevent.spawn(agent.run)
    while not agent.running:
        gevent.sleep(0.5)

    def teardown_agent():
        if not agent:
            return
        agent.interrupted = True
        while agent.running:
            gevent.sleep(0.5)

    request.addfinalizer(teardown_agent)
    return agent