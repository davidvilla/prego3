import pytest


class _PregoDetector:
    """Detects prego tests after collection and swaps in prego's reporter if found."""

    @pytest.hookimpl
    def pytest_collection_finish(self, session):
        import prego
        from .console import _PregoReporter

        pluginmanager = session.config.pluginmanager

        if any(isinstance(p, _PregoReporter) for p in pluginmanager.get_plugins()):
            return

        has_prego = any(_is_prego_item(item, prego) for item in session.items)

        if not has_prego:
            return

        terminal = pluginmanager.get_plugin("terminalreporter")
        if terminal is not None:
            pluginmanager.unregister(terminal)

        pluginmanager.register(_PregoReporter(verbose=False), "prego-reporter")


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
