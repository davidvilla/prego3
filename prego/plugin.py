def pytest_configure(config):
    from .const import term
    term.cache_clear()
    term()  # pre-warm cache before pytest capture redirects stdout

    from .console import _PregoReporter
    if not any(isinstance(p, _PregoReporter) for p in config.pluginmanager.get_plugins()):
        config.pluginmanager.set_blocked("terminalreporter")
        config.pluginmanager.register(_PregoReporter(verbose=False), "prego-reporter")

    try:
        if not config.getini("log_level"):
            config._inicache["log_level"] = "INFO"
    except ValueError:
        pass
