from datetime import datetime, timedelta


class DomainCache:
    def __init__(self):
        self.ip_ttls = {}

    def set_ttl(self, ip: str, ttl: int = 0):
        ttl_time = datetime.now() + timedelta(seconds=ttl)
        self.ip_ttls.setdefault(ip, ttl_time)

    def is_ip_present_and_valid(self, ip: str):
        now = datetime.now()
        return ip in self.ip_ttls and now <= self.ip_ttls[ip]

    def get_and_del_expired_ips(self):
        now = datetime.now()
        ips_to_return = []

        for ip in list(self.ip_ttls.keys()):
            if self.ip_ttls[ip] < now:
                ips_to_return.append(ip)
                del self.ip_ttls[ip]

        return ips_to_return
