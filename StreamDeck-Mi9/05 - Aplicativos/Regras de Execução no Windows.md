# ⚙️ Regras de Execução e Foco de Janelas no Windows

O backend Python implementa rotinas otimizadas para despachar aplicativos de forma não-bloqueante e prevenir múltiplas instâncias redundantes.

---

## 1. Foco Inteligente de Janelas (`bring_to_foreground`)
Quando o usuário toca em um app que já está aberto:
1. O backend consulta o nome do processo em `APP_PROCESS_NAMES` usando `psutil`.
2. Para WebApps e abas de navegador (`youtube`, `gemini`, `github`), consulta diretamente os títulos de janelas visíveis via `EnumWindows` no desktop `Default`.
3. Uma simulação de pressionamento e liberação da tecla `ALT` (código virtual `0x12`) é disparada para desviar a restrição do Windows contra roubo de foco.
4. O comando `SetForegroundWindow` é chamado, trazendo a janela instantaneamente para a frente sem abrir um segundo executável ou nova aba.

---

## 2. Detecção de Abas e WebApps no Windows
- Abas de navegador compartilham o processo `chrome.exe`.
- O `system_service.py` acessa o handle do desktop `Default` (`user32.OpenDesktopW`) e inspeciona janelas ativas em tempo real.
- Reconhece títulos contendo `YouTube`, `Google Gemini` e `GitHub`, ativando o **LED Neon Indicador** no deck para essas abas sem necessidade de extensões externas.

---

## 3. Execução Não-Bloqueante ("Fire and Forget")
Para abrir novos aplicativos:
* **Atalhos (.lnk), URLs e Schemas:** Executados via `os.startfile(caminho)`, que utiliza o manipulador nativo do Windows Shell sem reter a thread assíncrona.
* **Executáveis com Parâmetros:** Acionados através de `subprocess.Popen` com as flags:
  * `CREATE_NEW_PROCESS_GROUP`: Garante que o aplicativo filho continue rodando independentemente do backend.
  * `STARTF_USESHOWWINDOW` e `SW_SHOWNORMAL`: Força a janela a abrir de forma visível mesmo que o servidor Python tenha sido iniciado oculto via VBScript.

[[Catálogo de Aplicativos]]
[[MAIN]]
