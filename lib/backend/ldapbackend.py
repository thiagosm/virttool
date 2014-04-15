import ldap
from django.conf import settings
from django.contrib.auth.models import User

class LdapBackend:
    """Authenticate using LDAP
    """
    def authenticate(self, username=None, password=None):
        l = ldap.open('server.example.net', 389)
        userdn = 'uid=%s,ou=users,dc=domain,dc=com' % username         
        try:
            l.simple_bind_s(userdn, password)
            valid = True
        except ldap.LDAPError, e:
            valid = False

        if valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. Note that we can set password to anything
                # as it won't be checked, the password from settings.py will.
                user = User(username=username, password="password from ldap")
                user.is_staff = False
                user.is_superuser = False
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
	