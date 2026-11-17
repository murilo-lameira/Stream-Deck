import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link2, Settings } from 'lucide-react';
import { httpBaseFromWs } from '../utils/apiBase';
import { hapticFeedback } from '../utils/haptics';

const REQUEST_TIMEOUT_MS = 10000;
const CODE_LENGTH = 4;
const EMPTY_DIGITS = ['', '', '', ''];

async function postJson(url, body) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    });
    let data = {};
    try {
      data = await res.json();
    } catch {
      data = {};
    }
    return { status: res.status, data };
  } catch {
    return { status: 0, data: {} };
  } finally {
    clearTimeout(timer);
  }
}

function formatClock(ms) {
  const total = Math.max(0, Math.ceil(ms / 1000));
  const m = Math.floor(total / 60);
  const s = String(total % 60).padStart(2, '0');
  return `${m}:${s}`;
}

function minutesFrom(seconds) {
  return Math.max(1, Math.ceil((Number(seconds) || 0) / 60));
}

export function PairingScreen({ wsUrl, onPaired, onOpenSettings }) {
  const base = httpBaseFromWs(wsUrl);
  const [pairId, setPairId] = useState(null);
  const [digits, setDigits] = useState(EMPTY_DIGITS);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [now, setNow] = useState(() => Date.now());
  const [expiresAt, setExpiresAt] = useState(0);
  const [retryUntil, setRetryUntil] = useState(0);
  const inputRefs = useRef([]);
  const busyRef = useRef(false);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Relogio de 1s ativo apenas enquanto ha prazo correndo; o tempo restante vem do deadline.
  const hasDeadline = expiresAt > 0 || retryUntil > 0;
  useEffect(() => {
    if (!hasDeadline) return undefined;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [hasDeadline]);

  const resetToStart = useCallback((msg) => {
    setPairId(null);
    setExpiresAt(0);
    setDigits(EMPTY_DIGITS);
    setMessage(msg);
  }, []);

  // Codigo expirou localmente
  useEffect(() => {
    if (pairId && expiresAt && now >= expiresAt && !busy) {
      resetToStart('Expirou — gere outro');
    }
  }, [now, pairId, expiresAt, busy, resetToStart]);

  // Fim do retry_after: zera o prazo (para o intervalo) e some com "Aguarde N s"
  useEffect(() => {
    if (retryUntil && now >= retryUntil) {
      setRetryUntil(0);
      setMessage((m) => (m.startsWith('Aguarde') ? '' : m));
    }
  }, [now, retryUntil]);

  const fail = (msg) => {
    hapticFeedback.warning();
    setMessage(msg);
  };

  const focusFirst = () => setTimeout(() => inputRefs.current[0]?.focus(), 0);

  const handleRequest = async () => {
    if (busyRef.current) return;
    if (!base) {
      fail('Endereço do PC inválido');
      return;
    }
    busyRef.current = true;
    setBusy(true);
    setMessage('');
    const { status, data } = await postJson(`${base}/api/v1/deck/pair/request`);
    busyRef.current = false;
    if (!mountedRef.current) return;
    setBusy(false);
    const retry = Number(data.retry_after) || 0;
    if (status === 200 && data.pair_id) {
      const t = Date.now();
      setPairId(data.pair_id);
      setDigits(EMPTY_DIGITS);
      setNow(t);
      setExpiresAt(t + (Number(data.expires_in) || 120) * 1000);
      focusFirst();
    } else if (status === 429) {
      setRetryUntil(Date.now() + retry * 1000);
      setNow(Date.now());
      fail(`Aguarde ${Math.max(1, Math.ceil(retry))} s`);
    } else if (status === 423) {
      fail(`Muitas tentativas — tente em ${minutesFrom(retry)} min`);
      if (pairId !== null) resetToStart(`Muitas tentativas — tente em ${minutesFrom(retry)} min`);
    } else if (status === 503) {
      fail('Não consegui mostrar o código no PC');
      if (pairId !== null) resetToStart('Não consegui mostrar o código no PC');
    } else if (status === 403) {
      fail('Acesso negado — use a rede local');
    } else if (status === 0) {
      fail('Sem conexão com o PC');
    } else {
      fail('Erro inesperado');
    }
  };

  const submitCode = async (code) => {
    if (busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setMessage('');
    const { status, data } = await postJson(`${base}/api/v1/deck/pair/confirm`, {
      pair_id: pairId,
      code
    });
    busyRef.current = false;
    if (!mountedRef.current) return;
    setBusy(false);
    if (status === 200 && data.auth_token) {
      hapticFeedback.success();
      onPaired(data.auth_token);
      return;
    }
    setDigits(EMPTY_DIGITS);
    if (status === 401) {
      const left = Number(data.attempts_left);
      if (!(left > 0)) {
        hapticFeedback.warning();
        resetToStart('Código errado — gere outro');
        return;
      }
      fail(`Código errado — ${left} ${left === 1 ? 'tentativa restante' : 'tentativas restantes'}`);
      focusFirst();
    } else if (status === 410) {
      hapticFeedback.warning();
      resetToStart('Expirou — gere outro');
    } else if (status === 423) {
      hapticFeedback.warning();
      resetToStart(`Muitas tentativas — tente em ${minutesFrom(data.retry_after)} min`);
    } else if (status === 0) {
      fail('Sem conexão com o PC');
      focusFirst();
    } else {
      fail('Erro inesperado');
      focusFirst();
    }
  };

  const applyDigits = (next) => {
    setDigits(next);
    if (next.every((d) => d !== '')) submitCode(next.join(''));
  };

  const handleChange = (index, value) => {
    // Apagar via teclado virtual/cortar: o Gboard nem sempre manda keydown Backspace
    if (value === '') {
      const cleared = [...digits];
      cleared[index] = '';
      setDigits(cleared);
      return;
    }
    let onlyDigits = value.replace(/\D/g, '');
    if (!onlyDigits) return;
    // Campo ja tinha um digito e entrou 1 caractere a mais: substitui pelo novo caractere
    if (digits[index] && onlyDigits.length === 2) {
      onlyDigits = onlyDigits.replace(digits[index], '').slice(-1) || onlyDigits.slice(-1);
    }
    const next = [...digits];
    if (onlyDigits.length > 1) {
      // autopreenchimento (one-time-code): distribui a partir deste campo
      onlyDigits.slice(0, CODE_LENGTH - index).split('').forEach((d, i) => {
        next[index + i] = d;
      });
      inputRefs.current[Math.min(index + onlyDigits.length, CODE_LENGTH - 1)]?.focus();
    } else {
      next[index] = onlyDigits;
      if (index < CODE_LENGTH - 1) inputRefs.current[index + 1]?.focus();
    }
    applyDigits(next);
  };

  const handleKeyDown = (index, e) => {
    if (e.key !== 'Backspace') return;
    e.preventDefault();
    const next = [...digits];
    if (next[index]) {
      next[index] = '';
      setDigits(next);
    } else if (index > 0) {
      next[index - 1] = '';
      setDigits(next);
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    const text = (e.clipboardData?.getData('text') || '').replace(/\D/g, '');
    if (!text) return;
    e.preventDefault();
    const next = [...EMPTY_DIGITS];
    text.slice(0, CODE_LENGTH).split('').forEach((d, i) => {
      next[i] = d;
    });
    inputRefs.current[Math.min(text.length, CODE_LENGTH) - 1]?.focus();
    applyDigits(next);
  };

  const retryLeft = Math.max(0, retryUntil - now);
  const waitLabel = `Aguarde ${Math.ceil(retryLeft / 1000)} s`;

  return (
    <div className="pairing-screen">
      <div className="pairing-card">
        <Link2 size={36} className="pairing-icon" />
        <h1 className="pairing-title">Parear com o PC</h1>

        {pairId === null ? (
          <>
            <p className="pairing-hint">O código aparece numa notificação no PC</p>
            <button
              type="button"
              className="pairing-btn-primary"
              onClick={handleRequest}
              disabled={busy || retryLeft > 0}
            >
              {retryLeft > 0 ? waitLabel : 'Parear com o PC'}
            </button>
          </>
        ) : (
          <>
            <p className="pairing-hint">Digite o código de 4 dígitos mostrado no PC</p>
            <div className="pairing-digits" onPaste={handlePaste}>
              {digits.map((d, i) => (
                <input
                  key={i}
                  ref={(el) => {
                    inputRefs.current[i] = el;
                  }}
                  className="pairing-digit"
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  maxLength={i === 0 ? CODE_LENGTH : 1}
                  autoComplete={i === 0 ? 'one-time-code' : 'off'}
                  value={d}
                  disabled={busy}
                  aria-label={`Dígito ${i + 1}`}
                  onChange={(e) => handleChange(i, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(i, e)}
                />
              ))}
            </div>
            <div className="pairing-countdown">{formatClock(expiresAt - now)}</div>
            <p className="pairing-hint pairing-hint-small">
              Não apareceu? Veja as notificações (Win+N)
            </p>
            <button
              type="button"
              className="pairing-btn-secondary"
              onClick={handleRequest}
              disabled={busy || retryLeft > 0}
            >
              {retryLeft > 0 ? waitLabel : 'Gerar novo código'}
            </button>
          </>
        )}

        <div className="pairing-message" role="status" aria-live="polite">
          {message}
        </div>

        <button type="button" className="pairing-link" onClick={onOpenSettings}>
          <Settings size={14} /> Endereço do PC
        </button>
      </div>
    </div>
  );
}

export default PairingScreen;
