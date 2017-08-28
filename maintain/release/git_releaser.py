import os

from git import Repo

from maintain.release.base import Releaser
from maintain.process import invoke


class GitReleaser(Releaser):
    name = 'git'

    @classmethod
    def detect(cls):
        return os.path.exists('.git')

    def __init__(self, config=None):
        self.repo = Repo()

        self.commit_format = (config or {}).get('commit_format', 'Release {version}')
        self.tag_format = (config or {}).get('tag_format', '{version}')

        if self.repo.head.ref != self.repo.heads.master:
            # TODO: Support releasing from stable/hotfix branches
            raise Exception('You need to be on the `master` branch in order to do a release.')

        if self.repo.is_dirty():
            raise Exception('Git repository has unstaged changes.')

        if self.has_origin():
            self.repo.remotes.origin.fetch()

            if self.repo.remotes.origin.refs.master.commit != self.repo.head.ref.commit:
                raise Exception('Master has unsynced changes.')

    def has_origin(self):
        try:
            self.repo.remotes.origin
        except AttributeError:
            return False

        return True

    def determine_current_version(self):
        return None

    def bump(self, new_version):
        if self.repo.is_dirty():
            self.repo.index.add('*')
            self.repo.index.commit(self.commit_format.format(version=new_version))

    def release(self, version):
        tag_name = self.tag_format.format(version=version)
        tag = self.repo.create_tag(tag_name, message='Release {}'.format(version))

        if self.has_origin():
            self.repo.remotes.origin.push(tag)


def git_update():
    invoke(['git', 'pull', 'origin', 'master'])