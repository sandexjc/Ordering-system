import select
import socket


def _input_fileno(request):
    """File descriptor for the WSGI request socket, if the server exposes one."""
    stream = request.META.get("wsgi.input")
    candidates = (stream, getattr(stream, "stream", None))
    for candidate in candidates:
        if candidate is None:
            continue
        try:
            fileno = candidate.fileno()
        except (AttributeError, OSError, ValueError):
            continue
        if isinstance(fileno, int) and fileno >= 0:
            return fileno
    return None


def client_disconnected(request):
    """
    True when the browser has already closed this request.

    Sync polls are aborted in the browser after 10 seconds. The WSGI worker
    still runs the view unless we notice the closed socket and return first.
    A socket with nothing waiting is treated as still connected.
    """
    fileno = _input_fileno(request)
    if fileno is None:
        return False
    try:
        readable, _, _ = select.select([fileno], [], [], 0)
    except (OSError, ValueError):
        return False
    if not readable:
        return False

    probe = socket.fromfd(fileno, socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        probe.setblocking(False)
        try:
            data = probe.recv(1, socket.MSG_PEEK)
        except BlockingIOError:
            return False
        except ConnectionResetError:
            return True
        except OSError:
            return False
        return data == b""
    finally:
        probe.close()
