from django.conf import settings

settings.DEBUG = True
from django.db import connection, reset_queries


def num_queries(reset=True):
    print(len(connection.queries))
    if reset:
        reset_queries()
