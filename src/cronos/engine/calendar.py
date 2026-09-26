"""Calendários de trabalho do Primavera P6 (tabela CALENDAR, campo clndr_data).

Formato do clndr_data (texto aninhado, separadores de linha podem ser \\x7f):

    (0||CalendarData()(
      (0||DaysOfWeek()(
        (0||1()())                                   domingo, sem trabalho
        (0||2()((0||0(s|08:00|f|12:00)())
                (0||1(s|13:00|f|17:00)())))          segunda, 8 h
        ...))
      (0||Exceptions()(
        (0||0(d|45292)())                            feriado (data serial Excel)
        (0||1(d|45300)((0||0(s|08:00|f|12:00)())))   dia com horário especial
      ))))

Dias: 1 = domingo … 7 = sábado. Datas seriais contam dias desde 1899-12-30.

O tempo de trabalho é medido em horas acumuladas desde uma data-base; somar
ou subtrair trabalho é uma busca nesse acumulado (prefix sums), o que mantém
o cálculo rápido mesmo em cronogramas com milhares de atividades.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

Intervalo = tuple[float, float]          # (hora inicial, hora final) em horas do dia
EXCEL_ZERO = date(1899, 12, 30)
PADRAO_SEMANA: dict[int, list[Intervalo]] = {  # 0 = segunda … 6 = domingo (date.weekday)
    d: ([(8.0, 12.0), (13.0, 17.0)] if d < 5 else []) for d in range(7)
}


# ---------------------------------------------------------------------------
# Parser do clndr_data
# ---------------------------------------------------------------------------
@dataclass
class _No:
    nome: str
    atributos: str
    filhos: list["_No"] = field(default_factory=list)


def _parse_nos(txt: str) -> list[_No]:
    s = txt.replace("\x7f", "").replace("\r", "").replace("\n", "").replace("\t", "")
    pos = 0

    def pula_espacos() -> None:
        nonlocal pos
        while pos < len(s) and s[pos] == " ":
            pos += 1

    def no() -> _No:
        nonlocal pos
        pos += 1                                   # "("
        ini = pos
        while s[pos] != "(":
            pos += 1
        nome = s[ini:pos].strip()
        pos += 1                                   # "(" dos atributos
        ini = pos
        while s[pos] != ")":
            pos += 1
        attrs = s[ini:pos]
        pos += 1                                   # ")"
        pula_espacos()
        filhos: list[_No] = []
        if pos < len(s) and s[pos] == "(":
            pos += 1                               # "(" dos filhos
            pula_espacos()
            while s[pos] == "(":
                filhos.append(no())
                pula_espacos()
            pos += 1                               # ")" dos filhos
        pula_espacos()
        pos += 1                                   # ")" do nó
        return _No(nome, attrs, filhos)

    nos = []
    pula_espacos()
    while pos < len(s) and s[pos] == "(":
        nos.append(no())
        pula_espacos()
    return nos


def _hora(txt: str) -> float:
    h, m = txt.split(":")[:2]
    return int(h) + int(m) / 60.0


def _intervalos(no: _No) -> list[Intervalo]:
    out = []
    for f in no.filhos:
        partes = f.atributos.split("|")
        kv = dict(zip(partes[0::2], partes[1::2]))
        if "s" in kv and "f" in kv:
            s, e = _hora(kv["s"]), _hora(kv["f"])
            if e <= s:                             # "f|00:00" = meia-noite do fim do dia
                e = 24.0 if e == 0 else e + 24.0
            out.append((s, min(e, 24.0)))
    return sorted(out)


def _procura(nos: list[_No], sufixo: str) -> _No | None:
    for n in nos:
        if n.nome.endswith(sufixo):
            return n
        achado = _procura(n.filhos, sufixo)
        if achado:
            return achado
    return None


def ler_clndr_data(txt: str) -> tuple[dict[int, list[Intervalo]], dict[date, list[Intervalo]]]:
    """Devolve (semana por date.weekday(), exceções por data). Lança ValueError se inválido."""
    try:
        nos = _parse_nos(txt)
    except (IndexError, ValueError) as e:
        raise ValueError(f"clndr_data inválido: {e}") from e
    dow = _procura(nos, "DaysOfWeek")
    if dow is None:
        raise ValueError("clndr_data sem DaysOfWeek")
    semana: dict[int, list[Intervalo]] = {d: [] for d in range(7)}
    for dia in dow.filhos:
        p6 = int(dia.nome.split("||")[-1])          # 1 = domingo … 7 = sábado
        semana[(p6 + 5) % 7] = _intervalos(dia)
    excecoes: dict[date, list[Intervalo]] = {}
    exc = _procura(nos, "Exceptions")
    for e in (exc.filhos if exc else []):
        partes = e.atributos.split("|")
        kv = dict(zip(partes[0::2], partes[1::2]))
        if "d" in kv:
            excecoes[EXCEL_ZERO + timedelta(days=int(float(kv["d"])))] = _intervalos(e)
    return semana, excecoes


# ---------------------------------------------------------------------------
# Calendário de trabalho
# ---------------------------------------------------------------------------
class Calendario:
    """Aritmética de tempo de trabalho: acumulado de horas desde a data-base."""

    def __init__(self, cid: str, nome: str, semana: dict[int, list[Intervalo]] | None = None,
                 excecoes: dict[date, list[Intervalo]] | None = None, horas_dia: float = 8.0,
                 base: date | None = None):
        self.id, self.nome = cid, nome
        self.semana = semana if semana is not None else PADRAO_SEMANA
        self.excecoes = excecoes or {}
        self.horas_dia = horas_dia or 8.0
        if not any(self.semana.values()):
            raise ValueError(f"Calendário {cid} sem nenhum dia de trabalho")
        self.base = base or date(1990, 1, 1)
        self._pref = [0.0]                          # horas trabalhadas antes do dia i

    # -- dias --------------------------------------------------------------
    def intervalos(self, d: date) -> list[Intervalo]:
        return self.excecoes.get(d, self.semana[d.weekday()])

    def _garante(self, i: int) -> None:
        while len(self._pref) <= i + 1:
            d = self.base + timedelta(days=len(self._pref) - 1)
            self._pref.append(self._pref[-1] + sum(e - s for s, e in self.intervalos(d)))

    def _indice(self, d: date) -> int:
        i = (d - self.base).days
        if i < 0:
            raise ValueError(f"Data {d} anterior à base do calendário {self.base}")
        self._garante(i)
        return i

    # -- conversões --------------------------------------------------------
    def acumulado(self, t: datetime) -> float:
        """Horas de trabalho da data-base até t."""
        i = self._indice(t.date())
        h = t.hour + t.minute / 60.0 + t.second / 3600.0
        dentro = sum(max(0.0, min(e, h) - s) for s, e in self.intervalos(t.date()))
        return self._pref[i] + dentro

    def _dia_do_acumulado(self, H: float, estrito: bool) -> int:
        i = 0
        while True:
            self._garante(i + 400)
            k = (bisect.bisect_right if estrito else bisect.bisect_left)(self._pref, H) - 1
            if k < len(self._pref) - 2:
                return max(k, 0)
            i += 400

    def _no_dia(self, i: int, resto: float, inicio: bool) -> datetime | None:
        d = self.base + timedelta(days=i)
        for s, e in self.intervalos(d):
            dur = e - s
            if resto < dur - 1e-9 or (not inicio and resto <= dur + 1e-9):
                return datetime.combine(d, datetime.min.time()) + timedelta(hours=s + max(resto, 0.0))
            resto -= dur
        return None

    def instante_fim(self, H: float) -> datetime:
        """Primeiro instante em que o acumulado atinge H (fim de trabalho: ex. 17:00)."""
        if H <= 0:
            return self.instante_inicio(0.0)
        i = self._dia_do_acumulado(H, estrito=False)
        while True:
            t = self._no_dia(i, H - self._pref[i], inicio=False)
            if t is not None:
                return t
            i += 1
            self._garante(i)

    def instante_inicio(self, H: float) -> datetime:
        """Instante de trabalho em que o acumulado vale H e há trabalho a seguir (ex. 08:00)."""
        H = max(H, 0.0)
        i = self._dia_do_acumulado(H, estrito=True)
        while True:
            t = self._no_dia(i, H - self._pref[i], inicio=True)
            if t is not None:
                return t
            i += 1
            self._garante(i)

    # -- operações de uso direto -------------------------------------------
    def proximo_inicio(self, t: datetime) -> datetime:
        return self.instante_inicio(self.acumulado(t))

    def ultimo_fim(self, t: datetime) -> datetime:
        return self.instante_fim(self.acumulado(t))

    def soma(self, t: datetime, horas: float, como_inicio: bool = False) -> datetime:
        H = self.acumulado(t) + horas
        return self.instante_inicio(H) if como_inicio else self.instante_fim(H)

    def entre(self, a: datetime, b: datetime) -> float:
        """Horas de trabalho de a até b (negativo se b < a)."""
        return self.acumulado(b) - self.acumulado(a)


def calendario_padrao(base: date | None = None) -> Calendario:
    return Calendario("_padrao", "Padrão 5×8 (seg–sex 08–12, 13–17)", base=base)
