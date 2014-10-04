# coding=utf-8

import hashlib


def compute_hash(*args):
    """Compute hash"""
    res = hashlib.sha1()
    for chunk in args:
        res.update(str(chunk))
    return res.hexdigest()
