import logging
import logging.config
import platform
import docker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from hpotter.tables import Base

logging.config.fileConfig('hpotter/logging.conf')
logger = logging.getLogger('hpotter')

# note sqlite:///:memory: can't be used, even for testing, as it
# doesn't work with threads.
db = 'sqlite:///main.db'
engine = create_engine(db)
# engine = create_engine(db, echo=True)
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(engine))

# a start, for a Pi 0.
machine = 'arm32v6/' if platform.machine() == 'armv6l' else ''

busybox = True
shell_container = None

def get_busybox():
    return busybox

def get_shell_container():
    return shell_container

def startShell():
    global shell_container
    if shell_container:
        logger.info('Shell container already started')
        return

    logger.info('Starting shell container')
    client = docker.from_env()
    if busybox:
        shell_container = client.containers.run(machine + 'busybox', 
            command=['/bin/ash'], tty=True, detach=True, read_only=True)
    else:
        shell_container = client.containers.run(machine + 'alpine',
            command=['/bin/ash'], user='guest', tty=True, detach=True,
            read_only=True)

    logger.info(shell_container)

    network = client.networks.get('bridge')
    network.disconnect(shell_container)

def stopShell():
    if not shell_container:
        logger.info('No shell container to stop')
        return

    logger.info('Stopping shell container')
    shell_container.stop()
    logger.info('Removing shell container')
    shell_container.remove()

jsonserverport = 8000
