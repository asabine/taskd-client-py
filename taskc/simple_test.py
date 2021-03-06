import unittest
import os
import time
# import logging

from docker import Client

from simple import TaskdConnection


class TestRCParse(unittest.TestCase):

    def setUp(self):
        self.tc = TaskdConnection.from_taskrc("taskc/fixture/.taskrc")

    def test_rc(self):
        self.assertEqual(
            self.tc.client_cert, "/home/jack/.task/jacklaxson.cert.pem")
        self.assertEqual(
            self.tc.client_key, "/home/jack/.task/jacklaxson.key.pem")
        self.assertEqual(self.tc.cacert_file, "/home/jack/.task/ca.cert.pem")
        self.assertEqual(self.tc.server, "192.168.1.129")
        self.assertEqual(self.tc.port, 53589)
        self.assertEqual(self.tc.group, "Public")
        self.assertEqual(self.tc.username, "Jack Laxson")
        self.assertEqual(self.tc.uuid, "f60bfcb9-b7b8-4466-b4c1-7276b8afe609")


class TestConnection(unittest.TestCase):

    def setUp(self):
        # logging.basicConfig(level=logging.DEBUG)
        self.docker = Client(base_url='unix://var/run/docker.sock')
        host_config = self.docker.create_host_config(publish_all_ports=True)
        self.container = self.docker.create_container("jrabbit/taskd", name="taskc_test", host_config=host_config)
        self.docker.start(self.container["Id"])
        our_exec = self.docker.exec_create(self.container["Id"], "taskd add user Public test_user")
        self.tc = TaskdConnection()
        o = self.docker.exec_start(our_exec['Id'])
        # print o
        self.tc.uuid = o.split('\n')[0].split()[-1]
        # print self.tc.uuid
        self.tc.server = "localhost"
        c = self.docker.inspect_container("taskc_test")
        
        self.tc.port = int(c['NetworkSettings']['Ports']['53589/tcp'][0]['HostPort'])
        # self.tc.uuid = os.getenv("TEST_UUID")
        self.tc.group = "Public"
        self.tc.username = "test_user"
        self.tc.client_cert = "taskc/fixture/pki/client.cert.pem"
        self.tc.client_key = "taskc/fixture/pki/client.key.pem"
        self.tc.cacert_file = "taskc/fixture/pki/ca.cert.pem"
        time.sleep(2)
    def test_connect(self):

        self.tc._connect()
        # print self.tc.conn.getpeername()
        self.assertEqual(self.tc.conn.getpeername(), ('127.0.0.1', self.tc.port))
        # make sure we're on TLS v2 per spec
        self.assertEqual(self.tc.conn.context.protocol, 2)
        self.tc.conn.close()
        # from IPython import embed
        # embed()

    def test_put(self):
        assert self.tc.uuid
        self.tc.put("")
        tasks = """{"description":"hang up posters","entry":"20141130T081652Z","status":"pending","uuid":"0037aa92-45e5-44a6-8f34-2f92989f173a"}
{"description":"make pb ramen","entry":"20141130T081700Z","status":"pending","uuid":"dd9b71db-f51c-4026-9e46-bb099df8dd3f"}
{"description":"fold clothes","entry":"20141130T081709Z","status":"pending","uuid":"d0f53865-2f01-42a8-9f9e-3652c63f216d"}"""
        resp = self.tc.put(tasks)
        self.assertEqual(resp.status_code, 200)
        # might not be correct depends on state of taskd
    def tearDown(self):
        self.docker.remove_container(self.container['Id'], force=True)

# class TestStringIO(unittest.TestCase):
#     def setUp(self):
#         self.tc = TaskdConnection()
#         self.tc.server = "localhost"
#         self.tc.port = 53589
#         self.tc.uuid = os.getenv("TEST_UUID")
#         self.tc.group = "Public"
#         self.tc.username = "test_user"
#         self.tc.client_cert = "taskc/fixture/pki/client.cert.pem"
#         self.tc.client_key = "taskc/fixture/pki/client.key.pem"
#         self.tc.cacert_file = "taskc/fixture/pki/ca.cert.pem"

if __name__ == '__main__':
    unittest.main()
