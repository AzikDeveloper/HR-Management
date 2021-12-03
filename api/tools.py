from django.db.models import Q
from hrm.my_tools import *

"""
AND Q

queries = {
    Q(field1=value1): condition1, (+ or -),
    Q(field2=value2): condition2, (+ or -),
    Q(fieldN=valueN): conditionN, (+ or -),
}

returns filter mask
"""


def andQ(q_c: dict):
    filter_mask = Q()
    for query, condition in q_c.items():
        if '-' in condition[1]:
            filter_mask &= ~query if condition[0] else Q()
        else:
            filter_mask &= query if condition[0] else Q()
    return filter_mask
