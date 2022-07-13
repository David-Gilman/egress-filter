from datetime import datetime, timedelta


class DomainCache:
    def __init__(self):
        self.domain_mapping = {}

    def set_domain(self, ip: str, domain: str, ttl: int = 0):
        ttl_time = datetime.now() + timedelta(seconds=ttl)

        if domain in self.domain_mapping:
            self.domain_mapping[domain].append({'ip': ip, 'ttl': ttl_time})
        else:
            self.domain_mapping[domain] = [{'ip': ip, 'ttl': ttl_time}]

    def is_ip_present(self, ip: str, domain: str):
        now = datetime.now()

        """        if domain in self.domain_mapping and ip in self.domain_mapping[domain]:
        return now <="""

    def get_and_del_expired_ips(self) -> set[str]:
        now = datetime.now()
        ips_to_return = set()

        for domain in self.domain_mapping:
            for i, ip in enumerate(domain):
                if ip['ttl'] < now:
                    ips_to_return.add(ip['ip'])
                    del domain[i]

        return ips_to_return
