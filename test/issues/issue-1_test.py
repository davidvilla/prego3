# -*- mode: python3; coding: utf-8 -*-

from hamcrest import contains_string
from prego import TestCase, Task, context as ctx

code = """
#include <stdio.h>
#include <time.h>

int
main(int argc, char *argv[]) {
    printf("Hello!\\n");
    fflush(stdout);
    sleep(1000);
    return 0;
}
"""


class TestBug(TestCase):
    def setUp(self):
        ctx.source = '/tmp/bug.c'
        ctx.bin = '/tmp/bug'

    def test(self):
        with open(ctx.source, 'w') as s:
            s.write(code)

        gcc = Task('compile')
        gcc.command('gcc $source -o $bin')

        run = Task('run', detach=True)
        c = run.command('$bin', expected=None)

        check = Task('check')
        check.wait_that(c.stdout.content, contains_string('Hello!\n'))
