# Copyright (C) 2012 David Villa Alises

import hamcrest
from prego import TestCase, Task
from prego.net import Host, reachable
from hamcrest import is_not, contains_string


class GoogleTest(TestCase):
    def test_is_reachable(self):
        link = Task(desc="Is interface link up?")
        link.command('ip link | grep -v lo | grep "state UP"')

        router = Task(desc="Is the local router reachable?")
        router.command("ping -c2 -W2 $(ip route | grep ^default | cut -d' ' -f 3)", expected=None)

        for line in open('/etc/resolv.conf'):
            if line.startswith('nameserver'):
                server = line.split()[1]
                test = Task(desc="Is DNS server {0} reachable?".format(server))
                test.command('ping -c 2 -W2 {0}'.format(server), expected=None)

        resolve = Task(desc="may google name be resolved?")
        resolve.command('dig +short A www.google.com | sort | uniq')

        ping = Task(desc="Is google reachable?")
        ping.command('ping -c 1 www.google.com')
        ping.assert_that(Host('www.google.com'), reachable())
        ping.assert_that(Host('www.googlewrong.com'), is_not(reachable()))

        web = Task(desc="get index.html")
        cmd = web.command('curl -s --compressed http://www.google.com')
        web.assert_that(cmd.stdout.content, contains_string('<title>Google</title>'))
