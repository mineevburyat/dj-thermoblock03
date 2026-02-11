from django.test import TestCase, Client


class AllPagesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.excluded_urls = [
            'admin:',
            'api:',
            'swagger',
            'redoc',
            'debug-toolbar',
            '__debug__',
        ]
        self.excluded_patterns = [
            r'\.json$',
            r'\.xml$',
            r'\.rss$',
            r'api/',
        ]