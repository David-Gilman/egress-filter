import logging_helper


logging = logging_helper.setup_logging()


class AllowList():
    def __init__(self, allow_list = set()):
        self.allow_list = allow_list


    def is_allowed(self, domain):
        print(domain)
        return domain in self.allow_list


    def add_domain(self, domain):
        self.allow_list.add(domain)


    def remove_domain(self, domain):
        self.allow_list.remove(domain)
