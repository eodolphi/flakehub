from git import NoSuchPathError, Repo as GitRepo
from flakehub import checker


class Repo(object):
    def __init__(self, full_name):
        self.full_name = full_name

        try:
            self.repo = GitRepo('repos/{}'.format(full_name))
        except NoSuchPathError:
            self.repo = GitRepo.clone_from(
                'git@github.com:{}.git'.format(full_name),
                'repos/{}'.format(full_name)
            )

    def checkout(self, sha):
        self.repo.git.checkout(sha)

    @property
    def errors(self):
        code_checker = checker.Checker(self.full_name)

        return code_checker.errors
