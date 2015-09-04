import os
import subprocess
import re


class Checker(object):
    error_regex = re.compile(
        '^(?P<file>.+):(?P<line>\d+):(?P<offset>\d+): (?P<message>.+)$'
    )

    def __init__(self, full_name):
        self.full_name = full_name

    @property
    def errors(self):
        output = subprocess.check_output(
            ['flake8', '.', '--exit-zero'],
            cwd=os.path.join('repos', self.full_name)
        )

        return [self.error_regex.match(line).groupdict() for line in output.split("\n") if line]
