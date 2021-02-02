# -*- coding:utf-8; tab-width:4; mode:python -*-

import hamcrest
from prego import Task, TestCase, context as ctx, running
from prego.net import localhost, listen_port
from prego.debian import Package, installed


class Net(TestCase):
    def test_netcat(self):
        ctx.port = 2000
        server = Task(desc='netcat server', detach=True)
        server.assert_that(Package('nmap'), installed())
        server.assert_that(localhost,
                           hamcrest.is_not(listen_port(ctx.port)))
        cmd = server.command('ncat -l -p $port')
        server.assert_that(cmd.stdout.content,
                           hamcrest.contains_string('bye'))

        client = Task(desc='netcat client')
        client.wait_that(server, running())
        client.wait_that(localhost, listen_port(ctx.port))
        client.command('ncat -c "echo bye" localhost $port')
