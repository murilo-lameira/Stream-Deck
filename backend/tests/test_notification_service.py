import logging

from winrt.windows.ui.notifications import ToastNotificationManager

from services import notification_service


def test_show_pairing_code_returns_false_on_error(monkeypatch, caplog):
    def boom(*args, **kwargs):
        raise RuntimeError("falha 4821")

    monkeypatch.setattr(ToastNotificationManager, "create_toast_notifier_with_id", boom)
    with caplog.at_level(logging.WARNING):
        assert notification_service.show_pairing_code("4821", "192.168.15.20") is False
    assert "4821" not in caplog.text


def test_build_xml_escapes_special_chars():
    xml = notification_service._build_xml("1234", "<x&y>")
    assert "&lt;x&amp;y&gt;" in xml
    assert "<x&y>" not in xml
