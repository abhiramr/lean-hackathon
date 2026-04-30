import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Activity, Shield, Terminal, Database, Play, CheckCircle2,
  XCircle, Clock, Upload, ChevronDown, Loader2, Wifi, WifiOff,
  FlaskConical, FileCode2, Award, Cpu, Zap, BarChart3,
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  ScatterChart, Scatter, CartesianGrid, Legend,
} from 'recharts';
import * as api from './lib/api';

// ── Lean code blocks for display ──
const LEAN_DEFS = `import Mathlib.Data.Rat.Basic
import Mathlib.Data.List.Basic

namespace VerifiedEDA

/-- Sum of a list of rationals. --/
def listSum : List ℚ → ℚ
  | [] => 0
  | (x :: xs) => x + listSum xs

/-- Length of a list as rational. --/
def listLen : List ℚ → ℚ
  | [] => 0
  | (_ :: xs) => 1 + listLen xs

/-- Arithmetic mean. --/
noncomputable def mean (xs : List ℚ) (h : xs ≠ []) : ℚ :=
  listSum xs / listLen xs

/-- Squared difference. --/
def sqDiff (x c : ℚ) : ℚ := (x - c) * (x - c)

/-- Population variance. --/
noncomputable def variance (xs : List ℚ) (h : xs ≠ []) : ℚ :=
  let m := mean xs h
  listSum (xs.map (sqDiff · m)) / listLen xs

end VerifiedEDA`;

const LEAN_PROOFS = `-- AGENT PIPELINE SAFETY PROOFS

theorem proven_requires_prover (r : VerifiedResult) (success : Bool) :
    (proverStep r success).status = .proven →
    (proverStep r success).prover_ran = true := by
  intro _; simp [proverStep]

theorem certifier_requires_prover (r : VerifiedResult)
    (h : r.prover_ran = false) :
    (certifierStep r).certifier_ran = false := by
  simp [certifierStep, h]

theorem pipeline_certifier_ran (r : VerifiedResult) (success : Bool) :
    (runPipeline r success).certifier_ran = true := by
  simp [runPipeline, certifierStep, proverStep]

theorem retryLoop_attempts_bounded (state : RetryState)
    (results : List AttemptResult) :
    (runRetryLoop state results).attempts_made
      ≤ state.attempts_made + results.length := by
  induction results generalizing state with
  | nil => simp [runRetryLoop]
  | cons r rs ih => ...`;

// ── Status Badge ──
function StatusBadge({ status }) {
  const cfg = {
    proven: { icon: CheckCircle2, cls: 'proof-proven', label: 'Proven' },
    failed: { icon: XCircle, cls: 'proof-failed', label: 'Failed' },
    pending: { icon: Clock, cls: 'proof-pending', label: 'Pending' },
  }[status] || { icon: Clock, cls: 'proof-pending', label: status };
  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono border ${cfg.cls}`}>
      <Icon size={11} /> {cfg.label}
    </span>
  );
}

// ── Stat Card ──
function StatCard({ label, value, icon: Icon, color = 'cyan', delay = 0 }) {
  const colors = {
    cyan: 'text-cyan-400 border-cyan-500/20 bg-cyan-500/5',
    purple: 'text-purple-400 border-purple-500/20 bg-purple-500/5',
    amber: 'text-amber-400 border-amber-500/20 bg-amber-500/5',
    pink: 'text-pink-400 border-pink-500/20 bg-pink-500/5',
    green: 'text-green-400 border-green-500/20 bg-green-500/5',
  };
  return (
    <div
      className={`glass-card p-4 border ${colors[color]} animate-slide-up`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-center gap-2 mb-2">
        {Icon && <Icon size={14} className="opacity-60" />}
        <span className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body">{label}</span>
      </div>
      <div className="font-mono text-xl font-semibold">
        {typeof value === 'number' ? value.toFixed(4) : value}
      </div>
    </div>
  );
}

// ── Connection Indicator ──
function ConnectionDot({ connected, label }) {
  return (
    <div className="flex items-center gap-2 text-xs font-mono">
      <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400 shadow-[0_0_6px_rgba(34,197,94,0.5)]' : 'bg-red-400 shadow-[0_0_6px_rgba(239,68,68,0.5)]'}`} />
      <span className="text-slate-500">{label}</span>
      <span className={connected ? 'text-green-400' : 'text-red-400'}>
        {connected ? 'CONNECTED' : 'OFFLINE'}
      </span>
    </div>
  );
}

// ── Correlation Heatmap ──
function Heatmap({ matrix, labels }) {
  if (!matrix || matrix.length === 0) return null;
  const n = labels.length;
  const cellSize = Math.min(56, 240 / n);
  const colorFor = (v) => {
    const t = (v + 1) / 2;
    const r = t < 0.5 ? 59 : Math.round(59 + (t - 0.5) * 2 * 195);
    const g = t < 0.5 ? Math.round(130 - (1 - t * 2) * 30) : Math.round(100 - (t - 0.5) * 2 * 30);
    const b = t < 0.5 ? Math.round(246 - (1 - t * 2) * 146) : Math.round(100 - (t - 0.5) * 2 * 60);
    return `rgb(${r},${g},${b})`;
  };
  return (
    <svg width={n * cellSize + 70} height={n * cellSize + 30} className="mx-auto">
      <g transform="translate(65, 5)">
        {matrix.map((row, i) => row.map((v, j) => (
          <g key={`${i}-${j}`}>
            <rect x={j * cellSize} y={i * cellSize} width={cellSize - 2} height={cellSize - 2} fill={colorFor(v)} rx={3} className="transition-all hover:opacity-80" />
            <text x={j * cellSize + cellSize / 2 - 1} y={i * cellSize + cellSize / 2 + 3} textAnchor="middle" fill="white" fontSize={9} fontFamily="JetBrains Mono" fontWeight={500}>{v.toFixed(2)}</text>
          </g>
        )))}
        {labels.map((l, i) => (
          <g key={`l-${i}`}>
            <text x={-8} y={i * cellSize + cellSize / 2 + 3} textAnchor="end" fill="#64748b" fontSize={9} fontFamily="JetBrains Mono">{l.slice(0, 7)}</text>
            <text x={i * cellSize + cellSize / 2 - 1} y={n * cellSize + 14} textAnchor="middle" fill="#64748b" fontSize={9} fontFamily="JetBrains Mono">{l.slice(0, 7)}</text>
          </g>
        ))}
      </g>
    </svg>
  );
}

// ═══════════════════════ MAIN APP ═══════════════════════
export default function App() {
  const [tab, setTab] = useState('analysis');
  const [backend, setBackend] = useState(null);
  const [leanStatus, setLeanStatus] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [activeDs, setActiveDs] = useState('');
  const [data, setData] = useState(null);
  const [edaResult, setEdaResult] = useState(null);
  const [verifyResult, setVerifyResult] = useState(null);
  const [selectedCol, setSelectedCol] = useState(0);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [agentLogs, setAgentLogs] = useState([]);
  const [leanBuilding, setLeanBuilding] = useState(false);
  const [leanBuildResult, setLeanBuildResult] = useState(null);
  const logRef = useRef(null);

  // ── Boot: check backend ──
  useEffect(() => {
    const check = async () => {
      try {
        const h = await api.fetchHealth();
        setBackend(h);
        const ls = await api.fetchLeanStatus();
        setLeanStatus(ls);
        const ds = await api.fetchDatasets();
        setDatasets(ds.datasets);
        if (ds.datasets.length > 0) setActiveDs(ds.datasets[0].name);
      } catch {
        setBackend(null);
      }
    };
    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  // ── Load dataset ──
  useEffect(() => {
    if (!activeDs || !backend) return;
    setLoading(true);
    setEdaResult(null);
    setVerifyResult(null);
    setAgentLogs([]);
    api.fetchDataset(activeDs).then(ds => {
      setData(ds);
      return api.runEDA(ds.data, ds.columns, ds.name, 12);
    }).then(result => {
      setEdaResult(result);
      setSelectedCol(0);
    }).catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [activeDs, backend]);

  // ── Run verification ──
  // const handleVerify = useCallback(async () => {
  //   if (!data || verifying) return;
  //   setVerifying(true);
  //   setVerifyResult(null);
  //   setAgentLogs([]);
  //   setTab('agents');

  //   try {
  //     const result = await api.runVerification(data.data, data.columns, data.name, 12);
  //     console.log('Verification result:', result);
  //     setVerifyResult(result);
  //     const logs = result.log || [];
  //     for (let i = 0; i < logs.length; i++) {
  //       await new Promise(r => setTimeout(r, 60));
  //       setAgentLogs(prev => [...prev, logs[i]]);
  //     }
  //     // Auto-switch to Proofs tab after logs finish
  //     setTab('proofs');
  //   } catch (err) {
  //     console.error('Verification failed:', err);
  //   }
  //   setVerifying(false);
  // }, [data, verifying]);
const handleVerify = useCallback(async () => {
    if (!data || verifying) return;
    setVerifying(true);
    setVerifyResult(null);
    setAgentLogs([]);
    setTab('agents');

    try {
      const result = await api.runVerification(data.data, data.columns, data.name, 12);
      console.log('Verification result:', result);
      const logs = result.log || [];
      for (let i = 0; i < logs.length; i++) {
        await new Promise(r => setTimeout(r, 60));
        setAgentLogs(prev => [...prev, logs[i]]);
      }
      setVerifyResult(result);
      await new Promise(r => setTimeout(r, 300));
      setTab('proofs');
    } catch (err) {
      console.error('Verification failed:', err);
    }
    setVerifying(false);
  }, [data, verifying]);

  // ── Build Lean ──
  const handleLeanBuild = useCallback(async () => {
    setLeanBuilding(true);
    setLeanBuildResult(null);
    try {
      const result = await api.buildLean();
      setLeanBuildResult(result);
    } catch (err) {
      setLeanBuildResult({ success: false, stderr: err.message });
    }
    setLeanBuilding(false);
  }, []);

  // ── CSV Upload ──
  const handleUpload = useCallback(async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const ds = await api.uploadCSV(file);
      setData(ds);
      setActiveDs(ds.name);
      const result = await api.runEDA(ds.data, ds.columns, ds.name, 12);
      setEdaResult(result);
      setSelectedCol(0);
    } catch (err) {
      console.error(err);
    }
  }, []);

  // Scroll agent log
  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [agentLogs]);

  const cols = edaResult?.columns || [];
  const stats = edaResult?.stats?.[cols[selectedCol]] || {};
  const proven = verifyResult?.proven || 0;
  const total = verifyResult?.total || edaResult?.total_operations || 0;
  const pct = total > 0 ? Math.round((proven / total) * 100) : 0;
  const isConnected = !!backend;

  const TABS = [
    { id: 'analysis', label: 'Analysis', icon: BarChart3 },
    { id: 'proofs', label: 'Proofs', icon: Shield },
    { id: 'agents', label: 'Agents', icon: Cpu },
    { id: 'lean', label: 'Lean 4', icon: FileCode2 },
  ];

  const agentIcon = (type) => ({ Translator: '⟳', Prover: '⊢', Certifier: '◈', Orchestrator: '◉' }[type] || '›');
  const agentColor = (type) => ({ Translator: 'text-purple-400', Prover: 'text-cyan-400', Certifier: 'text-amber-400', Orchestrator: 'text-pink-400' }[type] || 'text-slate-400');

  return (
    <div className="min-h-screen relative">
      <div className="noise-overlay" />

      {/* ─── BG glow ─── */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-[15%] w-[500px] h-[500px] bg-cyan-500/[0.03] rounded-full blur-[120px]" />
        <div className="absolute bottom-0 right-[10%] w-[400px] h-[400px] bg-purple-500/[0.03] rounded-full blur-[100px]" />
      </div>

      {/* ═══ HEADER ═══ */}
      <header className="sticky top-0 z-50 border-b border-white/[0.06] bg-void/80 backdrop-blur-xl">
        <div className="flex items-center justify-between px-6 h-16">
          <div className="flex items-center gap-4">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center font-mono font-bold text-void text-sm">
              V
            </div>
            <div>
              <h1 className="font-display font-bold text-base tracking-tight">VERIFIED EDA</h1>
              <p className="text-[10px] text-slate-500 tracking-[0.2em] uppercase font-mono">Mission Control</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            {/* Dataset selector */}
            <div className="relative">
              <select
                value={activeDs}
                onChange={(e) => setActiveDs(e.target.value)}
                className="appearance-none bg-white/[0.04] border border-white/[0.08] rounded-lg px-4 py-2 pr-8 text-xs font-mono text-slate-300 outline-none focus:border-cyan-500/30 cursor-pointer"
              >
                {datasets.map(d => (
                  <option key={d.name} value={d.name} className="bg-slate-900">{d.name}</option>
                ))}
              </select>
              <ChevronDown size={12} className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
            </div>

            {/* Upload */}
            <label className="flex items-center gap-2 px-3 py-2 rounded-lg border border-white/[0.08] text-xs font-mono text-slate-400 cursor-pointer hover:border-white/[0.15] transition-colors">
              <Upload size={13} />
              <span>CSV</span>
              <input type="file" accept=".csv" className="hidden" onChange={handleUpload} />
            </label>

            {/* Verify button */}
            <button
              onClick={handleVerify}
              disabled={verifying || !isConnected}
              className={`flex items-center gap-2 px-5 py-2 rounded-lg font-mono text-xs font-semibold tracking-wide transition-all ${
                verifying
                  ? 'bg-cyan-500/10 text-slate-500 border border-cyan-500/10'
                  : 'bg-gradient-to-r from-cyan-500/15 to-purple-500/15 border border-cyan-500/25 text-cyan-400 hover:border-cyan-400/40 hover:shadow-[0_0_20px_-4px_rgba(34,211,238,0.2)]'
              }`}
            >
              {verifying ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
              {verifying ? 'VERIFYING...' : 'RUN VERIFICATION'}
            </button>
          </div>
        </div>

        {/* ─── Status bar ─── */}
        <div className="flex items-center justify-between px-6 py-2 border-t border-white/[0.04] text-[11px] font-mono">
          <div className="flex items-center gap-6">
            <ConnectionDot connected={isConnected} label="Backend" />
            <ConnectionDot connected={!!leanStatus?.lean_installed} label="Lean 4" />
            {data && (
              <span className="text-slate-500">
                ROWS <span className="text-slate-300">{data.n_rows}</span>
                <span className="mx-2 text-slate-700">|</span>
                COLS <span className="text-slate-300">{data.n_cols}</span>
              </span>
            )}
          </div>
          <div className="flex items-center gap-4">
            <span className={proven === total && total > 0 ? 'text-green-400' : 'text-slate-500'}>
              VERIFIED {proven}/{total}
            </span>
            <div className="w-28 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${pct}%`,
                  background: pct === 100 ? '#22c55e' : 'linear-gradient(90deg, #22d3ee, #a78bfa)',
                }}
              />
            </div>
            <span className={`font-semibold ${pct === 100 ? 'text-green-400' : 'text-slate-400'}`}>{pct}%</span>
          </div>
        </div>
      </header>

      {/* ═══ TAB NAV ═══ */}
      <nav className="px-6 border-b border-white/[0.04] flex gap-0">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-5 py-3 text-xs font-mono uppercase tracking-[0.1em] border-b-2 transition-all ${
              tab === t.id
                ? 'border-cyan-400 text-cyan-400'
                : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
          >
            <t.icon size={13} />
            {t.label}
          </button>
        ))}
      </nav>

      {/* ═══ CONTENT ═══ */}
      <main className="p-6 relative z-10">

        {/* Not connected */}
        {!isConnected && (
          <div className="max-w-lg mx-auto mt-20 text-center">
            <WifiOff size={48} className="mx-auto text-red-400 mb-4" />
            <h2 className="font-display text-xl font-bold mb-2">Backend Not Connected</h2>
            <p className="text-slate-400 text-sm mb-6 font-body">Start the FastAPI server to use the full dashboard.</p>
            <div className="code-block text-left text-sm">
              <span className="text-slate-500"># Terminal 1: Start backend</span>{'\n'}
              <span className="text-cyan-400">cd</span> verified-eda-app{'\n'}
              <span className="text-cyan-400">pip install</span> -r backend/requirements.txt{'\n'}
              <span className="text-cyan-400">python</span> backend/server.py{'\n\n'}
              <span className="text-slate-500"># Terminal 2: Start frontend</span>{'\n'}
              <span className="text-cyan-400">npm install</span> && <span className="text-cyan-400">npm run</span> dev
            </div>
          </div>
        )}

        {/* ══════ ANALYSIS ══════ */}
        {isConnected && tab === 'analysis' && edaResult && (
          <div className="grid grid-cols-5 gap-6">
            {/* Left: column selector + stats */}
            <div className="col-span-3 space-y-6">
              {/* Column pills */}
              <div className="flex gap-2 flex-wrap">
                {cols.map((col, i) => (
                  <button
                    key={col}
                    onClick={() => setSelectedCol(i)}
                    className={`px-4 py-1.5 rounded-lg text-xs font-mono transition-all ${
                      selectedCol === i
                        ? 'bg-cyan-500/12 border border-cyan-500/30 text-cyan-400'
                        : 'bg-white/[0.03] border border-white/[0.06] text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {col}
                  </button>
                ))}
              </div>

              {/* Stat cards */}
              <div className="grid grid-cols-2 gap-3 stagger">
                <StatCard label="Mean" value={stats.mean?.value} icon={Activity} color="cyan" delay={0} />
                <StatCard label="Std Dev" value={stats.std?.value} icon={FlaskConical} color="purple" delay={60} />
                <StatCard label="Median" value={stats.median?.value} icon={BarChart3} color="amber" delay={120} />
                <StatCard label="Variance" value={stats.variance?.value} icon={Zap} color="pink" delay={180} />
              </div>

              {/* Range bar */}
              {stats.min && stats.max && (
                <div className="glass-card p-4">
                  <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body mb-3">Distribution Range</p>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-slate-400">{stats.min.value.toFixed(2)}</span>
                    <div className="flex-1 relative h-2 bg-white/[0.06] rounded-full">
                      <div className="absolute h-full bg-cyan-500/20 rounded-full" style={{
                        left: `${((stats.median?.value - stats.min.value) / ((stats.max.value - stats.min.value) || 1)) * 100 * 0.3}%`,
                        right: `${(1 - (stats.median?.value - stats.min.value) / ((stats.max.value - stats.min.value) || 1)) * 100 * 0.3}%`,
                      }} />
                      <div className="absolute top-[-3px] w-0.5 h-[14px] bg-amber-400 rounded" style={{
                        left: `${((stats.median?.value - stats.min.value) / ((stats.max.value - stats.min.value) || 1)) * 100}%`,
                      }} />
                    </div>
                    <span className="font-mono text-xs text-slate-400">{stats.max.value.toFixed(2)}</span>
                  </div>
                </div>
              )}

              {/* Histogram */}
              {edaResult.histograms?.[cols[selectedCol]] && (
                <div className="glass-card p-4">
                  <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body mb-3">Histogram</p>
                  <ResponsiveContainer width="100%" height={120}>
                    <BarChart data={edaResult.histograms[cols[selectedCol]].counts.map((c, i) => ({ bin: i, count: c }))}>
                      <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                        {edaResult.histograms[cols[selectedCol]].counts.map((_, i) => (
                          <Cell key={i} fill="rgba(34,211,238,0.35)" />
                        ))}
                      </Bar>
                      <XAxis dataKey="bin" hide />
                      <YAxis hide />
                      <Tooltip
                        contentStyle={{ background: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 11, fontFamily: 'JetBrains Mono' }}
                        labelStyle={{ color: '#64748b' }}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Right: correlation + summary */}
            <div className="col-span-2 space-y-6">
              {edaResult.correlation_matrix && (
                <div className="glass-card p-4">
                  <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body mb-3">Correlation Matrix</p>
                  <Heatmap matrix={edaResult.correlation_matrix} labels={cols} />
                </div>
              )}

              <div className="glass-card overflow-hidden">
                <div className="px-4 py-3 border-b border-white/[0.06]">
                  <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body">All Columns</p>
                </div>
                <table className="w-full text-xs font-mono">
                  <thead>
                    <tr className="border-b border-white/[0.04]">
                      {['Col', 'Mean', 'Std', 'Min', 'Max'].map(h => (
                        <th key={h} className="px-3 py-2 text-left text-slate-500 font-medium">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {cols.map((col, i) => {
                      const s = edaResult.stats[col] || {};
                      return (
                        <tr
                          key={col}
                          onClick={() => setSelectedCol(i)}
                          className={`border-b border-white/[0.02] cursor-pointer transition-colors ${
                            selectedCol === i ? 'bg-cyan-500/[0.04]' : 'hover:bg-white/[0.02]'
                          }`}
                        >
                          <td className={`px-3 py-2 ${selectedCol === i ? 'text-cyan-400' : ''}`}>{col}</td>
                          <td className="px-3 py-2 text-slate-400">{s.mean?.value?.toFixed(2)}</td>
                          <td className="px-3 py-2 text-slate-400">{s.std?.value?.toFixed(2)}</td>
                          <td className="px-3 py-2 text-slate-400">{s.min?.value?.toFixed(2)}</td>
                          <td className="px-3 py-2 text-slate-400">{s.max?.value?.toFixed(2)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ══════ PROOFS ══════ */}
      {isConnected && tab === 'proofs' && (() => {
          const certs = verifyResult && verifyResult.certificates ? verifyResult.certificates : [];
          return (
          <div style={{display:'flex',gap:24}}>
            <div style={{flex:1,maxHeight:'70vh',overflowY:'auto'}}>
              <p style={{fontSize:10,textTransform:'uppercase',letterSpacing:'0.15em',color:'#64748b',marginBottom:16}}>
                {'Certificates: ' + certs.length}
              </p>
              {certs.length === 0 && (
                <div style={{textAlign:'center',padding:'48px 0',color:'#64748b',fontSize:14}}>
                  Click Run Verification first.
                </div>
              )}
              {certs.map(function(cert, i) {
                var ok = cert.proof_status === 'proven';
                return React.createElement('div', {key: i, style: {
                  background: ok ? 'rgba(34,197,94,0.06)' : 'rgba(239,68,68,0.06)',
                  border: '1px solid ' + (ok ? 'rgba(34,197,94,0.2)' : 'rgba(239,68,68,0.2)'),
                  borderRadius: 8, padding: '12px 16px', marginBottom: 8,
                }},
                  React.createElement('div', {style: {display:'flex',alignItems:'center',gap:10}},
                    React.createElement('span', {style: {fontFamily:'JetBrains Mono',fontSize:14,fontWeight:700,color: ok ? '#22c55e' : '#ef4444'}}, ok ? '\u2713' : '\u2717'),
                    React.createElement('span', {style: {fontFamily:'JetBrains Mono',fontSize:12,color:'#e2e8f0',flex:1}}, cert.lean_theorem),
                    React.createElement('span', {style: {fontSize:11,color:'#64748b',fontFamily:'JetBrains Mono'}}, cert.column + '.' + cert.operation)
                  ),
                  React.createElement('div', {style: {marginTop:8,display:'flex',gap:16,fontSize:10,fontFamily:'JetBrains Mono',color:'#475569'}},
                    React.createElement('span', null, 'ID: ' + cert.certificate_id),
                    React.createElement('span', null, 'Hash: ' + cert.proof_hash),
                    React.createElement('span', null, 'Value: ' + (typeof cert.python_result === 'number' ? cert.python_result.toFixed(4) : cert.python_result))
                  )
                );
              })}
            </div>
            <div style={{flex:1}}>
              <p style={{fontSize:10,textTransform:'uppercase',letterSpacing:'0.15em',color:'#64748b',marginBottom:16}}>Lean 4 Definitions</p>
              <pre className="code-block text-[11px] leading-6" style={{maxHeight:320}}>{LEAN_DEFS}</pre>
              <p style={{fontSize:10,textTransform:'uppercase',letterSpacing:'0.15em',color:'#64748b',marginBottom:16,marginTop:24}}>Key Proofs</p>
              <pre className="code-block text-[11px] leading-6" style={{maxHeight:320}}>{LEAN_PROOFS}</pre>
            </div>
          </div>
          );
        })()}

        {/* ══════ AGENTS ══════ */}
        {isConnected && tab === 'agents' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body mb-2">Agent Activity Log</p>
              <div ref={logRef} className="code-block max-h-[400px] overflow-y-auto text-[11px] leading-7">
                {agentLogs.length === 0 && (
                  <span className="text-slate-600">Click "Run Verification" to see agent activity...</span>
                )}
                {agentLogs.map((log, i) => (
                  <div key={i} className="flex gap-2 animate-fade-in" style={{ animationDelay: `${i * 15}ms` }}>
                    <span className={agentColor(log.agent)}>{agentIcon(log.agent)}</span>
                    <span className={`${agentColor(log.agent)} min-w-[90px]`}>[{log.agent}]</span>
                    <span className="text-slate-300">{log.action} {log.column}.{log.operation}</span>
                    <span className={log.status === 'proven' || log.status === 'done' ? 'text-green-400' : log.status === 'failed' ? 'text-red-400' : 'text-slate-500'}>
                      → {log.status}
                    </span>
                    {log.details && <span className="text-slate-600 truncate">({log.details})</span>}
                  </div>
                ))}
                {verifying && (
                  <div className="flex items-center gap-2 text-cyan-400 mt-2">
                    <Loader2 size={12} className="animate-spin" /> Processing...
                  </div>
                )}
              </div>

              {/* Agent cards */}
              <div className="grid grid-cols-2 gap-3">
                {[
                  { name: 'Translator', desc: 'Python AST → Lean 4', color: 'purple', icon: '⟳' },
                  { name: 'Prover', desc: 'Tactic search & proof', color: 'cyan', icon: '⊢' },
                  { name: 'Certifier', desc: 'SHA-256 certificates', color: 'amber', icon: '◈' },
                  { name: 'Orchestrator', desc: 'Pipeline coordination', color: 'pink', icon: '◉' },
                ].map(a => (
                  <div key={a.name} className="glass-card p-3">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-${a.color}-400`}>{a.icon}</span>
                      <span className={`font-mono text-xs font-semibold text-${a.color}-400`}>{a.name}</span>
                    </div>
                    <p className="text-[10px] text-slate-500 font-body">{a.desc}</p>
                    <p className={`text-[10px] font-mono mt-1.5 ${verifying ? `text-${a.color}-400 animate-pulse` : 'text-slate-600'}`}>
                      {verifying ? 'ACTIVE' : (verifyResult ? 'COMPLETE' : 'IDLE')}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Architecture diagram */}
            <div className="space-y-4">
              <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body mb-2">Architecture</p>
              <div className="glass-card p-5">
                <svg viewBox="0 0 400 320" className="w-full">
                  <defs>
                    <marker id="arr" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
                      <polygon points="0 0, 8 3, 0 6" fill="#475569" />
                    </marker>
                  </defs>
                  {/* Boxes */}
                  <rect x="20" y="20" width="160" height="50" rx="8" fill="rgba(34,211,238,0.06)" stroke="#22d3ee" strokeWidth="1" />
                  <text x="100" y="42" textAnchor="middle" fill="#22d3ee" fontSize="11" fontFamily="JetBrains Mono" fontWeight="600">Python EDA</text>
                  <text x="100" y="58" textAnchor="middle" fill="#64748b" fontSize="9" fontFamily="JetBrains Mono">stats.py · pipeline.py</text>

                  <line x1="100" y1="70" x2="100" y2="100" stroke="#475569" markerEnd="url(#arr)" />

                  <rect x="20" y="100" width="160" height="50" rx="8" fill="rgba(167,139,250,0.06)" stroke="#a78bfa" strokeWidth="1" />
                  <text x="100" y="122" textAnchor="middle" fill="#a78bfa" fontSize="11" fontFamily="JetBrains Mono" fontWeight="600">⟳ Translator</text>
                  <text x="100" y="138" textAnchor="middle" fill="#64748b" fontSize="9" fontFamily="JetBrains Mono">AST → Lean 4</text>

                  <line x1="100" y1="150" x2="100" y2="180" stroke="#475569" markerEnd="url(#arr)" />

                  <rect x="20" y="180" width="160" height="50" rx="8" fill="rgba(34,211,238,0.06)" stroke="#22d3ee" strokeWidth="1" />
                  <text x="100" y="202" textAnchor="middle" fill="#22d3ee" fontSize="11" fontFamily="JetBrains Mono" fontWeight="600">Lean 4 Specs</text>
                  <text x="100" y="218" textAnchor="middle" fill="#64748b" fontSize="9" fontFamily="JetBrains Mono">Defs · Proofs</text>

                  <line x1="180" y1="205" x2="220" y2="205" stroke="#475569" markerEnd="url(#arr)" />

                  <rect x="220" y="100" width="160" height="50" rx="8" fill="rgba(34,211,238,0.06)" stroke="#22d3ee" strokeWidth="1" />
                  <text x="300" y="122" textAnchor="middle" fill="#22d3ee" fontSize="11" fontFamily="JetBrains Mono" fontWeight="600">⊢ Prover</text>
                  <text x="300" y="138" textAnchor="middle" fill="#64748b" fontSize="9" fontFamily="JetBrains Mono">Tactic search</text>

                  <line x1="300" y1="150" x2="300" y2="180" stroke="#475569" markerEnd="url(#arr)" />

                  <rect x="220" y="180" width="160" height="50" rx="8" fill="rgba(251,191,36,0.06)" stroke="#fbbf24" strokeWidth="1" />
                  <text x="300" y="202" textAnchor="middle" fill="#fbbf24" fontSize="11" fontFamily="JetBrains Mono" fontWeight="600">◈ Certifier</text>
                  <text x="300" y="218" textAnchor="middle" fill="#64748b" fontSize="9" fontFamily="JetBrains Mono">SHA-256</text>

                  <rect x="120" y="260" width="160" height="50" rx="8" fill="rgba(244,114,182,0.06)" stroke="#f472b6" strokeWidth="1" />
                  <text x="200" y="282" textAnchor="middle" fill="#f472b6" fontSize="11" fontFamily="JetBrains Mono" fontWeight="600">◉ Orchestrator</text>
                  <text x="200" y="298" textAnchor="middle" fill="#64748b" fontSize="9" fontFamily="JetBrains Mono">Coordinates all</text>

                  <line x1="100" y1="230" x2="160" y2="260" stroke="#475569" strokeDasharray="4" />
                  <line x1="300" y1="230" x2="240" y2="260" stroke="#475569" strokeDasharray="4" />
                </svg>
              </div>
            </div>
          </div>
        )}

        {/* ══════ LEAN TAB ══════ */}
        {isConnected && tab === 'lean' && (
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-4">
              <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body mb-2">Lean 4 Environment</p>

              <div className="glass-card p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">Lean Binary</span>
                  <span className={`text-xs font-mono ${leanStatus?.lean_installed ? 'text-green-400' : 'text-red-400'}`}>
                    {leanStatus?.lean_installed ? leanStatus.lean_path : 'Not found'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">Version</span>
                  <span className="text-xs font-mono text-slate-300">{leanStatus?.lean_version || '—'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">Lake</span>
                  <span className={`text-xs font-mono ${leanStatus?.lake_available ? 'text-green-400' : 'text-slate-500'}`}>
                    {leanStatus?.lake_available ? 'Available' : 'Not found'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-slate-400">Project</span>
                  <span className={`text-xs font-mono ${leanStatus?.lean_project_found ? 'text-green-400' : 'text-slate-500'}`}>
                    {leanStatus?.lean_project_found ? '✓ Found' : 'Not found'}
                  </span>
                </div>
              </div>

              <button
                onClick={handleLeanBuild}
                disabled={leanBuilding || !leanStatus?.lean_installed}
                className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-mono text-xs font-semibold transition-all ${
                  leanBuilding
                    ? 'bg-amber-500/10 border border-amber-500/20 text-amber-400'
                    : 'bg-green-500/10 border border-green-500/20 text-green-400 hover:bg-green-500/15'
                }`}
              >
                {leanBuilding ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
                {leanBuilding ? 'Building (this may take a while)...' : 'Build & Type-Check Proofs'}
              </button>

              {leanBuildResult && (
                <div className={`glass-card p-4 border ${leanBuildResult.success ? 'border-green-500/20' : 'border-red-500/20'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    {leanBuildResult.success ? <CheckCircle2 size={14} className="text-green-400" /> : <XCircle size={14} className="text-red-400" />}
                    <span className={`text-xs font-mono font-bold ${leanBuildResult.success ? 'text-green-400' : 'text-red-400'}`}>
                      {leanBuildResult.success ? 'ALL PROOFS TYPE-CHECKED ✓' : 'BUILD FAILED'}
                    </span>
                  </div>
                  {leanBuildResult.stderr && (
                    <pre className="code-block text-[10px] max-h-[200px] mt-2">{leanBuildResult.stderr}</pre>
                  )}
                </div>
              )}

              {!leanStatus?.lean_installed && (
                <div className="glass-card p-4 border border-amber-500/20">
                  <p className="text-xs font-body text-amber-400 mb-2">Lean 4 is not installed</p>
                  <div className="code-block text-[10px]">
                    curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y{'\n'}
                    source ~/.profile
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-4">
              <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body mb-2">Proof Files</p>

              {['Defs.lean', 'Proofs.lean', 'Advanced.lean'].map((file) => (
                <div key={file} className="glass-card p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <FileCode2 size={13} className="text-cyan-400" />
                    <span className="font-mono text-xs text-cyan-400">{file}</span>
                    <span className="text-[10px] text-slate-600 font-mono">lean/VerifiedEDA/</span>
                  </div>
                  <p className="text-[10px] text-slate-500 font-body">
                    {file === 'Defs.lean' && 'Core definitions: listSum, listLen, mean, variance, sqDiff, innerProd'}
                    {file === 'Proofs.lean' && 'Machine-checked proofs: variance_nonneg, sqDiff_nonneg, listSum_nonneg'}
                    {file === 'Advanced.lean' && 'Cauchy-Schwarz, histogram conservation, algebraic lemmas'}
                  </p>
                </div>
              ))}

              <div className="glass-card p-4">
                <p className="text-[10px] uppercase tracking-[0.15em] text-slate-500 font-body mb-3">Theorem Status</p>
                <div className="space-y-2 font-mono text-xs">
                {[
                    ['variance_nonneg', true], ['sqDiff_nonneg', false], ['listSum_nonneg', true],
                    ['listLen_pos', true], ['innerProd_self_nonneg', false], ['listSum_append', true],
                    ['binTotal_append', true],
                    ['-- Agent Pipeline --', null],
                    ['proven_requires_prover', true], ['certifier_requires_prover', true],
                    ['pipeline_certifier_ran', true], ['pipeline_prover_ran', true],
                    ['pipelineAll_all_prover_ran', true], ['pipelineAll_all_certifier_ran', true],
                    ['retryStep_increments', true], ['retryLoop_attempts_bounded', true],
                    ['retryLoop_finds_first_success', true],
                  ].map(([name, proven]) => (
                    <div key={name} className="flex items-center gap-2">
                      <span className={proven === null ? 'text-slate-500' : proven ? 'text-green-400' : 'text-amber-400'}>
                        {proven === null ? '--' : proven ? '✓' : '◻'}
                      </span>
                      <span className={proven === null ? 'text-slate-500 font-bold' : 'text-slate-300'}>{name}</span>
                      <span className={`text-[10px] ml-auto ${proven === null ? '' : proven ? 'text-green-400/60' : 'text-amber-400/60'}`}>
                        {proven === null ? '' : proven ? 'proven' : 'sorry'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Loading */}
        {isConnected && loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={32} className="text-cyan-400 animate-spin" />
          </div>
        )}
      </main>
    </div>
  );
}