class AllowList:
    def __init__(self, allow_list: set = None):
        self.allow_list = allow_list or set()

    def is_allowed(self, domain):
        return domain in self.allow_list

    def add_domain(self, domain):
        self.allow_list.add(domain)

    def remove_domain(self, domain):
        self.allow_list.remove(domain)
