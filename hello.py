#!/usr/bin/env python


import msgpack
from cocaine.decorators import http

from cocaine.worker import Worker
from cocaine.logging import Logger

@http
def main(request, response):
    response.write("Hello, world!")
    response.close()


W = Worker()
W.run({
    'doIt': main,
})
