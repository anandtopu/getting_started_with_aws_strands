"""A test-only network guard: loopback supports asyncio, external access fails."""

import ipaddress
import socket
from contextlib import ExitStack, contextmanager
from unittest.mock import patch


def is_loopback(host: str | bytes | None) -> bool:
    if host is None:
        return True
    if isinstance(host, bytes):
        host = host.decode("ascii")
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


@contextmanager
def offline_network():
    """Block external DNS, TCP and UDP; this is a test guard, not an OS sandbox."""
    original_dns = socket.getaddrinfo
    original_host_lookup = socket.gethostbyname
    original_extended_lookup = socket.gethostbyname_ex
    original_reverse_lookup = socket.gethostbyaddr
    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex
    original_sendto = socket.socket.sendto

    def dns(host, *args, **kwargs):
        if not is_loopback(host):
            raise OSError("External network disabled in offline mode")
        return original_dns(host, *args, **kwargs)

    def validate(sock, address):
        if sock.family in (socket.AF_INET, socket.AF_INET6) and not is_loopback(address[0]):
            raise OSError("External network disabled in offline mode")

    def local_lookup(original):
        def lookup(host):
            if not is_loopback(host):
                raise OSError("External network disabled in offline mode")
            return original(host)

        return lookup

    def connect(sock, address):
        validate(sock, address)
        return original_connect(sock, address)

    def connect_ex(sock, address):
        validate(sock, address)
        return original_connect_ex(sock, address)

    def sendto(sock, data, *args):
        validate(sock, args[-1])
        return original_sendto(sock, data, *args)

    with ExitStack() as stack:
        for target, replacement in [
            ("socket.getaddrinfo", dns),
            ("socket.gethostbyname", local_lookup(original_host_lookup)),
            ("socket.gethostbyname_ex", local_lookup(original_extended_lookup)),
            ("socket.gethostbyaddr", local_lookup(original_reverse_lookup)),
            ("socket.socket.connect", connect),
            ("socket.socket.connect_ex", connect_ex),
            ("socket.socket.sendto", sendto),
        ]:
            stack.enter_context(patch(target, replacement))
        yield
