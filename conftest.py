import threading
from http.server import ThreadingHTTPServer

import pytest
from playwright.sync_api import expect

from server import HOST, PORT, Handler

expect.set_options(timeout=5000)  # проверки expect(...) ждут до 5 секунд

collect_ignore_glob = [
    "bug/*",        # исходные нестабильные версии тестов не собираем
    "artifacts/*",  # копии для скриншотов редактора тоже не собираем
]

_server = None


def pytest_configure(config):
    """Запускает магазин перед тестами: один раз, в основном процессе."""
    global _server
    if hasattr(config, "workerinput"):  # рабочий процесс pytest-xdist: сервер уже запущен
        return
    _server = ThreadingHTTPServer((HOST, PORT), Handler)
    threading.Thread(target=_server.serve_forever, daemon=True).start()


def pytest_unconfigure(config):
    if _server is not None:
        _server.shutdown()
        _server.server_close()


@pytest.fixture(autouse=True)
def short_action_timeout(page):
    page.set_default_timeout(5000)  # клик и другие действия ждут не дольше 5 секунд
