import short_url
from time import time

def from_time():
    return short_url.encode_url(int(time()*1000)).upper()

def encode_url(v):
    return short_url.encode_url(v)
