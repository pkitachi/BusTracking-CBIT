from collections import Counter
from rest_framework.throttling import SimpleRateThrottle


class UserLoginRateThrottle(SimpleRateThrottle):
    scope = 'loginAttempts'

    def get_cache_key(self, uname):
        

        ident = uname

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    def allow_request(self,uname,k):
        """
        Implement the check to see if the request should be throttled.
        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        if self.rate is None:
            return True

        self.key = self.get_cache_key(uname)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()
        
        if (k==1 and (len(self.history) <=2)):
            return True,None
        else:
            if(len(self.history)<4):
                self.history.insert(0, uname)
                self.cache.set(self.key, self.history, self.duration)
            if (len(self.history)) >2:
                return False,None
            else:
                return True,len(self.history)
    

        
