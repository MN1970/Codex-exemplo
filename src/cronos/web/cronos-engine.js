/* Manta Cronos — motor no navegador (porta fiel de src/cronos/engine, Python).
 * Datas são "ingênuas" (sem fuso): milissegundos UTC representando o relógio local do XER.
 * Exposto como window.CronosEngine (navegador) ou module.exports (Node, para testes). */
(function (root) {
  "use strict";
  var DIA = 86400000, H = 3600000, EPS = 1e-6;
  var EXCEL_ZERO = Date.UTC(1899, 11, 30);

  function dataXER(v) {
    if (!v) return null;
    var m = /^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2}))?/.exec(String(v).trim());
    return m ? Date.UTC(+m[1], +m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0)) : null;
  }
  function p2(n) { return (n < 10 ? "0" : "") + n; }
  function fmtXER(t) {
    if (t == null) return "";
    var d = new Date(t);
    return d.getUTCFullYear() + "-" + p2(d.getUTCMonth() + 1) + "-" + p2(d.getUTCDate()) + " " + p2(d.getUTCHours()) + ":" + p2(d.getUTCMinutes());
  }
  function fmtBR(t) { if (t == null) return "—"; var d = new Date(t); return p2(d.getUTCDate()) + "/" + p2(d.getUTCMonth() + 1) + "/" + d.getUTCFullYear(); }
  function num(v) { var n = parseFloat(v); return isFinite(n) ? n : 0; }
  function diaSemana(t) { return (new Date(t).getUTCDay() + 6) % 7; } // 0 = segunda … 6 = domingo

  /* ---------------- clndr_data ---------------- */
  function parseNos(txt) {
    var s = String(txt).replace(/[\x7f\r\n\t]/g, ""), pos = 0;
    function esp() { while (pos < s.length && s[pos] === " ") pos++; }
    function no() {
      pos++; var ini = pos;
      while (s[pos] !== "(") { if (pos >= s.length) throw new Error("fim inesperado"); pos++; }
      var nome = s.slice(ini, pos).trim(); pos++; ini = pos;
      while (s[pos] !== ")") { if (pos >= s.length) throw new Error("fim inesperado"); pos++; }
      var attrs = s.slice(ini, pos); pos++; esp();
      var filhos = [];
      if (s[pos] === "(") { pos++; esp(); while (s[pos] === "(") { filhos.push(no()); esp(); } pos++; }
      esp(); pos++;
      return { nome: nome, atributos: attrs, filhos: filhos };
    }
    var nos = []; esp();
    while (pos < s.length && s[pos] === "(") { nos.push(no()); esp(); }
    return nos;
  }
  function hora(t) { var p = t.split(":"); return +p[0] + (+p[1]) / 60; }
  function intervalos(n) {
    var out = [];
    n.filhos.forEach(function (f) {
      var p = f.atributos.split("|"), kv = {};
      for (var i = 0; i + 1 < p.length; i += 2) kv[p[i]] = p[i + 1];
      if (kv.s && kv.f) { var a = hora(kv.s), b = hora(kv.f); if (b <= a) b = b === 0 ? 24 : b + 24; out.push([a, Math.min(b, 24)]); }
    });
    return out.sort(function (x, y) { return x[0] - y[0]; });
  }
  function procura(nos, suf) {
    for (var i = 0; i < nos.length; i++) {
      if (nos[i].nome.slice(-suf.length) === suf) return nos[i];
      var a = procura(nos[i].filhos, suf); if (a) return a;
    }
    return null;
  }
  function lerClndrData(txt) {
    var nos;
    try { nos = parseNos(txt); } catch (e) { throw new Error("clndr_data inválido: " + e.message); }
    var dow = procura(nos, "DaysOfWeek");
    if (!dow) throw new Error("clndr_data sem DaysOfWeek");
    var semana = {}; for (var d = 0; d < 7; d++) semana[d] = [];
    dow.filhos.forEach(function (dia) { var n = +dia.nome.split("||").pop(); semana[(n + 5) % 7] = intervalos(dia); });
    var exc = {}, e = procura(nos, "Exceptions");
    (e ? e.filhos : []).forEach(function (x) {
      var p = x.atributos.split("|"), kv = {};
      for (var i = 0; i + 1 < p.length; i += 2) kv[p[i]] = p[i + 1];
      if (kv.d) exc[EXCEL_ZERO + Math.floor(num(kv.d)) * DIA] = intervalos(x);
    });
    return { semana: semana, excecoes: exc };
  }

  /* ---------------- Calendário ---------------- */
  var PADRAO = {}; for (var dd = 0; dd < 7; dd++) PADRAO[dd] = dd < 5 ? [[8, 12], [13, 17]] : [];
  function Calendario(id, nome, semana, excecoes, horasDia, base) {
    this.id = id; this.nome = nome; this.semana = semana || PADRAO; this.excecoes = excecoes || {};
    this.horasDia = horasDia || 8; this.base = base || Date.UTC(1990, 0, 1); this.pref = [0];
    var algum = false; for (var k in this.semana) if (this.semana[k].length) algum = true;
    if (!algum) throw new Error("Calendário " + id + " sem nenhum dia de trabalho");
  }
  Calendario.prototype.intervalos = function (dia) { var e = this.excecoes[dia]; return e !== undefined ? e : this.semana[diaSemana(dia)]; };
  Calendario.prototype._garante = function (i) {
    while (this.pref.length <= i + 1) {
      var dia = this.base + (this.pref.length - 1) * DIA, soma = 0;
      this.intervalos(dia).forEach(function (iv) { soma += iv[1] - iv[0]; });
      this.pref.push(this.pref[this.pref.length - 1] + soma);
    }
  };
  Calendario.prototype.acumulado = function (t) {
    var dia = Math.floor(t / DIA) * DIA, i = Math.round((dia - this.base) / DIA);
    if (i < 0) throw new Error("Data anterior à base do calendário");
    this._garante(i);
    var h = (t - dia) / H, dentro = 0;
    this.intervalos(dia).forEach(function (iv) { dentro += Math.max(0, Math.min(iv[1], h) - iv[0]); });
    return this.pref[i] + dentro;
  };
  Calendario.prototype._diaDo = function (Hh, estrito) {
    var a = this.pref;
    for (;;) {
      this._garante(a.length + 400);
      var lo = 0, hi = a.length;           // bisect_left / bisect_right
      while (lo < hi) { var mid = (lo + hi) >> 1; if (estrito ? a[mid] <= Hh : a[mid] < Hh) lo = mid + 1; else hi = mid; }
      var k = lo - 1;
      if (k < a.length - 2) return Math.max(k, 0);
    }
  };
  Calendario.prototype._noDia = function (i, resto, inicio) {
    var dia = this.base + i * DIA, ivs = this.intervalos(dia);
    for (var j = 0; j < ivs.length; j++) {
      var dur = ivs[j][1] - ivs[j][0];
      if (resto < dur - 1e-9 || (!inicio && resto <= dur + 1e-9)) return dia + Math.round((ivs[j][0] + Math.max(resto, 0)) * H);
      resto -= dur;
    }
    return null;
  };
  Calendario.prototype.instanteFim = function (Hh) {
    if (Hh <= 0) return this.instanteInicio(0);
    var i = this._diaDo(Hh, false);
    for (;;) { var t = this._noDia(i, Hh - this.pref[i], false); if (t !== null) return t; i++; this._garante(i); }
  };
  Calendario.prototype.instanteInicio = function (Hh) {
    Hh = Math.max(Hh, 0);
    var i = this._diaDo(Hh, true);
    for (;;) { var t = this._noDia(i, Hh - this.pref[i], true); if (t !== null) return t; i++; this._garante(i); }
  };
  Calendario.prototype.proximoInicio = function (t) { return this.instanteInicio(this.acumulado(t)); };
  Calendario.prototype.ultimoFim = function (t) { return this.instanteFim(this.acumulado(t)); };
  Calendario.prototype.soma = function (t, h, comoInicio) { var Hh = this.acumulado(t) + h; return comoInicio ? this.instanteInicio(Hh) : this.instanteFim(Hh); };
  Calendario.prototype.entre = function (a, b) { return this.acumulado(b) - this.acumulado(a); };

  /* ---------------- XER ---------------- */
  var TL = { PR_FS: "FS", PR_SS: "SS", PR_FF: "FF", PR_SF: "SF" };
  var TA = { TT_Task: "tarefa", TT_Rsrc: "tarefa", TT_Mile: "marco_inicio", TT_FinMile: "marco_fim", TT_LOE: "loe", TT_WBS: "resumo" };
  var ST = { TK_NotStart: "nao_iniciada", TK_Active: "em_andamento", TK_Complete: "concluida" };
  var RS = { CS_MSOA: "SNET", CS_MEOA: "FNET", CS_MSOB: "SNLT", CS_MEOB: "FNLT", CS_MSO: "MSO", CS_MEO: "MFO", CS_MANDSTART: "MSO", CS_MANDFIN: "MFO", CS_ALAP: "ALAP" };
  var HIST = ["obsoleto", "_deprecated", "deprecated", "99-backup"];
  function eHistorico(c) { c = String(c || "").toLowerCase(); return HIST.some(function (h) { return c.indexOf(h) >= 0; }); }

  function lerTabelas(txt) {
    var fim = txt.slice(0, 5000).indexOf("\r\n") >= 0 ? "\r\n" : "\n", linhas = txt.split(fim);
    var tb = { cabecalho: linhas[0] && linhas[0].indexOf("ERMHDR") === 0 ? linhas[0] : "ERMHDR\t19.12", ordem: [], campos: {}, linhas: {}, fimLinha: fim }, atual = null;
    for (var n = 0; n < linhas.length; n++) {
      var p = linhas[n].split("\t"), m = p[0];
      if (m === "%T") { atual = (p[1] || "").trim(); tb.ordem.push(atual); tb.linhas[atual] = []; }
      else if (m === "%F" && atual) tb.campos[atual] = p.slice(1);
      else if (m === "%R" && atual) { var r = { _linha: String(n + 1) }, f = tb.campos[atual] || []; for (var k = 0; k < f.length; k++) r[f[k]] = p[k + 1]; tb.linhas[atual].push(r); }
    }
    return tb;
  }
  function lerXER(txt, arq) {
    var tb = lerTabelas(txt), L = function (t) { return tb.linhas[t] || []; };
    var datas = [];
    L("PROJECT").forEach(function (p) { var d = dataXER(p.plan_start_date) || dataXER(p.last_recalc_date); if (d) datas.push(d); });
    L("TASK").slice(0, 5000).forEach(function (a) { var d = dataXER(a.act_start_date) || dataXER(a.target_start_date); if (d) datas.push(d); });
    var base = datas.length ? Date.UTC(new Date(Math.min.apply(null, datas)).getUTCFullYear() - 2, 0, 1) : Date.UTC(1990, 0, 1);
    var alertas = [], cals = { _padrao: new Calendario("_padrao", "Padrão 5×8", null, null, 8, base) };
    L("CALENDAR").forEach(function (c) {
      try { var x = lerClndrData(c.clndr_data || ""); cals[c.clndr_id] = new Calendario(c.clndr_id, c.clndr_name || c.clndr_id, x.semana, x.excecoes, num(c.day_hr_cnt) || 8, base); }
      catch (e) { alertas.push("Calendário " + c.clndr_id + " ilegível, usado o padrão 5×8: " + e.message); }
    });
    var wbs = {}, wbsNo = {}; L("PROJWBS").forEach(function (w) { wbs[w.wbs_id] = w.wbs_name || ""; wbsNo[w.wbs_id] = w; });
    function caminhoWBS(id) {
      var c = [], vistos = {};
      while (id && wbsNo[id] && !vistos[id]) { vistos[id] = 1; if (wbsNo[id].proj_node_flag !== "Y") c.unshift(id); id = wbsNo[id].parent_wbs_id; }
      return c;
    }
    var custo = {}, real = {}, rec = {};
    L("TASKRSRC").forEach(function (r) { custo[r.task_id] = (custo[r.task_id] || 0) + num(r.target_cost); real[r.task_id] = (real[r.task_id] || 0) + num(r.act_reg_cost) + num(r.act_ot_cost); rec[r.task_id] = true; });
    var P = {}, ordem = [];
    L("PROJECT").forEach(function (p) {
      P[p.proj_id] = { id: p.proj_id, nome: p.proj_short_name || p.proj_id, arquivo: arq, chave: arq + "#" + p.proj_id,
        dataStatus: dataXER(p.last_recalc_date) || dataXER(p.plan_start_date), inicioPlan: dataXER(p.plan_start_date),
        terminoExigido: dataXER(p.plan_end_date), calPadrao: p.clndr_id || "", calendarios: cals, at: {}, lig: [],
        alertas: alertas.slice(), origem: tb };
      ordem.push(p.proj_id);
    });
    L("TASK").forEach(function (a) {
      var pr = P[a.proj_id]; if (!pr) return;
      var restr = [];
      [["cstr_type", "cstr_date"], ["cstr_type2", "cstr_date2"]].forEach(function (c) { var tp = RS[a[c[0]]]; if (tp) restr.push({ tipo: tp, data: dataXER(a[c[1]]) }); });
      var rest = a.remain_drtn_hr_cnt !== undefined && a.remain_drtn_hr_cnt !== "" ? num(a.remain_drtn_hr_cnt) : num(a.target_drtn_hr_cnt);
      pr.at[a.task_id] = { uid: a.task_id, cod: a.task_code || "", nome: a.task_name || "", wbs: wbs[a.wbs_id] || "",
        tipo: TA[a.task_type || "TT_Task"] || "tarefa", status: ST[a.status_code] || "nao_iniciada",
        durH: num(a.target_drtn_hr_cnt), restH: rest, cal: a.clndr_id || "",
        iniReal: dataXER(a.act_start_date), fimReal: dataXER(a.act_end_date),
        iniPlan: dataXER(a.target_start_date), fimPlan: dataXER(a.target_end_date),
        restricoes: restr, custo: custo[a.task_id] || 0, custoReal: real[a.task_id] || 0,
        pctFisico: a.phys_complete_pct !== undefined && a.phys_complete_pct !== "" ? num(a.phys_complete_pct) : null, temRecurso: !!rec[a.task_id],
        fonte: arq + " › TASK › linha " + a._linha, eapCaminho: caminhoWBS(a.wbs_id) };
    });
    ordem.forEach(function (k) {                  // nós da EAP em ordem de exibição (seq_num, como no P6)
      var pr = P[k], filhos = {}, nos = [];
      L("PROJWBS").forEach(function (w) { if (w.proj_id === k && w.proj_node_flag !== "Y") (filhos[w.parent_wbs_id] = filhos[w.parent_wbs_id] || []).push(w); });
      var raizes = L("PROJWBS").filter(function (w) { return w.proj_id === k && w.proj_node_flag !== "Y" && (!wbsNo[w.parent_wbs_id] || wbsNo[w.parent_wbs_id].proj_node_flag === "Y"); });
      (function dfs(lista, nivel, pai) {
        lista.sort(function (a, b) { return num(a.seq_num) - num(b.seq_num) || String(a.wbs_short_name || a.wbs_name).localeCompare(String(b.wbs_short_name || b.wbs_name)); })
          .forEach(function (w) { nos.push({ chave: w.wbs_id, nome: w.wbs_name || w.wbs_short_name || w.wbs_id, codigo: w.wbs_short_name || "", nivel: nivel, pai: pai }); dfs(filhos[w.wbs_id] || [], nivel + 1, w.wbs_id); });
      })(raizes, 0, null);
      pr.eapNos = nos;
    });
    L("TASKPRED").forEach(function (r) {
      var pr = P[r.proj_id] || P[r.pred_proj_id];
      if (pr && pr.at[r.task_id] && pr.at[r.pred_task_id]) pr.lig.push({ p: r.pred_task_id, s: r.task_id, t: TL[r.pred_type] || "FS", lag: num(r.lag_hr_cnt) });
    });
    return ordem.map(function (k) { var p = P[k]; p.custo = sumCusto(p); return p; });
  }
  function sumCusto(p) { var s = 0; for (var u in p.at) s += p.at[u].custo; return s; }
  function noCalculo(a) { return a.tipo !== "loe" && a.tipo !== "resumo"; }
  function marco(a) { return a.tipo === "marco_inicio" || a.tipo === "marco_fim"; }
  function calDe(p, a) { return p.calendarios[a.cal] || p.calendarios[p.calPadrao] || p.calendarios._padrao; }

  /* ---------------- MSPDI ---------------- */
  function horasISO(v) { var m = /PT(\d+(?:\.\d+)?)H(\d+(?:\.\d+)?)M(\d+(?:\.\d+)?)S/.exec(v || ""); return m ? num(m[1]) + num(m[2]) / 60 + num(m[3]) / 3600 : 0; }
  function filhos(el, n) { var o = []; if (!el) return o; for (var i = 0; i < el.children.length; i++) if (el.children[i].localName === n) o.push(el.children[i]); return o; }
  function hhmm(v) { var p = String(v || "0:0").split(":"); return +p[0] + (+p[1]) / 60; }
  function faixasMS(el) {
    var o = [];
    filhos(filhos(el, "WorkingTimes")[0], "WorkingTime").forEach(function (w) {
      var s = hhmm((filhos(w, "FromTime")[0] || {}).textContent), e = hhmm((filhos(w, "ToTime")[0] || {}).textContent);
      if (e <= s) e = e === 0 ? 24 : e + 24; o.push([s, Math.min(e, 24)]);
    });
    return o.sort(function (a, b) { return a[0] - b[0]; });
  }
  function diasMS(tp, g) {
    if (!tp) return [];
    var a = dataXER(g(tp, "FromDate")), b = dataXER(g(tp, "ToDate")) || a, o = [];
    if (a == null) return o;
    for (var d = Math.floor(a / DIA) * DIA; d <= b && o.length < 3660; d += DIA) o.push(d);
    return o;
  }
  function calendariosMSPDI(raiz, g, hd, base) {
    var cals = { _padrao: new Calendario("_padrao", "Padrão 5×8", null, null, hd, base) }, alertas = [], brutos = {};
    filhos(filhos(raiz, "Calendars")[0], "Calendar").forEach(function (c) {
      var sem = {}, exc = {};
      filhos(filhos(c, "WeekDays")[0], "WeekDay").forEach(function (wd) {
        var tp = g(wd, "DayType"), fx = g(wd, "DayWorking") === "1" ? faixasMS(wd) : [];
        if (tp === "0") diasMS(filhos(wd, "TimePeriod")[0], g).forEach(function (d) { exc[d] = fx; });
        else if (+tp >= 1 && +tp <= 7) sem[(+tp + 5) % 7] = fx;
      });
      filhos(filhos(c, "Exceptions")[0], "Exception").forEach(function (ex) {
        var fx = g(ex, "DayWorking") === "1" ? faixasMS(ex) : [];
        diasMS(filhos(ex, "TimePeriod")[0], g).forEach(function (d) { exc[d] = fx; });
      });
      brutos[g(c, "UID")] = { nome: g(c, "Name") || g(c, "UID"), base: g(c, "BaseCalendarUID"), sem: sem, exc: exc };
    });
    Object.keys(brutos).forEach(function (uid) {
      var b = brutos[uid], h = brutos[b.base], sem = {}, exc = {}, k;
      for (var d = 0; d < 7; d++) sem[d] = b.sem[d] !== undefined ? b.sem[d] : (h && h.sem[d] !== undefined ? h.sem[d] : cals._padrao.semana[d]);
      if (h) for (k in h.exc) exc[k] = h.exc[k];
      for (k in b.exc) exc[k] = b.exc[k];
      try { cals[uid] = new Calendario(uid, b.nome, sem, exc, hd, base); }
      catch (e) { alertas.push("Calendário " + uid + " (" + b.nome + ") ignorado: " + e.message); }
    });
    return { cals: cals, alertas: alertas };
  }
  /* Leitor XML mínimo (Node/testes, sem DOMParser): elementos com localName, children e textContent. */
  function xmlMin(txt) {
    var ent = function (v) { return v.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, "&"); };
    var raiz = { localName: "#doc", children: [], textContent: "" }, pilha = [raiz], re = /<(\/?)([A-Za-z_][\w:.-]*)[^>]*?(\/?)>|([^<]+)|<[!?][^>]*>/g, m, todos = [];
    while ((m = re.exec(txt))) {
      var topo = pilha[pilha.length - 1];
      if (m[4] !== undefined) { var tx = ent(m[4]); pilha.forEach(function (e) { e.textContent += tx; }); continue; }
      if (!m[2]) continue;
      var nome = m[2].replace(/^.*:/, "");
      if (m[1]) { if (pilha.length > 1) pilha.pop(); continue; }
      var el = { localName: nome, children: [], textContent: "" }; topo.children.push(el); todos.push(el);
      if (!m[3]) pilha.push(el);
    }
    return { documentElement: raiz.children[0], getElementsByTagName: function (n) { return todos.filter(function (e) { return e.localName === n; }); } };
  }
  var CT_DE = { "1": "ALAP", "2": "MSO", "3": "MFO", "4": "SNET", "5": "SNLT", "6": "FNET", "7": "FNLT" }, CT_PARA = {};
  Object.keys(CT_DE).forEach(function (k) { CT_PARA[CT_DE[k]] = k; });
  function lerMSPDI(txt, arq) {
    var d = typeof DOMParser !== "undefined" ? new DOMParser().parseFromString(txt, "application/xml") : xmlMin(txt);
    if (d.getElementsByTagName("parsererror").length || !d.getElementsByTagName("Tasks").length) throw new Error("XML não reconhecido como MS Project (MSPDI)");
    var g = function (el, n) { for (var i = 0; i < el.children.length; i++) if (el.children[i].localName === n) return el.children[i].textContent.trim(); return ""; };
    var raiz = d.documentElement, ini = dataXER(g(raiz, "StartDate"));
    var base = Date.UTC((ini ? new Date(ini).getUTCFullYear() : 2000) - 2, 0, 1);
    var hd = num(g(raiz, "MinutesPerDay") || 480) / 60, cx = calendariosMSPDI(raiz, g, hd, base), pad = g(raiz, "CalendarUID");
    var pr = { id: "1", nome: g(raiz, "Name") || g(raiz, "Title") || arq, arquivo: arq, chave: arq + "#1",
      dataStatus: dataXER(g(raiz, "StatusDate")) || ini, inicioPlan: ini, terminoExigido: null, calPadrao: cx.cals[pad] ? pad : "_padrao",
      calendarios: cx.cals, at: {}, lig: [], alertas: cx.alertas, origem: null };
    var tasks = d.getElementsByTagName("Tasks")[0].children;
    for (var i = 0; i < tasks.length; i++) {
      var t = tasks[i]; if (g(t, "Summary") === "1" || g(t, "IsNull") === "1" || !g(t, "Name")) continue;
      var uid = g(t, "UID"), pc = num(g(t, "PercentComplete")), dur = horasISO(g(t, "Duration"));
      var rest = g(t, "RemainingDuration") ? horasISO(g(t, "RemainingDuration")) : dur;
      var fimR = dataXER(g(t, "ActualFinish")), iniR = dataXER(g(t, "ActualStart"));
      var stt = pc >= 100 || fimR != null ? "concluida" : pc > 0 || iniR != null ? "em_andamento" : "nao_iniciada";
      var ct = CT_DE[g(t, "ConstraintType")];
      pr.at[uid] = { uid: uid, cod: g(t, "WBS") || g(t, "ID") || uid, nome: g(t, "Name"), wbs: g(t, "OutlineNumber"),
        tipo: g(t, "Milestone") === "1" ? "marco_fim" : "tarefa", status: stt,
        durH: dur, restH: stt === "concluida" ? 0 : rest, cal: "", iniReal: iniR, fimReal: fimR,
        iniPlan: dataXER(g(t, "Start")), fimPlan: dataXER(g(t, "Finish")),
        restricoes: ct ? [{ tipo: ct, data: dataXER(g(t, "ConstraintDate")) }] : [], custo: num(g(t, "Cost")),
        custoReal: num(g(t, "ActualCost")), pctFisico: g(t, "PhysicalPercentComplete") ? num(g(t, "PhysicalPercentComplete")) : null,
        temRecurso: num(g(t, "Cost")) > 0, fonte: arq + " › Task UID " + uid };
      if (cx.cals[g(t, "CalendarUID")]) pr.at[uid].cal = g(t, "CalendarUID");
    }
    var TD = { "0": "FF", "1": "FS", "2": "SF", "3": "SS" };
    for (var j = 0; j < tasks.length; j++) {
      var tk = tasks[j], su = g(tk, "UID"); if (!pr.at[su]) continue;
      for (var k = 0; k < tk.children.length; k++) {
        var lk = tk.children[k]; if (lk.localName !== "PredecessorLink") continue;
        var pu = g(lk, "PredecessorUID"); if (pr.at[pu]) pr.lig.push({ p: pu, s: su, t: TD[g(lk, "Type") || "1"] || "FS", lag: num(g(lk, "LinkLag")) / 600 });
      }
    }
    pr.custo = sumCusto(pr);
    return [pr];
  }

  /* ---------------- CPM por datas ---------------- */
  function lag(cal, t, h, ini) { return Math.abs(h) < EPS ? t : cal.soma(t, h, ini); }
  function calcular(p, restH) {
    var ids = Object.keys(p.at).filter(function (u) { return noCalculo(p.at[u]); }), conj = {};
    ids.forEach(function (u) { conj[u] = true; });
    var ligs = p.lig.filter(function (l) { return conj[l.p] && conj[l.s]; }), Pd = {}, Sc = {}, grau = {};
    ids.forEach(function (u) { Pd[u] = []; Sc[u] = []; grau[u] = 0; });
    ligs.forEach(function (l) { Pd[l.s].push(l); Sc[l.p].push(l); grau[l.s]++; });
    var fila = ids.filter(function (u) { return grau[u] === 0; }), ordem = [], qi = 0;
    while (qi < fila.length) { var u0 = fila[qi++]; ordem.push(u0); Sc[u0].forEach(function (l) { if (--grau[l.s] === 0) fila.push(l.s); }); }
    if (ordem.length !== ids.length) {
      var presas = ids.filter(function (u) { return grau[u] > 0; }).slice(0, 10).map(function (u) { return p.at[u].cod; });
      throw new Error("Laço lógico (loop) no cronograma, envolvendo: " + presas.join(", "));
    }
    var dur = {}; ids.forEach(function (u) { dur[u] = restH && restH[u] !== undefined ? restH[u] : p.at[u].restH; });
    var dd = p.dataStatus || p.inicioPlan;
    if (dd == null) { var ds = ids.map(function (u) { return p.at[u].iniPlan; }).filter(Boolean); dd = ds.length ? Math.min.apply(null, ds) : Date.UTC(2000, 0, 3, 8); }
    var es = {}, ef = {}, avisos = [];
    ordem.forEach(function (u) {
      var a = p.at[u], cal = calDe(p, a);
      if (a.status === "concluida") { var i0 = a.iniReal || a.fimReal || dd; es[u] = i0; ef[u] = a.fimReal || i0; return; }
      var d = dur[u], cIni = cal.proximoInicio(dd), cFim = null;
      Pd[u].forEach(function (l) {
        var pcal = calDe(p, p.at[l.p]);
        if (a.status === "em_andamento" && (l.t === "SS" || l.t === "SF")) return;
        var alvo;
        if (l.t === "FS") cIni = Math.max(cIni, cal.proximoInicio(lag(pcal, ef[l.p], l.lag, true)));
        else if (l.t === "SS") cIni = Math.max(cIni, cal.proximoInicio(lag(pcal, es[l.p], l.lag, true)));
        else if (l.t === "FF") { alvo = cal.ultimoFim(lag(pcal, ef[l.p], l.lag, false)); cFim = cFim === null ? alvo : Math.max(cFim, alvo); }
        else { alvo = cal.ultimoFim(lag(pcal, es[l.p], l.lag, false)); cFim = cFim === null ? alvo : Math.max(cFim, alvo); }
      });
      a.restricoes.forEach(function (r) {
        if (!r.data || a.status === "em_andamento") return;
        if (r.tipo === "SNET") cIni = Math.max(cIni, cal.proximoInicio(r.data));
        else if (r.tipo === "MSO") cIni = cal.proximoInicio(r.data);
        else if (r.tipo === "FNET" || r.tipo === "MFO") { var al = cal.ultimoFim(r.data); cFim = (r.tipo === "MFO" || cFim === null) ? al : Math.max(cFim, al); }
      });
      if (cFim !== null) cIni = Math.max(cIni, d > EPS ? cal.soma(cFim, -d, true) : cFim);
      if (a.tipo === "marco_fim" && d <= EPS) { var f0 = cal.ultimoFim(cIni); if (cFim !== null) f0 = Math.max(f0, cFim); es[u] = ef[u] = f0; return; }
      var fim = d > EPS ? cal.soma(cIni, d, false) : cIni;
      if (a.status === "em_andamento") { es[u] = a.iniReal || cIni; ef[u] = fim; } else { es[u] = cIni; ef[u] = fim; }
    });
    var fimCedo = ordem.length ? Math.max.apply(null, ordem.map(function (u) { return ef[u]; })) : dd;
    var fimProj = p.terminoExigido || fimCedo, ls = {}, lf = {};
    for (var x = ordem.length - 1; x >= 0; x--) {
      var u = ordem[x], a = p.at[u], cal = calDe(p, a);
      if (a.status === "concluida") { ls[u] = es[u]; lf[u] = ef[u]; continue; }
      var d = dur[u], tFim = cal.ultimoFim(fimProj), tIni = null;
      Sc[u].forEach(function (l) {
        var sa = p.at[l.s]; if (sa.status === "concluida") return;
        var alvo;
        if (l.t === "FS") tFim = Math.min(tFim, cal.ultimoFim(lag(cal, ls[l.s], -l.lag, false)));
        else if (l.t === "FF") tFim = Math.min(tFim, cal.ultimoFim(lag(cal, lf[l.s], -l.lag, false)));
        else if (l.t === "SS") { if (sa.status === "em_andamento" || a.status === "em_andamento") return; alvo = cal.proximoInicio(lag(cal, ls[l.s], -l.lag, true)); tIni = tIni === null ? alvo : Math.min(tIni, alvo); }
        else { if (a.status === "em_andamento") return; alvo = cal.proximoInicio(lag(cal, lf[l.s], -l.lag, true)); tIni = tIni === null ? alvo : Math.min(tIni, alvo); }
      });
      a.restricoes.forEach(function (r) {
        if (!r.data) return;
        if (r.tipo === "FNLT" || r.tipo === "MFO") tFim = Math.min(tFim, cal.ultimoFim(r.data));
        else if ((r.tipo === "SNLT" || r.tipo === "MSO") && a.status !== "em_andamento") { var al = cal.proximoInicio(r.data); tIni = tIni === null ? al : Math.min(tIni, al); }
      });
      if (tIni !== null) tFim = Math.min(tFim, d > EPS ? cal.soma(tIni, d, false) : tIni);
      lf[u] = tFim; ls[u] = d > EPS ? cal.soma(tFim, -d, true) : tFim;
      if (a.status === "em_andamento") ls[u] = es[u];
    }
    var folgaH = {}, criticas = [];
    ordem.forEach(function (u) {
      var a = p.at[u]; if (a.status === "concluida") return;
      var cal = calDe(p, a), ff = cal.entre(ef[u], lf[u]);
      folgaH[u] = a.status === "em_andamento" ? ff : Math.min(cal.entre(es[u], ls[u]), ff);
      if (folgaH[u] <= EPS) criticas.push(u);
    });
    if (p.terminoExigido && fimCedo > p.terminoExigido) avisos.push("Término cedo " + fmtBR(fimCedo) + " após o término exigido " + fmtBR(p.terminoExigido));
    return { ordem: ordem, es: es, ef: ef, ls: ls, lf: lf, folgaH: folgaH, criticas: criticas, dataStatus: dd, termino: fimCedo, avisos: avisos, ligacoes: ligs };
  }
  function folgaDias(p, r, u) { return (r.folgaH[u] || 0) / calDe(p, p.at[u]).horasDia; }

  /* ---------------- DCMA-14 (regra A5) ---------------- */
  var BLOQ = { 1: 1, 3: 1, 6: 1, 7: 1, 11: 1 };
  function pct(n, t) { return t ? Math.round(1000 * n / t) / 10 : 0; }
  function dcma14(p, r) {
    r = r || calcular(p);
    var dd = r.dataStatus, ativs = Object.keys(p.at).map(function (u) { return p.at[u]; }).filter(noCalculo);
    var abertas = ativs.filter(function (a) { return a.status !== "concluida"; }), tarefas = abertas.filter(function (a) { return !marco(a); });
    var ligs = r.ligacoes, nA = abertas.length, tp = {}, tsx = {}, pts = [];
    ligs.forEach(function (l) { tp[l.s] = 1; tsx[l.p] = 1; });
    var cod = function (l) { return l.slice(0, 10).map(function (a) { return a.cod; }); };
    function pt(n, nome, valor, lim, ok, det, aplic, ex) { pts.push({ ponto: n, nome: nome, valor: valor, limite: lim, passou: aplic === false ? null : ok, aplicavel: aplic !== false, detalhe: det, exemplos: ex || [] }); }
    var sem = abertas.filter(function (a) { return (!tp[a.uid] && a.tipo !== "marco_inicio") || (!tsx[a.uid] && a.tipo !== "marco_fim"); });
    pt(1, "Lógica (sem predecessora ou sucessora)", pct(sem.length, nA) + "%", "≤ 5%", pct(sem.length, nA) <= 5, sem.length + " de " + nA + " abertas", true, cod(sem));
    var leads = ligs.filter(function (l) { return l.lag < -EPS; }); pt(2, "Leads (lag negativo)", leads.length, "0", !leads.length, leads.length + " ligações");
    var lags = ligs.filter(function (l) { return l.lag > EPS; }); pt(3, "Lags", pct(lags.length, ligs.length) + "%", "≤ 5%", pct(lags.length, ligs.length) <= 5, lags.length + " de " + ligs.length + " ligações");
    var fs = ligs.filter(function (l) { return l.t === "FS"; }); pt(4, "Ligações término-início (FS)", pct(fs.length, ligs.length) + "%", "≥ 90%", ligs.length ? pct(fs.length, ligs.length) >= 90 : true, fs.length + " de " + ligs.length + " ligações");
    var rig = abertas.filter(function (a) { return a.restricoes.some(function (x) { return ["MSO", "MFO", "SNLT", "FNLT"].indexOf(x.tipo) >= 0; }); });
    pt(5, "Restrições rígidas", pct(rig.length, nA) + "%", "≤ 5%", pct(rig.length, nA) <= 5, rig.length + " de " + nA + " abertas", true, cod(rig));
    var fd = function (a) { return (r.folgaH[a.uid] || 0) / calDe(p, a).horasDia; };
    var alta = abertas.filter(function (a) { return fd(a) > 44; }); pt(6, "Folga alta (> 44 dias úteis)", pct(alta.length, nA) + "%", "≤ 5%", pct(alta.length, nA) <= 5, alta.length + " de " + nA + " abertas", true, cod(alta));
    var neg = abertas.filter(function (a) { return (r.folgaH[a.uid] || 0) < -EPS; }); pt(7, "Folga negativa", neg.length, "0", !neg.length, neg.length + " atividades", true, cod(neg));
    var longas = tarefas.filter(function (a) { return a.restH / calDe(p, a).horasDia > 44; }); pt(8, "Duração alta (> 44 dias úteis)", pct(longas.length, tarefas.length) + "%", "≤ 5%", pct(longas.length, tarefas.length) <= 5, longas.length + " de " + tarefas.length + " tarefas", true, cod(longas));
    var inval = ativs.filter(function (a) { return (a.iniReal && a.iniReal > dd) || (a.fimReal && a.fimReal > dd); })
      .concat(abertas.filter(function (a) { return a.status === "nao_iniciada" && r.es[a.uid] < dd; }));
    pt(9, "Datas inválidas", inval.length, "0", !inval.length, inval.length + " atividades", true, cod(inval));
    var semRec = tarefas.filter(function (a) { return a.restH > EPS && !a.temRecurso; }); pt(10, "Tarefas sem recurso/custo", pct(semRec.length, tarefas.length) + "%", "0%", !semRec.length, semRec.length + " de " + tarefas.length + " tarefas", true, cod(semRec));
    var dev = ativs.filter(function (a) { return a.fimPlan && a.fimPlan <= dd; });
    var perd = dev.filter(function (a) { return !(a.status === "concluida" && a.fimReal && a.fimReal <= a.fimPlan); });
    pt(11, "Tarefas perdidas (proxy: datas planejadas)", pct(perd.length, dev.length) + "%", "≤ 5%", pct(perd.length, dev.length) <= 5, perd.length + " de " + dev.length + " devidas", dev.length > 0, cod(perd));
    var crA = r.criticas.filter(function (u) { return p.at[u].status !== "concluida"; });
    if (crA.length) {
      var u = crA[0], cal = calDe(p, p.at[u]), atraso = 100 * cal.horasDia, rr = {};
      Object.keys(p.at).forEach(function (k) { rr[k] = p.at[k].restH; }); rr[u] += atraso;
      var desl = cal.entre(r.termino, calcular(p, rr).termino);
      pt(12, "Teste do caminho crítico (+100 dias numa crítica)", Math.round(desl / cal.horasDia) + " d", "= 100 d", desl >= atraso - 1, "atividade testada " + p.at[u].cod);
    } else pt(12, "Teste do caminho crítico", "—", "= 100 d", null, "sem atividade crítica aberta", false);
    if (p.terminoExigido) {
      var c0 = p.calendarios[p.calPadrao] || p.calendarios._padrao, cpl = c0.entre(dd, r.termino), fp = c0.entre(r.termino, p.terminoExigido), cpli = cpl > EPS ? (cpl + fp) / cpl : 1;
      pt(13, "CPLI", cpli.toFixed(2), "≥ 0,95", cpli >= 0.95, "término exigido do projeto");
    } else pt(13, "CPLI", "—", "≥ 0,95", null, "projeto sem término exigido", false);
    var conc = ativs.filter(function (a) { return a.status === "concluida"; }), bei = dev.length ? conc.length / dev.length : null;
    pt(14, "BEI (proxy: datas planejadas)", bei === null ? "—" : bei.toFixed(2), "≥ 0,95", bei !== null && bei >= 0.95, conc.length + " concluídas / " + dev.length + " devidas", bei !== null);
    var ap = pts.filter(function (x) { return x.aplicavel; }), nota = ap.length ? ap.filter(function (x) { return x.passou; }).length / ap.length : 0;
    var bl = ap.filter(function (x) { return BLOQ[x.ponto] && !x.passou; }).map(function (x) { return x.ponto; });
    return { pontos: pts, nota: Math.round(nota * 1000) / 1000, aplicaveis: ap.length, aprovado: nota >= 0.9 && !bl.length, bloqueios: bl };
  }

  /* ---------------- Monte Carlo ---------------- */
  function monteCarlo(p, n, otim, pess) {
    n = n || 500; otim = otim || 0.9; pess = pess || 1.3;
    var seed = 42, rnd = function () { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
    var base = calcular(p), ids = base.ordem.filter(function (u) { return p.at[u].status !== "concluida"; }), fins = [];
    for (var i = 0; i < n; i++) {
      var d = {};
      ids.forEach(function (u) { var m = p.at[u].restH, a = m * otim, b = m * pess, c = m, x = rnd(), f = (c - a) / ((b - a) || 1);
        d[u] = x < f ? a + Math.sqrt(x * (b - a) * (c - a)) : b - Math.sqrt((1 - x) * (b - a) * (b - c)); });
      fins.push(calcular(p, d).termino);
    }
    fins.sort(function (a, b) { return a - b; });
    var q = function (x) { return fins[Math.min(Math.floor(x * n), n - 1)]; };
    return { n: n, deterministico: base.termino, p50: q(.5), p80: q(.8), p90: q(.9) };
  }

  /* ---------------- Exportação ---------------- */
  var CALC = ["early_start_date", "early_end_date", "late_start_date", "late_end_date", "total_float_hr_cnt"];
  function gravarXER(p, r) {
    var tb = p.origem; if (!tb) throw new Error("Projeto sem tabelas XER de origem (importado de outro formato)");
    var out = [tb.cabecalho];
    tb.ordem.forEach(function (nome) {
      var campos = (tb.campos[nome] || []).slice(), linhas = (tb.linhas[nome] || []).filter(function (x) { return !("proj_id" in x) || x.proj_id === p.id; });
      if (nome === "TASK" && r) CALC.forEach(function (c) { if (campos.indexOf(c) < 0) campos.push(c); });
      out.push("%T\t" + nome); out.push("%F\t" + campos.join("\t"));
      linhas.forEach(function (x) {
        var v = Object.assign({}, x), u = x.task_id;
        if (nome === "TASK" && r && r.es[u] !== undefined) {
          v.early_start_date = fmtXER(r.es[u]); v.early_end_date = fmtXER(r.ef[u]);
          v.late_start_date = fmtXER(r.ls[u]); v.late_end_date = fmtXER(r.lf[u]);
          if (r.folgaH[u] !== undefined) v.total_float_hr_cnt = r.folgaH[u].toFixed(1);
        }
        out.push("%R\t" + campos.map(function (c) { return v[c] === undefined ? "" : v[c]; }).join("\t"));
      });
    });
    out.push("%E");
    return out.join(tb.fimLinha) + tb.fimLinha;
  }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;" }[c]; }); }
  function iso(t) { return t == null ? "" : fmtXER(t).replace(" ", "T") + ":00"; }
  function durISO(h) { h = Math.max(h, 0); var i = Math.floor(h); return "PT" + i + "H" + Math.round((h - i) * 60) + "M0S"; }
  function semanaXML(cal) {
    var hh = function (x) { return p2(Math.floor(x) % 24) + ":" + p2(Math.round((x % 1) * 60)) + ":00"; }, s = "";
    for (var d = 0; d < 7; d++) {
      var iv = cal.semana[d] || [];
      s += "<WeekDay><DayType>" + ((d + 1) % 7 + 1) + "</DayType><DayWorking>" + (iv.length ? 1 : 0) + "</DayWorking>" +
        (iv.length ? "<WorkingTimes>" + iv.map(function (x) { return "<WorkingTime><FromTime>" + hh(x[0]) + "</FromTime><ToTime>" + hh(x[1]) + "</ToTime></WorkingTime>"; }).join("") + "</WorkingTimes>" : "") + "</WeekDay>";
    }
    return s;
  }
  function excecoesXML(cal) {
    var hh = function (x) { return p2(Math.floor(x) % 24) + ":" + p2(Math.round((x % 1) * 60)) + ":00"; };
    var ks = Object.keys(cal.excecoes).map(Number).sort(function (a, b) { return a - b; });
    if (!ks.length) return "";
    return "<Exceptions>" + ks.map(function (k) {
      var fx = cal.excecoes[k], d = fmtXER(k).slice(0, 10);
      return "<Exception><EnteredByOccurrences>0</EnteredByOccurrences><TimePeriod><FromDate>" + d + "T00:00:00</FromDate><ToDate>" + d + "T23:59:00</ToDate></TimePeriod><Occurrences>1</Occurrences><Type>1</Type><DayWorking>" + (fx.length ? 1 : 0) + "</DayWorking>" +
        (fx.length ? "<WorkingTimes>" + fx.map(function (x) { return "<WorkingTime><FromTime>" + hh(x[0]) + "</FromTime><ToTime>" + hh(x[1]) + "</ToTime></WorkingTime>"; }).join("") + "</WorkingTimes>" : "") + "</Exception>";
    }).join("") + "</Exceptions>";
  }
  function cstrXML(a) {
    var c = (a.restricoes || []).filter(function (x) { return CT_PARA[x.tipo]; })[0];
    return c ? "<ConstraintType>" + CT_PARA[c.tipo] + "</ConstraintType>" + (c.data != null ? "<ConstraintDate>" + iso(c.data) + "</ConstraintDate>" : "") : "";
  }
  function gravarMSPDI(p, r) {
    var padrao = p.calendarios[p.calPadrao] || p.calendarios._padrao, num0 = {}, preds = {}, usados = [padrao];
    r.ordem.forEach(function (u, i) { num0[u] = i + 1; var c = calDe(p, p.at[u]); if (usados.indexOf(c) < 0) usados.push(c); });
    r.ligacoes.forEach(function (l) { (preds[l.s] = preds[l.s] || []).push(l); });
    var TP = { FF: 0, FS: 1, SF: 2, SS: 3 };
    var cals = usados.map(function (c, i) { return "<Calendar><UID>" + (i + 1) + "</UID><Name>" + esc(c.nome) + "</Name><IsBaseCalendar>1</IsBaseCalendar><WeekDays>" + semanaXML(c) + "</WeekDays>" + excecoesXML(c) + "</Calendar>"; }).join("");
    var ini = r.ordem.length ? Math.min.apply(null, r.ordem.map(function (u) { return r.es[u]; })) : r.dataStatus;
    var x = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<Project xmlns="http://schemas.microsoft.com/project">',
      "<Name>" + esc(p.nome) + "</Name><Title>" + esc(p.nome) + "</Title><StartDate>" + iso(ini) + "</StartDate><StatusDate>" + iso(r.dataStatus) + "</StatusDate>",
      "<MinutesPerDay>" + Math.round(padrao.horasDia * 60) + "</MinutesPerDay><CalendarUID>1</CalendarUID>",
      "<Calendars>" + cals + "</Calendars>", "<Tasks>"];
    r.ordem.forEach(function (u) {
      var a = p.at[u], pc = a.status === "concluida" ? 100 : (a.status === "nao_iniciada" || a.durH <= 0 ? 0 : Math.max(0, Math.min(99, Math.floor(100 * (1 - a.restH / a.durH)))));
      x.push("<Task><UID>" + num0[u] + "</UID><ID>" + num0[u] + "</ID><Name>" + esc(a.nome) + "</Name><WBS>" + esc(a.cod) + "</WBS><OutlineLevel>1</OutlineLevel>" +
        "<Start>" + iso(r.es[u]) + "</Start><Finish>" + iso(r.ef[u]) + "</Finish><Duration>" + durISO(a.durH) + "</Duration><DurationFormat>7</DurationFormat>" +
        "<RemainingDuration>" + durISO(a.status === "concluida" ? 0 : a.restH) + "</RemainingDuration><Milestone>" + (marco(a) ? 1 : 0) + "</Milestone>" +
        "<PercentComplete>" + pc + "</PercentComplete><Cost>" + a.custo.toFixed(2) + "</Cost><ActualCost>" + (a.custoReal || 0).toFixed(2) + "</ActualCost>" +
        "<CalendarUID>" + (usados.indexOf(calDe(p, a)) + 1) + "</CalendarUID>" + cstrXML(a) +
        (a.iniReal ? "<ActualStart>" + iso(a.iniReal) + "</ActualStart>" : "") + (a.fimReal ? "<ActualFinish>" + iso(a.fimReal) + "</ActualFinish>" : "") +
        (preds[u] || []).map(function (l) { return "<PredecessorLink><PredecessorUID>" + num0[l.p] + "</PredecessorUID><Type>" + TP[l.t] + "</Type><LinkLag>" + Math.round(l.lag * 600) + "</LinkLag><LagFormat>7</LagFormat></PredecessorLink>"; }).join("") +
        "</Task>");
    });
    x.push("</Tasks>", "</Project>");
    return x.join("\n") + "\n";
  }

  /* ---------------- Curva S e valor agregado (porta de engine/evm.py) ---------------- */
  function fracao(cal, ini, fim, t) {
    if (t <= ini) return 0; if (t >= fim) return 1;
    var tot = cal.entre(ini, fim); return tot <= EPS ? 1 : Math.max(0, Math.min(1, cal.entre(ini, t) / tot));
  }
  function pctConcluido(a) {
    if (a.status === "concluida") return 1; if (a.status === "nao_iniciada") return 0;
    if (a.pctFisico !== null && a.pctFisico !== undefined && a.pctFisico > 0) return Math.max(0, Math.min(1, a.pctFisico / 100));
    return a.durH <= EPS ? 0 : Math.max(0, Math.min(1, 1 - a.restH / a.durH));
  }
  function janelas(p, r, u) { var a = p.at[u]; return (a.iniPlan != null && a.fimPlan != null) ? [a.iniPlan, a.fimPlan] : [r.es[u], r.ef[u]]; }
  function r2(x) { return x === null ? null : Math.round(x * 100) / 100; }
  function r3(x) { return x === null ? null : Math.round(x * 1000) / 1000; }
  function curvaS(p, r) {
    r = r || calcular(p);
    var ids = r.ordem, proxy = ids.some(function (u) { return p.at[u].iniPlan == null || p.at[u].fimPlan == null; }), datas = [];
    ids.forEach(function (u) { var j = janelas(p, r, u); datas.push(j[0], j[1], r.es[u], r.ef[u]); });
    if (!datas.length) return { meses: [], bac: 0, linhaDeBaseProxy: proxy };
    var t0 = Math.min.apply(null, datas), t1 = Math.max.apply(null, datas), bac = 0, peso = 0;
    ids.forEach(function (u) { bac += p.at[u].custo; peso += p.at[u].durH; }); peso = peso || 1;
    var meses = [], d0 = new Date(t0), ano = d0.getUTCFullYear(), mes = d0.getUTCMonth();
    for (;;) {
      mes++; if (mes === 12) { mes = 0; ano++; }
      var fim = Date.UTC(ano, mes, 1), cp = 0, cf = 0, fp = 0, ff = 0;
      ids.forEach(function (u) {
        var a = p.at[u], cal = calDe(p, a), j = janelas(p, r, u), fP = fracao(cal, j[0], j[1], fim), fF = fracao(cal, r.es[u], r.ef[u], fim);
        cp += a.custo * fP; cf += a.custo * fF; fp += a.durH * fP; ff += a.durH * fF;
      });
      var lab = new Date(fim - DIA);
      meses.push({ mes: lab.getUTCFullYear() + "-" + p2(lab.getUTCMonth() + 1), planejadoCusto: r2(cp), previstoCusto: r2(cf),
        planejadoFisicoPct: r2(100 * fp / peso), previstoFisicoPct: r2(100 * ff / peso) });
      if (fim > t1) break;
    }
    return { meses: meses, bac: r2(bac), linhaDeBaseProxy: proxy };
  }
  function valorAgregado(p, r) {
    r = r || calcular(p);
    var dd = r.dataStatus, bac = 0, pv = 0, ev = 0, ac = 0, real = false;
    r.ordem.forEach(function (u) {
      var a = p.at[u], cal = calDe(p, a), j = janelas(p, r, u);
      bac += a.custo; pv += a.custo * fracao(cal, j[0], j[1], dd); ev += a.custo * pctConcluido(a); ac += a.custoReal || 0;
      if ((a.custoReal || 0) > EPS) real = true;
    });
    var spi = pv > EPS ? ev / pv : null, cpi = real && ac > EPS ? ev / ac : null;
    return { dataStatus: dd, BAC: r2(bac), PV: r2(pv), EV: r2(ev), AC: real ? r2(ac) : null, SPI: r3(spi), CPI: r3(cpi),
      EAC: cpi ? r2(bac / cpi) : null, TCPI: real && Math.abs(bac - ac) > EPS ? r3((bac - ev) / (bac - ac)) : null,
      SV: r2(ev - pv), CV: real ? r2(ev - ac) : null,
      avisos: real ? [] : ["Sem custos reais (act_reg_cost/act_ot_cost) no cronograma: AC, CPI, EAC e TCPI não calculados"] };
  }

  /* ---------------- Linha do tempo de versões (porta de engine/versoes.py) ---------------- */
  function linhaDoTempo(projetos) {
    var calc = projetos.map(function (p) { try { return { p: p, r: p.r || calcular(p), erro: null }; } catch (e) { return { p: p, r: null, erro: e.message }; } });
    calc.sort(function (a, b) { return (a.p.dataStatus == null ? Infinity : a.p.dataStatus) - (b.p.dataStatus == null ? Infinity : b.p.dataStatus); });
    var versoes = [], ant = null, marcos = {};
    calc.forEach(function (c) {
      var l = { chave: c.p.chave, projeto: c.p.nome, dataStatus: c.p.dataStatus, atividades: Object.keys(c.p.at).length, custoTotal: r2(c.p.custo || sumCusto(c.p)), erro: c.erro };
      if (c.r) {
        l.termino = c.r.termino; l.criticas = c.r.criticas.length;
        if (ant) { l.deltaTerminoDias = Math.round((c.r.termino - ant.termino) / DIA * 10) / 10; l.deltaCusto = r2(l.custoTotal - ant.custoTotal); }
        ant = l;
        c.r.ordem.forEach(function (u) {
          var a = c.p.at[u]; if (!marco(a)) return;
          var m = marcos[a.cod] = marcos[a.cod] || { codigo: a.cod, nome: a.nome, datas: {} };
          m.datas[c.p.chave] = c.r.ef[u];
        });
      }
      versoes.push(l);
    });
    var tend = Object.keys(marcos).map(function (k) { return marcos[k]; }).filter(function (m) { return Object.keys(m.datas).length >= 2; });
    tend.forEach(function (m) {
      var ord = versoes.filter(function (v) { return m.datas[v.chave] !== undefined; }).map(function (v) { return v.chave; });
      m.deslizamentoDias = Math.round((m.datas[ord[ord.length - 1]] - m.datas[ord[0]]) / DIA * 10) / 10;
    });
    tend.sort(function (a, b) { return Math.abs(b.deslizamentoDias) - Math.abs(a.deslizamentoDias); });
    return { versoes: versoes, tendenciaMarcos: tend };
  }

  /* ---------------- Relatório do P6 impresso em PDF (layout de colunas) ----------------
   * Entrada: páginas de itens de texto {x, y, s} (y cresce para cima, como no pdf.js).
   * Saída: um projeto só de leitura (sem lógica): EAP, atividades, datas, durações.
   * Datas com "A" são reais; "*" (restrição) é ignorado. */
  function semAcento(s) { return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/\s+/g, " ").trim(); }
  var COL_PDF = [
    ["id", /(activity id|id da atividade|id atividade|codigo da atividade|^id$)/],
    ["nome", /(activity name|nome da atividade|descricao|^nome$|^atividade$)/],
    ["iniBL", /((baseline|bl project|linha de base|lb).*(start|inicio))/],
    ["fimBL", /((baseline|bl project|linha de base|lb).*(finish|termino|fim))/],
    ["rest", /(remaining|remanescente|restante)/],
    ["dur", /(original|duracao|duration)/],
    ["folga", /(total float|folga total|float|folga)/],
    ["pct", /(% ?complete|% ?conclu|concluid)/],
    ["ini", /(start|inicio)/],
    ["fim", /(finish|termino|^fim)/],
    ["cal", /(calendar|calendario)/],
    ["custo", /(cost|custo)/]
  ];
  var MESES = { jan: 0, fev: 1, feb: 1, mar: 2, abr: 3, apr: 3, mai: 4, may: 4, jun: 5, jul: 6, ago: 7, aug: 7, set: 8, sep: 8, out: 9, oct: 9, nov: 10, dez: 11, dec: 11 };
  var RE_DATA = /(\d{1,2})[\/.\-](\d{1,2}|[A-Za-zçÇ]{3})[\/.\-](\d{2,4})/;
  function numPDF(v) {
    var s = String(v || "").replace(/[^\d,.\-]/g, "");
    if (!s) return null;
    if (/,\d{1,2}$/.test(s)) s = s.replace(/\./g, "").replace(",", "."); else s = s.replace(/,/g, "");
    var n = parseFloat(s); return isFinite(n) ? n : null;
  }
  function linhasPDF(itens) {
    var ord = itens.filter(function (i) { return String(i.s).trim(); }).slice().sort(function (a, b) { return b.y - a.y || a.x - b.x; }), out = [];
    ord.forEach(function (i) {
      var l = out[out.length - 1];
      if (l && Math.abs(l.y - i.y) <= 2.5) l.itens.push(i); else out.push({ y: i.y, itens: [i] });
    });
    out.forEach(function (l) { l.itens.sort(function (a, b) { return a.x - b.x; }); l.texto = l.itens.map(function (i) { return i.s; }).join(" "); });
    return out;
  }
  function classificarCab(t) { t = semAcento(t); for (var i = 0; i < COL_PDF.length; i++) if (COL_PDF[i][1].test(t)) return COL_PDF[i][0]; return null; }
  function cabecalhoPDF(linhas, i0) {
    var zona = [linhas[i0]];
    for (var j = i0 + 1; j < linhas.length && linhas[i0].y - linhas[j].y < 28 && !RE_DATA.test(linhas[j].texto); j++) zona.push(linhas[j]);
    var grupos = [];
    zona.forEach(function (l) { l.itens.forEach(function (it) {
      var g = grupos.filter(function (g) { return Math.abs(g.x - it.x) < 18; })[0];
      if (g) g.t += " " + it.s; else grupos.push({ x: it.x, t: String(it.s) });
    }); });
    // itens do mesmo cabeçalho na mesma linha, lado a lado ("Activity" "ID") viram um só
    grupos.sort(function (a, b) { return a.x - b.x; });
    var cols = [], vistos = {};
    grupos.forEach(function (g) {
      var k = classificarCab(g.t);
      if (!k) { var ant = cols[cols.length - 1]; if (ant && !ant.k) { ant.t += " " + g.t; ant.k = classificarCab(ant.t); } else cols.push({ x: g.x, t: g.t, k: null }); return; }
      cols.push({ x: g.x, t: g.t, k: k });
    });
    cols = cols.filter(function (c) { if (!c.k || vistos[c.k]) return false; vistos[c.k] = 1; return true; });
    return { cols: cols, fim: i0 + zona.length };
  }
  function lerRelatorioPDF(paginas, arq) {
    var todas = [], datas = [], ehCab = function (l) { var t = semAcento(l.texto), n = 0; ["activity id", "id da atividade", "activity name", "nome da atividade", "start", "inicio", "finish", "termino"].forEach(function (k) { if (t.indexOf(k) >= 0) n++; }); return n >= 3; };
    paginas.forEach(function (itens, pg) { linhasPDF(itens).forEach(function (l) { l.pg = pg + 1; todas.push(l); }); });
    todas.forEach(function (l) { var m, re = new RegExp(RE_DATA.source, "g"); while ((m = re.exec(l.texto))) datas.push(m); });
    var dmy = !datas.some(function (m) { return /^\d+$/.test(m[2]) && +m[2] > 12; }) || datas.some(function (m) { return +m[1] > 12; });
    function dataPDF(v, fim) {
      var m = RE_DATA.exec(v || ""); if (!m) return null;
      var d = +m[1], mes = /^\d+$/.test(m[2]) ? +m[2] - 1 : MESES[semAcento(m[2]).slice(0, 3)], a = +m[3];
      if (!/^\d+$/.test(m[2]) || dmy) {} else { var t = d; d = mes + 1; mes = t - 1; }
      if (mes == null || mes < 0 || mes > 11 || d < 1 || d > 31) return null;
      if (a < 100) a += a < 70 ? 2000 : 1900;
      return Date.UTC(a, mes, d, fim ? 17 : 8, 0);
    }
    var base = Date.UTC(1990, 0, 1), cal = new Calendario("_padrao", "Padrão 5×8", null, null, 8, base);
    var pr = { id: "1", nome: arq, arquivo: arq, chave: arq + "#pdf", dataStatus: null, inicioPlan: null, terminoExigido: null, calPadrao: "_padrao",
      calendarios: { _padrao: cal }, at: {}, lig: [], alertas: [], origem: null, somenteLeitura: true, formato: "pdf", colunasPDF: [], eap: [] };
    var cab = null, ultimo = null, wbs = "", n = 0, colsUsadas = {}, sequencia = [];
    for (var i = 0; i < todas.length; i++) {
      var l = todas[i];
      if (ehCab(l)) { var c = cabecalhoPDF(todas, i); if (c.cols.length >= 3) { cab = c.cols; c.cols.forEach(function (k) { colsUsadas[k.k] = 1; }); i = c.fim - 1; ultimo = null; continue; } }
      if (!cab) continue;
      var larg = 80; for (var q = 1; q < cab.length; q++) larg = Math.max(larg, cab[q].x - cab[q - 1].x);
      var cel = {}, limite = cab[cab.length - 1].x + larg;
      l.itens.forEach(function (it) {
        if (it.x > limite) return;
        var col = cab[0]; cab.forEach(function (c) { if (c.x <= it.x + 6) col = c; });
        cel[col.k] = cel[col.k] ? cel[col.k] + " " + it.s : String(it.s);
      });
      var ini = dataPDF(cel.ini, false), fim = dataPDF(cel.fim, true), id = (cel.id || "").trim();
      var ehAtv = id && /^[A-Za-z0-9][\w.\-\/]*$/.test(id) && (ini != null || fim != null);
      if (!ehAtv && ini == null && fim == null) {
        // continuação do nome (quebra de linha no PDF)
        var soNome = Object.keys(cel).every(function (k) { return k === "nome" || k === "id"; });
        if (ultimo && soNome && cel.nome && ultimo.pg === l.pg) { ultimo.alvo.nome += " " + (cel.id ? cel.id + " " : "") + cel.nome; }
        continue;
      }
      if (!ehAtv) {
        var nomeW = ((cel.id ? cel.id + " " : "") + (cel.nome || "")).trim(); if (!nomeW) continue;
        var w = { nome: nomeW, ini: ini, fim: fim, pg: l.pg, nivel: 0, x: l.itens[0].x, idx: pr.eap.length };
        pr.eap.push(w); wbs = nomeW; ultimo = { alvo: w, pg: l.pg }; sequencia.push({ eap: w.idx });
        if (!pr.nomeDoPDF) pr.nomeDoPDF = w;
        continue;
      }
      var real0 = /\bA\b/.test(cel.ini || ""), real1 = /\bA\b/.test(cel.fim || "");
      var st = real1 ? "concluida" : real0 ? "em_andamento" : "nao_iniciada";
      var durD = numPDF(cel.dur), restD = numPDF(cel.rest);
      var i0 = ini != null ? ini : fim != null ? cal.proximoInicio(fim - 9 * H) : null, f0 = fim != null ? fim : ini;
      var durH = durD != null ? durD * 8 : (ini != null && fim != null ? cal.entre(cal.proximoInicio(ini), fim) : 0);
      var restH = st === "concluida" ? 0 : restD != null ? restD * 8 : durH;
      var mk = (durD === 0 || restD === 0 && st === "nao_iniciada" || ini == null || fim == null) && (ini == null || fim == null || ini >= fim - 10 * H && durH < EPS);
      if (mk && (real0 || real1)) st = "concluida";
      var uid = "p" + (++n);
      var a = pr.at[uid] = { uid: uid, cod: id, nome: (cel.nome || "").trim(), wbs: wbs, tipo: mk ? (fim == null ? "marco_inicio" : "marco_fim") : "tarefa", status: st,
        durH: mk ? 0 : durH, restH: mk ? 0 : restH, cal: "", iniReal: real0 ? ini : null, fimReal: real1 ? fim : null, iniPlan: dataPDF(cel.iniBL, false), fimPlan: dataPDF(cel.fimBL, true),
        restricoes: [], custo: numPDF(cel.custo) || 0, custoReal: 0, pctFisico: numPDF(cel.pct), temRecurso: !!numPDF(cel.custo),
        fonte: arq + " › página " + l.pg, iniPDF: i0, fimPDF: f0, folgaPDF: numPDF(cel.folga), calPDF: (cel.cal || "").trim() };
      a.eapIdx = pr.eap.length - 1; sequencia.push({ u: uid });
      ultimo = { alvo: a, pg: l.pg };
    }
    pr.colunasPDF = Object.keys(colsUsadas);
    // nível da EAP pelo recuo impresso; caminho de cada atividade até a raiz
    var xs = []; pr.eap.forEach(function (w) { var x = Math.round(w.x / 4) * 4; if (xs.indexOf(x) < 0) xs.push(x); });
    xs.sort(function (a, b) { return a - b; });
    var pilhaE = [];
    pr.eap.forEach(function (w) {
      w.nivel = xs.indexOf(Math.round(w.x / 4) * 4);
      while (pilhaE.length && pilhaE[pilhaE.length - 1].nivel >= w.nivel) pilhaE.pop();
      w.pai = pilhaE.length ? "e" + pilhaE[pilhaE.length - 1].idx : null; w.caminho = pilhaE.map(function (x) { return "e" + x.idx; }).concat(["e" + w.idx]);
      pilhaE.push(w);
    });
    pr.eapNos = pr.eap.map(function (w) { return { chave: "e" + w.idx, nome: w.nome, codigo: "", nivel: w.nivel, pai: w.pai, iniImpresso: w.ini, fimImpresso: w.fim }; });
    Object.keys(pr.at).forEach(function (u) { var a = pr.at[u]; a.eapCaminho = a.eapIdx >= 0 ? pr.eap[a.eapIdx].caminho : []; });
    pr.sequenciaPDF = sequencia;
    var ids = Object.keys(pr.at);
    if (!ids.length) throw new Error("Nenhuma atividade reconhecida: o PDF precisa ser um layout do P6/MS Project com colunas de ID, nome, início e término (texto, não imagem escaneada)");
    var txt = todas.map(function (l) { return l.texto; }).join("\n"), md = /(data date|data de status|data dos dados|data da atualiza\S*|status date)\D{0,12}(\d{1,2}[\/.\-](?:\d{1,2}|[A-Za-z]{3})[\/.\-]\d{2,4})/i.exec(txt);
    var reais = []; ids.forEach(function (u) { var a = pr.at[u]; if (a.fimReal != null) reais.push(a.fimReal); if (a.iniReal != null) reais.push(a.iniReal); });
    pr.dataStatus = md ? dataPDF(md[2], false) : reais.length ? Math.max.apply(null, reais) : Math.min.apply(null, ids.map(function (u) { return pr.at[u].iniPDF; }).filter(function (x) { return x != null; }));
    if (!md) pr.alertas.push("Data de status não encontrada no PDF: " + (reais.length ? "usada a última data real" : "usado o início do cronograma"));
    pr.alertas.push("Lido de PDF: sem lógica (predecessoras); datas e folgas são as impressas pelo P6, sem recálculo CPM");
    if (!colsUsadas.folga) pr.alertas.push("PDF sem coluna de folga total: caminho crítico não disponível");
    if (!colsUsadas.custo) pr.alertas.push("PDF sem coluna de custo: curva financeira e valor agregado vazios");
    if (pr.nomeDoPDF) pr.nome = pr.nomeDoPDF.nome; delete pr.nomeDoPDF;
    pr.custo = sumCusto(pr);
    return [pr];
  }
  /* Linhas da visão Primavera: faixas da EAP (com datas-resumo) e atividades, na ordem do P6. */
  function arvoreEAP(p, r) {
    var nos = (p.eapNos || []).map(function (n) { return { k: "eap", chave: n.chave, nome: n.nome, codigo: n.codigo, nivel: n.nivel, pai: n.pai, ini: null, fim: null, n: 0, custo: 0, criticas: 0 }; });
    var porChave = {}; nos.forEach(function (n) { porChave[n.chave] = n; });
    var noCalc = {}; r.ordem.forEach(function (u) { noCalc[u] = 1; });
    var semEAP = { k: "eap", chave: "_sem", nome: "(sem EAP)", codigo: "", nivel: 0, pai: null, ini: null, fim: null, n: 0, custo: 0, criticas: 0 };
    var crit = {}; r.criticas.forEach(function (u) { crit[u] = 1; });
    var atvDe = {};
    r.ordem.forEach(function (u) {
      var a = p.at[u], cam = (a.eapCaminho || []).filter(function (c) { return porChave[c]; }), folha = cam.length ? cam[cam.length - 1] : "_sem";
      (atvDe[folha] = atvDe[folha] || []).push(u);
      (cam.length ? cam.map(function (c) { return porChave[c]; }) : [semEAP]).forEach(function (n) {
        n.ini = n.ini == null ? r.es[u] : Math.min(n.ini, r.es[u]); n.fim = n.fim == null ? r.ef[u] : Math.max(n.fim, r.ef[u]);
        n.n++; n.custo += a.custo; if (crit[u]) n.criticas++;
      });
    });
    (p.eapNos || []).forEach(function (n) {           // PDF: vale o resumo impresso pelo P6
      var x = porChave[n.chave]; if (n.iniImpresso != null) x.ini = n.iniImpresso; if (n.fimImpresso != null) x.fim = n.fimImpresso;
    });
    var linhas = [], nivelDe = function (c) { return porChave[c] ? porChave[c].nivel + 1 : 1; };
    if (p.sequenciaPDF) {
      p.sequenciaPDF.forEach(function (x) {
        if (x.eap !== undefined) { var n = porChave["e" + x.eap]; if (n) linhas.push(n); }
        else if (noCalc[x.u]) { var a = p.at[x.u], c = a.eapCaminho || []; linhas.push({ k: "atv", u: x.u, nivel: c.length ? nivelDe(c[c.length - 1]) : 1, pai: c.length ? c[c.length - 1] : "_sem" }); }
      });
      if (atvDe._sem) { linhas.unshift(semEAP); }
    } else {
      var ordAt = function (lista) { return lista.slice().sort(function (a, b) { return r.es[a] - r.es[b] || String(p.at[a].cod).localeCompare(String(p.at[b].cod)); }); };
      var filhos = {}; nos.forEach(function (n) { (filhos[n.pai || ""] = filhos[n.pai || ""] || []).push(n); });
      (function dfs(pai) {
        (filhos[pai] || []).forEach(function (n) {
          if (!n.n) return;
          linhas.push(n);
          ordAt(atvDe[n.chave] || []).forEach(function (u) { linhas.push({ k: "atv", u: u, nivel: n.nivel + 1, pai: n.chave }); });
          dfs(n.chave);
        });
      })("");
      if (atvDe._sem) { linhas.push(semEAP); ordAt(atvDe._sem).forEach(function (u) { linhas.push({ k: "atv", u: u, nivel: 1, pai: "_sem" }); }); }
    }
    if (atvDe._sem && p.sequenciaPDF) linhas.forEach(function (l) { if (l.k === "atv" && l.pai === "_sem") l.nivel = 1; });
    return linhas;
  }

  /* Resultado no formato de calcular() a partir das datas impressas (projetos sem lógica). */
  function resultadoDasDatas(p) {
    var ordem = Object.keys(p.at).filter(function (u) { return p.at[u].iniPDF != null; }).sort(function (a, b) { return p.at[a].iniPDF - p.at[b].iniPDF; });
    var r = { ordem: ordem, es: {}, ef: {}, ls: {}, lf: {}, folgaH: {}, criticas: [], dataStatus: p.dataStatus, termino: null, avisos: [], ligacoes: [], semLogica: true };
    ordem.forEach(function (u) {
      var a = p.at[u]; r.es[u] = a.iniPDF; r.ef[u] = Math.max(a.fimPDF, a.iniPDF);
      if (a.status !== "concluida" && a.folgaPDF != null) { r.folgaH[u] = a.folgaPDF * 8; if (a.folgaPDF <= 0) r.criticas.push(u); }
      r.ls[u] = null; r.lf[u] = null;
      if (r.termino == null || r.ef[u] > r.termino) r.termino = r.ef[u];
    });
    return r;
  }

  var API = { lerXER: lerXER, lerMSPDI: lerMSPDI, lerClndrData: lerClndrData, Calendario: Calendario, calcular: calcular,
    folgaDias: folgaDias, dcma14: dcma14, monteCarlo: monteCarlo, gravarXER: gravarXER, gravarMSPDI: gravarMSPDI,
    eHistorico: eHistorico, dataXER: dataXER, fmtXER: fmtXER, fmtBR: fmtBR, calDe: calDe, noCalculo: noCalculo,
    curvaS: curvaS, valorAgregado: valorAgregado, pctConcluido: pctConcluido, linhaDoTempo: linhaDoTempo,
    lerRelatorioPDF: lerRelatorioPDF, arvoreEAP: arvoreEAP, linhasPDF: linhasPDF, resultadoDasDatas: resultadoDasDatas };
  if (typeof module !== "undefined" && module.exports) module.exports = API; else root.CronosEngine = API;
})(this);
