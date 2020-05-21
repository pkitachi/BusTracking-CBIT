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
        
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()

        if (len(self.history))//2 >= self.num_requests:
            return False,None
        if k==1 and len(self.history) < 3:
            return True,None
        elif len(self.history) >= 3:
            data = Counter(self.history)
            for key, value in data.items():
                if value == 2:
                    return False,None
        else:
            return self.throttle_success(uname)

    def throttle_success(self,uname):
        """
        Inserts the current request's timestamp along with the key
        into the cache.
        """
        username=uname
        self.history.insert(0, self.now)
        self.history.insert(0, username)
        
        self.cache.set(self.key, self.history, self.duration)
        return True,len(self.history)