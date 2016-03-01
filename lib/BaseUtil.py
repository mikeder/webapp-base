import logging
import socket


def getInstance():
    fqdn = socket.getfqdn()
    if fqdn.endswith('zenimaxonline.com'):
        return 'bwi'
    elif fqdn.endswith('infra.dfw'):
        return 'dfw'
    elif fqdn.endswith('infra.fra'):
        return 'fra'
    else:
        # Catchall for development
        return 'dev'