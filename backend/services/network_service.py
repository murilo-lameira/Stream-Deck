import socket
import logging
from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf

logger = logging.getLogger("streamdeck.network")

def get_local_ip() -> str:
    """Detecta o endereco IP local da interface ativa."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class NetworkDiscoveryService:
    def __init__(self, port: int):
        self.port = port
        self.zeroconf: AsyncZeroconf | None = None
        self.service_info: ServiceInfo | None = None

    async def start(self):
        try:
            ip = get_local_ip()
            self.zeroconf = AsyncZeroconf()
            self.service_info = ServiceInfo(
                "_http._tcp.local.",
                "StreamDeck._http._tcp.local.",
                addresses=[socket.inet_aton(ip)],
                port=self.port,
                server="streamdeck.local.",
            )
            await self.zeroconf.async_register_service(self.service_info)
            logger.info(f"mDNS Service registrado com sucesso! Acesso via: http://streamdeck.local:{self.port} (IP: {ip})")
        except Exception as e:
            logger.error(f"Erro ao registrar mDNS ZeroConf: {e}", exc_info=True)

    async def stop(self):
        if self.zeroconf and self.service_info:
            try:
                await self.zeroconf.async_unregister_service(self.service_info)
                await self.zeroconf.async_close()
                logger.info("mDNS Service finalizado.")
            except Exception as e:
                logger.debug(f"Erro ao encerrar mDNS: {e}")
