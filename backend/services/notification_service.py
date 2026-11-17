"""Notificacao toast do Windows com o codigo de pareamento."""
import logging
from xml.sax.saxutils import escape

logger = logging.getLogger(__name__)

# AUMID do Windows PowerShell: toasts de apps sem registro precisam de um AUMID conhecido.
AUMID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"


def _build_xml(code: str, client_ip: str) -> str:
    return (
        '<toast><visual><binding template="ToastGeneric">'
        "<text>Stream Deck \u2014 c\u00f3digo de pareamento</text>"
        f"<text>{escape(code)} \u00b7 expira em 2 min</text>"
        f"<text>Pedido de {escape(client_ip)}. Se n\u00e3o foi voc\u00ea, ignore.</text>"
        "</binding></visual></toast>"
    )


def _show_toast(code: str, client_ip: str) -> None:
    from winrt.windows.data.xml.dom import XmlDocument
    from winrt.windows.ui.notifications import ToastNotification, ToastNotificationManager

    doc = XmlDocument()
    doc.load_xml(_build_xml(code, client_ip))
    notifier = ToastNotificationManager.create_toast_notifier_with_id(AUMID)
    notifier.show(ToastNotification(doc))


def show_pairing_code(code: str, client_ip: str) -> bool:
    """Exibe o toast. Sincrona (chamar via asyncio.to_thread). Nunca levanta; nunca loga o codigo."""
    try:
        _show_toast(code, client_ip)
        return True
    except Exception as exc:
        logger.warning("Falha ao exibir notificacao de pareamento: %s", type(exc).__name__)
        return False
