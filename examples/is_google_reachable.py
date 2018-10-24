# -*- mode:python; coding:utf-8 -*-
# Copyright (C) 2012 David Villa Alises

import hamcrest
from prego import TestCase, Task
from prego.net import Host, reachable


class GoogleTest(TestCase):
    def test_is_reachable(self):
        link = Task(desc="Is interface link up?")
        link.command('ip link | grep eth0 | grep "state UP"')

        router = Task(desc="Is the local router reachable?")
        router.command("ping -c2 $(ip route | grep ^default | cut -d' ' -f 3)")

        for line in open('/etc/resolv.conf'):
            if line.startswith('nameserver'):
                server = line.split()[1]
                test = Task(desc="Is DNS server {0} reachable?".format(server))
                test.command('ping -c 2 {0}'.format(server))

        resolve = Task(desc="may google name be resolved?")
        resolve.command('host www.google.com')

        ping = Task(desc="Is google reachable?")
        ping.command('ping -c 1 www.google.com')
        ping.assert_that(Host('www.google.com'), reachable())
        ping.assert_that(Host('www.googlewrong.com'), hamcrest.is_not(reachable()))

        web = Task(desc="get index.html")
        cmd = web.command('wget http://www.google.com/webhp?hl=en -O-')
        web.assert_that(cmd.stdout.content,
                        hamcrest.contains_string('value="I\'m Feeling Lucky"'))
