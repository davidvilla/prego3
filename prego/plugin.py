import io

import pytest


class _PregoDetector:
    """Detects prego tests after collection and swaps in prego's reporter if found.

    The standard reporter writes its header before collection, so its output
    is buffered from session start and then discarded (prego session) or
    replayed verbatim (regular session) once the detection can be done.
    """

    def __init__(self):
        self._buffer = None
        self._original_file = None

    def _start_buffering(self, terminal):
        tw = getattr(terminal, '_tw', None)
        if getattr(tw, '_file', None) is None:
            return
        self._buffer = io.StringIO()
        self._original_file = tw._file
        tw._file = self._buffer

    def _stop_buffering(self, terminal, replay):
        if self._buffer is None:
            return
        terminal._tw._file = self._original_file
        if replay:
            self._original_file.write(self._buffer.getvalue())
            self._original_file.flush()
        self._buffer = None

    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionstart(self, session):
        terminal = session.config.pluginmanager.get_plugin("terminalreporter")
        if terminal is not None:
            self._start_buffering(terminal)

    @pytest.hookimpl
    def pytest_collection_finish(self, session):
        import prego
        from .console import _PregoReporter

        pluginmanager = session.config.pluginmanager
        terminal = pluginmanager.get_plugin("terminalreporter")

        already_registered = any(
            isinstance(p, _PregoReporter) for p in pluginmanager.get_plugins())
        has_prego = not already_registered and any(
            _is_prego_item(item, prego) for item in session.items)

        if already_registered or not has_prego:
            if terminal is not None:
                self._stop_buffering(terminal, replay=True)
            return

        if terminal is not None:
            self._stop_buffering(terminal, replay=False)
            pluginmanager.unregister(terminal)

        pluginmanager.register(_PregoReporter(verbose=False), "prego-reporter")

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session, exitstatus):
        # safety net: if collection aborted before pytest_collection_finish,
        # give the buffered output back instead of swallowing it
        terminal = session.config.pluginmanager.get_plugin("terminalreporter")
        if terminal is not None:
            self._stop_buffering(terminal, replay=True)


def _is_prego_item(item, prego):
    parent = getattr(item, 'parent', None)
    cls = getattr(parent, 'cls', None)
    if cls is not None and issubclass(cls, prego.TestCase):
        return True
    module = getattr(item, 'module', None)
    if module is not None and prego in vars(module).values():
        return True
    return False


def pytest_configure(config):
    config.pluginmanager.register(_PregoDetector(), "prego-detector")

    try:
        if not config.getini("log_level"):
            config._inicache["log_level"] = "INFO"
    except ValueError:
        pass
