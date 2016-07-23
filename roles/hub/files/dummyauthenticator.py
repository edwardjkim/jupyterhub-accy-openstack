import os
from jupyterhub.auth import LocalAuthenticator
from tornado import gen
from traitlets import Unicode
import pipes
from subprocess import Popen, PIPE, STDOUT

class DummyAuthenticator(LocalAuthenticator):

#    home_dir_string = Unicode('/home/{}',
#        help="""The format of a user's home directory path
#         """
#    ).tag(config=True)

    @gen.coroutine
    def authenticate(self, handler, data):
        return data['username']

#    @gen.coroutine
#    def add_user(self, user):
#        """Add a new user
#        
#        If self.create_system_users, the user will attempt to be created.
#        """
#        user_exists = yield gen.maybe_future(self.system_user_exists(user))
#        if not user_exists:
#            if self.create_system_users:
#                yield gen.maybe_future(self.add_jupyter_user(user))
#            else:
#                raise KeyError("User %s does not exist." % user.name)
#        
#        yield gen.maybe_future(super().add_user(user))
#
#    def add_jupyter_user(self, user):
#        """Create a new Linux/UNIX user on the system. Works on FreeBSD and Linux, at least."""
#        name = user.name
#        cmd = [ arg.replace('USERNAME', name) for arg in self.add_user_cmd ] + [name]
#        self.log.info("Creating user: %s", ' '.join(map(pipes.quote, cmd)))
#        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
#        p.wait()
#        if p.returncode:
#            err = p.stdout.read().decode('utf8', 'replace')
#            raise RuntimeError("Failed to create system user %s: %s" % (name, err))
#        home_dir = home_dir_string.format(name)
#        cmd = ['chown', '1000:1000', '{}'.format(home_dir)]
#        p = Popen(cmd, stdout=PIPE, stderr=STDOUT)
#        p.wait()
#        if p.returncode:
#            err = p.stdout.read().decode('utf8', 'replace')
#            raise RuntimeError("Failed to set home directory permissions %s: %s" % (name, err))
