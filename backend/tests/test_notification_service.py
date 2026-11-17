import logging

from services import notification_service


def test_show_pairing_code_returns_false_on_error(monkeypatch, caplog):
    def boom(*args, **kwargs):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(notification_service, "_show_toast", boom)
    with caplog.at_level(logging.WARNING):
        assert notification_service.show_pairing_code("4821", "192.168.15.20") is False
    assert "4821" not in caplog.text
