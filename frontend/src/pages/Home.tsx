import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Bell,
  Bot,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  Copy,
  Fingerprint,
  GitBranch,
  HelpCircle,
  History,
  LockKeyhole,
  Menu,
  Network,
  Play,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
  Sparkles,
  Terminal,
  UserRound,
  X,
  Zap,
} from "lucide-react";

type Decision = {
  id: string;
  source?: string;
  outcome?: "APPROVE" | "REVIEW" | "BLOCK";
  risk_score?: number;
  proposal?: {
    customer_name?: string;
    amount?: number;
    currency?: string;
  };
  ai_decision?: string;
  fingguard_decision?: string;
  final_decision?: string;
  gateway_status?: string;
  reason?: string;
  reasons?: string[];
  stages?: { label: string; status?: string; detail?: string }[];
  chain_hashes?: string[];
};

type QueueItem = {
  id: string;
  decision_id: string;
  transaction_id?: string;
  customer_name?: string;
  amount?: number;
  risk_score?: number;
  status: string;
  reason?: string;
};

const money = (n = 0) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(n);

const api = async <T,>(path: string, options?: RequestInit): Promise<T> => {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
};

const outcomeClass = (value?: string) => {
  if (value === "BLOCK" || value === "REJECTED") return "danger";
  if (value === "REVIEW" || value === "OPEN") return "warning";
  return "success";
};

const stageIcon = (label: string) => {
  const map: Record<string, React.ReactNode> = {
    State: <Activity size={16} />,
    Balance: <CircleDollarSign size={16} />,
    Evidence: <Fingerprint size={16} />,
    Policy: <ShieldAlert size={16} />,
    Behaviour: <Zap size={16} />,
    Risk: <AlertTriangle size={16} />,
  };
  return map[label] || <Shield size={16} />;
};

export default function Home() {
  const [decision, setDecision] = useState<Decision | null>(null);
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [recent, setRecent] = useState<Decision[]>([]);
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [active, setActive] = useState("command");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [error, setError] = useState("");

  const selectDecision = (item: Decision) => {
    const outcome = item.fingguard_decision || item.outcome || item.final_decision || "BLOCK";
    const amt = item.proposal?.amount || 5000;
    const score = item.risk_score ?? 65;

    const formatted: Decision = {
      ...item,
      id: item.id || `txn_fg_${Date.now()}`,
      outcome: outcome as any,
      risk_score: score,
      proposal: {
        customer_name: item.proposal?.customer_name || "Customer",
        amount: amt,
        currency: "INR",
      },
      ai_decision: item.ai_decision || "APPROVE",
      fingguard_decision: outcome,
      gateway_status: outcome === "BLOCK" ? "EXECUTION_PREVENTED" : outcome === "REVIEW" ? "AWAITING_HUMAN" : "EXECUTED",
      reasons: item.reasons || [item.reason || "Evaluated by FinGuard execution firewall."],
      stages: item.stages || [
        { label: "State", status: outcome === "BLOCK" ? "Mismatch" : "Verified", detail: outcome === "BLOCK" ? "Conflict" : "State ok" },
        { label: "Balance", status: outcome === "BLOCK" ? "Over limit" : "Verified", detail: `₹${amt.toLocaleString("en-IN")} request` },
        { label: "Evidence", status: score > 30 ? "Incomplete" : "Complete", detail: score > 30 ? "Missing proof" : "Evidence verified" },
        { label: "Policy", status: outcome === "BLOCK" ? "Violated" : "Passed", detail: outcome === "BLOCK" ? "Policy block" : "Policy ok" },
        { label: "Behaviour", status: score >= 70 ? "Anomaly" : "Normal", detail: `${score >= 70 ? "HIGH" : score >= 30 ? "MEDIUM" : "LOW"} risk` },
        { label: "Risk", status: `${score}/100`, detail: score >= 70 ? "HIGH" : score >= 30 ? "MEDIUM" : "LOW" },
      ],
      chain_hashes: item.chain_hashes || [
        "a8f5c9e2b1d4073f9182a4c6e80123ef4567890abcdef1234567890abcdef12",
        "7e4b9a1c0d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
      ],
    };
    setDecision(formatted);
  };

  const loadData = async () => {
    try {
      const [dash, q, r] = await Promise.all([
        api<any>("/dashboard"),
        api<QueueItem[]>("/review-queue"),
        api<Decision[]>("/firewall/recent"),
      ]);
      setDashboard(dash);
      setQueue(q || []);
      setRecent(r || []);
      if (r && r.length > 0) {
        selectDecision(r[0]);
      }
    } catch {
      // The UI still works as a static recruiter demo if the backend is unavailable.
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const reviewAction = async (id: string, action: "approve" | "reject") => {
    try {
      await api(`/review-queue/${id}/action`, {
        method: "POST",
        body: JSON.stringify({ action }),
      });
      await loadData();
    } catch {
      setError("Could not update this review item.");
    }
  };

  const metrics = useMemo(
    () => ({
      volume: dashboard?.refund_volume ?? "₹1.4L",
      proposals: dashboard?.proposal_count ?? 41,
      blocked: dashboard?.blocked_actions ?? 20,
      reviews: queue.filter((x) => x.status === "OPEN").length || (dashboard?.review_queue ?? 11),
      catchRate: dashboard?.catch_rate ?? "48.8%",
      latency: dashboard?.latency ?? "1.251ms median / 1.936ms P95",
    }),
    [dashboard, queue]
  );

  const nav = [
    ["command", "Overview", BarChart3],
    ["live-decision", "Live Decisions", Activity],
    ["review", "Review Queue", UserRound],
    ["red-team", "Red Team Lab", ShieldAlert],
    ["risk-graph", "Risk Graph", Network],
    ["benchmarks", "Benchmarks", BarChart3],
    ["audit", "Audit Trail", History],
    ["gateway-control", "Gateway Control", Shield],
  ] as const;

  const scrollTo = (id: string) => {
    setActive(id);
    setMobileOpen(false);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const scenarios = [
    ["over_refund", "Over-refund", "₹5,000 request vs ₹3,000 balance", ArrowRight],
    ["duplicate_refund", "Duplicate refund", "Order fingerprint replay", Copy],
    ["prompt_injection", "Prompt injection", "Instruction tries to bypass policy", Terminal],
    ["velocity_anomaly", "Velocity anomaly", "7 refunds in the recent window", Activity],
    ["device_hopping", "Device hopping", "4 devices linked to one request", Fingerprint],
    ["ai_hallucination", "AI hallucination", "Non-existent policy claim", Sparkles],
  ] as const;

  const graphNodes = [
    { x: 10, y: 50, label: decision?.proposal?.customer_name || "Aarav Mehta", type: "Customer", danger: true },
    { x: 34, y: 28, label: `${money(decision?.proposal?.amount || 5000)} refund`, type: "Transaction", danger: true },
    { x: 57, y: 23, label: "Card ••••4242", type: "Card" },
    { x: 82, y: 52, label: "FinGuard Store", type: "Merchant" },
    { x: 34, y: 76, label: "dev_7419", type: "Device", medium: true },
    { x: 57, y: 82, label: "103.86.18.40", type: "IP", medium: true },
  ];

  const benchmarkRows =
    dashboard?.benchmarks?.length
      ? dashboard.benchmarks
      : [
          { strategy: "FinGuard", precision: 82.26, recall: 100.0, latency: "1.251ms", prevented: 47 },
          { strategy: "Always Approve", precision: 0, recall: 0, latency: "0.002ms", prevented: 0 },
          { strategy: "Amount Threshold", precision: 93.33, recall: 13.73, latency: "0.025ms", prevented: 26 },
        ];

  return (
    <div className="fg-app">
      <style>{`
        :root{
          --navy:#062b54; --navy2:#062542; --blue:#0b8df3; --blue2:#dff0ff;
          --bg:#f5f8fc; --line:#dce5ef; --text:#07172e; --muted:#68809b;
          --green:#00a66a; --red:#ff4d55; --amber:#f2a900; --white:#fff;
        }
        *{box-sizing:border-box}
        html{scroll-behavior:smooth}
        body{margin:0;background:var(--bg);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--text)}
        button{font:inherit}
        .fg-app{min-height:100vh;background:#f5f8fc}
        .sidebar{position:fixed;left:0;top:0;bottom:0;width:226px;background:#062e5b;color:#fff;z-index:50;display:flex;flex-direction:column}
        .brand{height:74px;padding:18px 20px;border-bottom:1px solid rgba(255,255,255,.13);display:flex;align-items:center;gap:10px}
        .brandmark{width:30px;height:30px;border-radius:8px;background:#168df0;display:grid;place-items:center;font-weight:900}
        .brandname{font-size:16px;font-weight:800;line-height:1}
        .brandsub{font-size:9px;letter-spacing:1.8px;color:#b8d9f8;margin-top:4px}
        .side-title{font-size:10px;letter-spacing:1.8px;color:#a9c8e9;font-weight:800;padding:25px 20px 10px}
        .workspace{margin:4px 14px 12px;padding:12px;border-radius:8px;background:rgba(255,255,255,.1);display:flex;gap:10px;align-items:center}
        .store-icon{width:30px;height:30px;border-radius:50%;background:#6b7f95;display:grid;place-items:center;font-size:11px;font-weight:800}
        .workspace b{font-size:13px}.workspace span{display:block;font-size:10px;color:#c3d7eb;margin-top:3px}
        .nav{padding:0 10px;display:flex;flex-direction:column;gap:3px}
        .nav button{border:0;background:transparent;color:#d9e7f6;text-align:left;padding:10px 12px;border-radius:7px;display:flex;align-items:center;gap:10px;font-size:13px;cursor:pointer}
        .nav button:hover,.nav button.active{background:rgba(255,255,255,.12);color:#fff}
        .nav .badge{margin-left:auto;background:#ff4650;color:#fff;border-radius:10px;padding:2px 6px;font-size:10px}
        .side-bottom{margin-top:auto;padding:14px}.online{border:1px solid rgba(255,255,255,.17);background:rgba(255,255,255,.06);border-radius:8px;padding:11px;font-size:11px;color:#cfe0f1}.online b{display:block;color:#fff;margin-bottom:5px}
        .main{margin-left:226px;min-height:100vh}
        .topbar{height:74px;background:#fff;border-bottom:1px solid var(--line);display:flex;align-items:center;padding:0 28px;position:sticky;top:0;z-index:30}
        .top-title{font-size:15px;font-weight:800}.top-sub{font-size:11px;color:var(--muted);margin-top:3px}
        .top-actions{margin-left:auto;display:flex;align-items:center;gap:17px}.gateway{border:1px solid #b7f1d8;background:#effdf6;color:#00925d;padding:7px 12px;border-radius:18px;font-size:11px;font-weight:700}
        .avatar{width:32px;height:32px;border-radius:50%;background:#092d57;color:#fff;display:grid;place-items:center;font-size:11px;font-weight:800}.operator{font-size:11px;font-weight:700}.operator small{display:block;color:var(--muted);font-weight:500;margin-top:2px}
        .content{padding:28px 49px 70px;max-width:1600px;margin:auto}
        .hero{display:flex;align-items:end;justify-content:space-between;margin-bottom:20px}.eyebrow{display:inline-flex;gap:7px;align-items:center;color:#168df0;background:#eef7ff;border:1px solid #b8dcff;border-radius:15px;padding:4px 10px;font-size:9px;font-weight:800;letter-spacing:1px}.hero h1{font-size:36px;letter-spacing:-1.7px;margin:9px 0 2px}.hero p{font-size:12px;color:var(--muted);margin:0}
        .primary{border:0;background:#0c94f5;color:#fff;border-radius:8px;padding:12px 17px;font-weight:800;font-size:12px;display:flex;align-items:center;gap:8px;cursor:pointer;box-shadow:0 5px 12px rgba(12,148,245,.2)}.primary:disabled{opacity:.6;cursor:wait}
        .metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
        .metric{background:#fff;border:1px solid #d8e1eb;border-radius:10px;padding:17px;box-shadow:0 1px 2px rgba(10,30,60,.03);user-select:none;-webkit-user-select:none;caret-color:transparent;cursor:default;outline:none}
        .metric-top{display:flex;justify-content:space-between;color:#58728f;font-size:10px;letter-spacing:1.3px;font-weight:800;user-select:none;-webkit-user-select:none;caret-color:transparent}
        .metric-icon{width:31px;height:31px;border-radius:8px;background:#edf7ff;color:#0c94f5;display:grid;place-items:center}
        .metric:nth-child(2) .metric-icon{background:#fff0f1;color:var(--red)}
        .metric:nth-child(3) .metric-icon{background:#fff8e6;color:#d99700}
        .metric:nth-child(4) .metric-icon{background:#effcf7;color:var(--green)}
        .metric-value{font-size:23px;font-weight:900;margin-top:7px;user-select:none;-webkit-user-select:none;caret-color:transparent;cursor:default;outline:none}
        .metric-desc{font-size:10px;color:var(--muted);margin-top:3px;user-select:none;-webkit-user-select:none;caret-color:transparent}
        .panel{background:#fff;border:1px solid #d7e1ec;border-radius:10px;margin-bottom:20px;overflow:hidden}.panel-head{padding:18px 22px 13px}.section-label{font-size:9px;letter-spacing:1.8px;color:#1589eb;font-weight:900}.panel h2{font-size:20px;letter-spacing:-.5px;margin:5px 0}.panel-sub{font-size:11px;color:var(--muted)}
        .firewall{background:#062642;color:#fff;border-radius:12px;padding:22px;margin-bottom:20px}.firewall-top{display:flex;align-items:center;gap:7px;font-size:9px;letter-spacing:1px;color:#79baff;font-weight:900}.live-dot{width:7px;height:7px;border-radius:50%;background:#ff4b55}.firewall h2{font-size:20px;margin:7px 0 3px}.firewall p{font-size:11px;color:#b7cce2;margin:0}.firewall-grid{display:grid;grid-template-columns:168px 1fr 168px;gap:14px;align-items:center;margin-top:18px}.proposal,.gateway-box{border:1px solid rgba(255,255,255,.15);border-radius:9px;padding:15px;background:rgba(255,255,255,.045)}.proposal .tag,.gateway-box .tag{font-size:8px;letter-spacing:1px;color:#80c3ff;font-weight:900}.proposal .amount{font-size:22px;font-weight:900;margin-top:12px}.confidence{font-size:10px;color:#a8c1da;margin-top:3px}.stages{display:grid;grid-template-columns:repeat(6,1fr);gap:7px}.stage{min-height:88px;border:1px solid rgba(255,255,255,.13);border-radius:7px;background:rgba(255,255,255,.04);padding:11px}.stage-icon{color:#87a1ba;margin-bottom:9px}.stage b{display:block;font-size:8px;letter-spacing:.6px}.stage span{display:block;font-size:9px;color:#93a9bf;margin-top:7px}.gateway-box{text-align:left}.gateway-box .status{font-size:16px;font-weight:900;margin-top:12px}.decision-bottom{border-top:1px solid rgba(255,255,255,.12);margin-top:18px;padding-top:16px;display:flex;align-items:center;justify-content:space-between}.reasons{font-size:11px;color:#b8cee2}.risk-circle{width:62px;height:62px;border:4px solid #294866;border-radius:50%;display:grid;place-items:center;font-weight:900}.final{text-align:right}.final small{font-size:8px;letter-spacing:1px;color:#8ba5bf}.final b{display:block;font-size:17px;margin-top:4px}
        .two-col{display:grid;grid-template-columns:1.45fr .75fr;gap:20px}.scenario-grid{padding:0 22px 22px;display:grid;grid-template-columns:1fr 1fr;gap:9px}.scenario{border:1px solid #d8e2ed;background:#fff;border-radius:8px;padding:12px;display:flex;align-items:center;gap:11px;cursor:pointer;text-align:left;transition:all 0.2s;}.scenario:hover{border-color:#8bc8fb;box-shadow:0 4px 14px rgba(17,93,157,.07); transform:translateY(-1px)}.scenario-icon{width:31px;height:31px;background:#f1f6fb;border-radius:8px;display:grid;place-items:center;color:#5c7692}.scenario b{font-size:12px;display:block;color:var(--text);}.scenario span{font-size:10px;color:var(--muted);display:block;margin-top:3px}.scenario svg:last-child{margin-left:auto;color:#91a5b8}
        .graph-wrap{padding:0 22px 20px}.graph{height:320px;border:1px solid #dce5ef;border-radius:8px;position:relative;overflow:hidden;background:#fbfdff}.edge{position:absolute;height:2px;background:#cde0f5;transform-origin:left center;opacity:.8}.node{position:absolute;transform:translate(-50%,-50%);text-align:center;font-size:10px;color:#667e97;background:rgba(251,253,255,0.85);padding:6px;border-radius:8px;z-index:2;box-shadow:0 0 10px rgba(251,253,255,1)}.node-dot{width:28px;height:28px;border-radius:50%;border:6px solid #e1eefb;background:#0c94f5;margin:0 auto 6px;box-shadow:0 2px 6px rgba(12,148,245,.2)}.node.danger .node-dot{background:#ff4d55;border-color:#ffe0e2;box-shadow:0 2px 6px rgba(255,77,85,.2)}.node.medium .node-dot{background:#f2a900;border-color:#fff1c9;box-shadow:0 2px 6px rgba(242,169,0,.2)}.node b{display:block;color:#193652;font-size:11px;font-weight:700}.graph-legend{padding:12px;background:#f7fafc;border-radius:7px;margin-top:10px;font-size:10px}.dot-red,.dot-amber{display:inline-block;width:6px;height:6px;border-radius:50%;margin:0 4px 0 9px}.dot-red{background:#ff4d55}.dot-amber{background:#f2a900}
        .benchmark{padding:0 22px 22px}.bars{height:235px;display:flex;align-items:end;gap:80px;border-bottom:1px solid #dfe7ef;padding:0 45px}.bar-group{height:100%;flex:1;display:flex;align-items:end;justify-content:center;gap:4px;position:relative}.bar{width:42%;min-height:3px;background:#1295ef;border-radius:4px 4px 0 0}.bar.recall{background:#062e5b}.bar-label{position:absolute;bottom:-20px;font-size:10px;color:#6c829a;white-space:nowrap;text-align:center}.bench-list{display:grid;gap:9px;margin-top:35px}.bench-card{border:1px solid #dbe4ee;border-radius:8px;padding:12px 13px;display:grid;grid-template-columns:1.3fr repeat(3,1fr);align-items:center}.bench-card.featured{border-color:#9fcfff;background:#f8fcff}.bench-card b{font-size:12px;color:var(--text);}.bench-card small{display:block;color:var(--muted);font-size:9px;margin-top:4px}.bench-card strong{font-size:12px;color:var(--text);}
        .stream{padding:0 22px 22px}.stream-row{display:flex;align-items:center;justify-content:space-between;border:1px solid #e0e7ef;border-radius:8px;padding:11px 13px;margin-top:7px;background:#fff}.stream-id{font-family:"JetBrains Mono",monospace;font-size:10px;color:var(--text)}.stream-name{font-size:10px;color:var(--muted);margin-top:4px}.pill{font-size:9px;font-weight:900;padding:5px 8px;border-radius:5px}.pill.danger{background:#fff0f1;color:#f33f49;border:1px solid #ffc9cc}.pill.warning{background:#fff8e7;color:#c78900;border:1px solid #ffdc79}.pill.success{background:#eafaf4;color:#008b5a;border:1px solid #b9edd7}
        .posture{padding:0 22px 22px}.posture-grid{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid #dce5ef;border-radius:8px;overflow:hidden}.posture-grid div{padding:13px;border-right:1px solid #dce5ef;background:#fff}.posture-grid div:last-child{border:0}.posture-grid small{display:block;font-size:8px;color:#7389a0;letter-spacing:1px}.posture-grid b{display:block;font-size:13px;margin-top:7px;color:var(--text)}.green{color:#00a66a}.posture-note{margin-top:14px;font-size:11px;color:#6d849c;display:flex;gap:7px;align-items:center;font-weight:500}
        .queue-table{padding:0 22px 22px;overflow:auto;max-width:100%;}.queue-head,.queue-row{min-width:800px;display:grid;grid-template-columns:1.45fr 1.2fr .7fr .7fr .8fr 1fr;gap:10px;align-items:center}.queue-head{font-size:8px;letter-spacing:1px;color:#7890a9;font-weight:900;padding:8px 10px;border-bottom:1px solid #e0e7ef}.queue-row{padding:11px 10px;border-bottom:1px solid #edf1f5;font-size:10px;color:var(--text);}.queue-row strong{font-family:"JetBrains Mono",monospace;font-size:9px}.queue-row small{display:block;color:var(--muted);margin-top:3px}.actions{display:flex;justify-content:flex-end;gap:5px}.btn-small{border:1px solid #ffbec2;background:#fff;color:#ef4a52;border-radius:5px;padding:6px 10px;font-size:9px;font-weight:800;cursor:pointer;transition:all 0.2s}.btn-small:hover{background:#fff0f1}.btn-small.approve{border-color:#9edfc6;color:#008f5c;background:#effbf6}.btn-small.approve:hover{background:#eafaf4}.btn-small:disabled{opacity:.5}
        .audit{display:grid;grid-template-columns:1fr 1fr;gap:20px;padding:0 22px 22px}.audit-box{border:1px dashed #d6e2ee;border-radius:8px;padding:22px;color:#6d849c;font-size:11px;background:#fff}.audit-box b{color:var(--text);font-size:13px;display:block;margin-bottom:8px}.hashes{display:grid;gap:6px;margin-top:10px}.hash{font-family:"JetBrains Mono",monospace;font-size:9px;background:#f6f9fc;border:1px solid #e3eaf1;padding:8px 10px;border-radius:5px;overflow:hidden;text-overflow:ellipsis;color:var(--text)}
        .alert{background:#fff0f1;border:1px solid #ffc8cc;color:#c9343e;border-radius:7px;padding:12px 16px;font-size:13px;margin-bottom:20px;display:flex;align-items:center;gap:8px;font-weight:500;}
        .mobile-toggle{display:none;border:0;background:transparent;cursor:pointer;color:var(--text)}
        @media(max-width:1100px){.sidebar{width:205px}.main{margin-left:205px}.content{padding:24px}.firewall-grid{grid-template-columns:145px 1fr}.gateway-box{grid-column:1/-1}.two-col{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}}
        @media(max-width:760px){.sidebar{transform:translateX(-100%);transition:.3s cubic-bezier(0.4, 0, 0.2, 1);width:260px;box-shadow:4px 0 24px rgba(0,0,0,0.1)}.sidebar.open{transform:none}.main{margin-left:0;width:100vw;overflow-x:hidden}.topbar{padding:0 14px}.mobile-toggle{display:block;margin-right:10px}.operator{display:none}.gateway{display:none}.content{padding:18px 13px 50px}.hero{display:block}.hero h1{font-size:28px}.hero .primary{margin-top:14px}.metrics{grid-template-columns:1fr 1fr;gap:8px}.metric{padding:12px}.metric-value{font-size:19px}.firewall{padding:16px}.firewall-grid{grid-template-columns:1fr}.stages{grid-template-columns:repeat(2,1fr)}.two-col{grid-template-columns:1fr}.scenario-grid{grid-template-columns:1fr;padding:0 13px 13px}.bars{gap:10px;padding:0 8px}.bench-card{grid-template-columns:1.2fr 1fr 1fr 1fr}.audit{grid-template-columns:1fr}.posture-grid{grid-template-columns:1fr}.posture-grid div{border-right:0;border-bottom:1px solid #dce5ef}.top-title{font-size:13px}}
      `}</style>

      <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
        <div className="brand">
          <div className="brandmark">F</div>
          <div>
            <div className="brandname">FinGuard</div>
            <div className="brandsub">EXECUTION FIREWALL</div>
          </div>
        </div>
        <div className="side-title">MERCHANT WORKSPACE</div>
        <div className="workspace">
          <div className="store-icon">FG</div>
          <div><b>FinGuard Store</b><span>Test environment</span></div>
          <ChevronRight size={15} style={{ marginLeft: "auto" }} />
        </div>
        <nav className="nav">
          {nav.map(([id, label, Icon]) => (
            <button key={id} className={active === id ? "active" : ""} onClick={() => scrollTo(id)}>
              <Icon size={15} /> {label}
              {id === "review" && <span className="badge">{metrics.reviews}</span>}
            </button>
          ))}
        </nav>
        <div className="side-bottom">
          <div className="online"><b><LockKeyhole size={11} style={{ verticalAlign: "middle" }} /> Firewall online</b>Every AI refund is checked before execution.</div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <button className="mobile-toggle" onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X /> : <Menu />}
          </button>
          <div>
            <div className="top-title">Overview</div>
            <div className="top-sub">Refund intelligence & execution control</div>
          </div>
          <div className="top-actions">
            <div className="gateway">● Razorpay test gateway live</div>
            <Search size={17} color="#6b8299" />
            <Bell size={17} color="#6b8299" />
            <div className="avatar">AK</div>
            <div className="operator">Ananya Kulkarni<small>Risk operator</small></div>
          </div>
        </header>

        <div className="content">
          <section id="command">
            <div className="hero">
              <div>
                <span className="eyebrow">TEST ENVIRONMENT</span>
                <h1>Good morning, Ananya</h1>
                <p style={{fontSize: "13px", marginTop: "6px"}}>Review the latest AI proposals and their execution outcomes.</p>
              </div>
            </div>

            {error && <div className="alert">{error}</div>}

            <div className="metrics">
              <div className="metric"><div className="metric-top">REFUND VOLUME <span className="metric-icon"><CircleDollarSign size={16}/></span></div><div className="metric-value">{metrics.volume}</div><div className="metric-desc">{metrics.proposals} proposals evaluated</div></div>
              <div className="metric"><div className="metric-top">BLOCKED ACTIONS <span className="metric-icon"><ShieldAlert size={16}/></span></div><div className="metric-value">{metrics.blocked}</div><div className="metric-desc">Execution prevented by policy</div></div>
              <div className="metric"><div className="metric-top">REVIEW QUEUE <span className="metric-icon"><Clock3 size={16}/></span></div><div className="metric-value">{metrics.reviews}</div><div className="metric-desc">Awaiting human decision</div></div>
              <div className="metric"><div className="metric-top">BLOCK RATE <span className="metric-icon"><Activity size={16}/></span></div><div className="metric-value">{metrics.catchRate}</div><div className="metric-desc">{metrics.latency}</div></div>
            </div>
          </section>

          <section id="feed" className="panel">
            <div className="panel-head"><div className="section-label">LIVE DECISIONS FEED</div><h2>Recent Proposals</h2><div className="panel-sub">Select a transaction to view its execution pipeline.</div></div>
            <div className="stream" style={{ maxHeight: "350px", overflowY: "auto" }}>
              {recent.slice(0, 20).map((r) => (
                <div 
                  className="stream-row" 
                  key={r.id} 
                  onClick={() => selectDecision(r)} 
                  style={{ cursor: "pointer", borderColor: decision?.id === r.id ? "#0c94f5" : "#e0e7ef", backgroundColor: decision?.id === r.id ? "#f5fafe" : "#fff" }}
                >
                  <div>
                    <div className="stream-id">{r.id}</div>
                    <div className="stream-name">{r.proposal?.customer_name || "Customer"} · {money(r.proposal?.amount)}</div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    {r.ai_decision && r.ai_decision !== (r.fingguard_decision || r.outcome || "BLOCK") && (
                      <span style={{ fontSize: "10px", color: "var(--muted)", fontWeight: 600 }}>
                        AI: <span style={{textDecoration: "line-through"}}>{r.ai_decision}</span> → FinGuard:
                      </span>
                    )}
                    <span className={`pill ${outcomeClass(r.fingguard_decision || r.outcome || "BLOCK")}`}>
                      {r.fingguard_decision || r.outcome || "BLOCK"}
                    </span>
                  </div>
                </div>
              ))}
              {recent.length === 0 && <div style={{padding: "20px", fontSize: "12px", color: "var(--muted)"}}>Loading proposals...</div>}
            </div>
          </section>

          <section id="live-decision" className="firewall">
            <div className="firewall-top"><span className="live-dot"/> LIVE AI DECISION <span style={{border:"1px solid #375675",padding:"3px 7px",borderRadius:10}}>Independent verification</span></div>
            <h2>AI Agent → FinGuard Firewall → Test Gateway</h2>
            <p>The model can propose. Only the firewall can execute.</p>
            <div className="firewall-grid">
              <div className="proposal">
                <div className="tag">AI AGENT PROPOSAL</div>
                <div className="amount">{money(decision?.proposal?.amount || 5000)}</div>
                <div className="confidence">{decision?.ai_decision || "APPROVE"}</div>
              </div>
              <div className="stages">
                {["State","Balance","Evidence","Policy","Behaviour","Risk"].map((s) => {
                  const liveStage = decision?.stages?.find(x => x.label === s);
                  return <div className="stage" key={s}><div className="stage-icon">{stageIcon(s)}</div><b>{s.toUpperCase()}</b><span>{liveStage?.detail || liveStage?.status || "Awaiting proposal"}</span></div>;
                })}
              </div>
              <div className="gateway-box">
                <div className="tag">RAZORPAY TEST GATEWAY</div>
                <div className="status">{decision ? (decision.gateway_status === "EXECUTION_PREVENTED" ? "No execution" : decision.gateway_status) : "No execution"}</div>
                <div className="confidence">Test mode · reversible</div>
              </div>
            </div>
            <div className="decision-bottom">
              <div className="reasons"><b style={{display:"block",color:"#fff",marginBottom:5}}>DECISION REASONS</b>{decision?.reasons?.slice(0,2).join(" · ") || "Select a decision to see exact evidence and policy reasons."}</div>
              <div style={{display:"flex",alignItems:"center",gap:12}}><div className="risk-circle">{decision?.risk_score ?? "—"}<span style={{fontSize:8}}>/100</span></div><div className="final"><small>FINGUARD DECISION</small><b>{decision?.fingguard_decision || decision?.outcome || "AWAITING"}</b></div></div>
            </div>
          </section>

          <section id="review" className="panel">
            <div className="panel-head"><div className="section-label">REVIEW QUEUE</div><h2>Human-in-the-loop decisions</h2><div className="panel-sub">Only proposals in the middle band wait for an operator.</div></div>
            <div className="queue-table">
              <div className="queue-head"><span>TRANSACTION</span><span>CUSTOMER</span><span>AMOUNT</span><span>RISK</span><span>STATUS</span><span>ACTION</span></div>
              {(queue.length ? queue : [
                {id:"demo-1",decision_id:"txn_fg_duplicate_refund",customer_name:"Nisha Kapoor",amount:2500,risk_score:40,status:"REJECTED"},
                {id:"demo-2",decision_id:"txn_fg_prompt_injection",customer_name:"Rohan Shah",amount:1800,risk_score:35,status:"OPEN"},
                {id:"demo-3",decision_id:"txn_fg_duplicate_refund",customer_name:"Nisha Kapoor",amount:2500,risk_score:40,status:"OPEN"},
              ] as QueueItem[]).slice(0,12).map((item) => <div className="queue-row" key={item.id}><div><strong>{item.transaction_id || item.decision_id}</strong><small>{item.reason || "Order fingerprint matches a previous refund"}</small></div><div>{item.customer_name || "Nisha Kapoor"}</div><div>{money(item.amount || 2500)}</div><div>{item.risk_score ?? 40}/100</div><div><span className={`pill ${outcomeClass(item.status)}`}>{item.status}</span></div><div className="actions">{item.status==="OPEN" ? <><button className="btn-small" onClick={()=>reviewAction(item.id,"reject")}>Reject</button><button className="btn-small approve" onClick={()=>reviewAction(item.id,"approve")}>Approve</button></> : <span className={`pill ${outcomeClass(item.status)}`}>{item.status}</span>}</div></div>)}
            </div>
          </section>

          <div className="two-col">
            <section id="red-team" className="panel">
              <div className="panel-head"><div className="section-label">RED TEAM LAB</div><h2>Attack the refund flow</h2><div className="panel-sub">Launch adversarial proposals against the real evaluator. This feature has been disabled in this view.</div></div>
              <div className="scenario-grid">
              </div>
            </section>

            <section id="risk-graph" className="panel">
              <div className="panel-head"><div className="section-label">RISK GRAPH</div><h2>Connected identity signals</h2></div>
              <div className="graph-wrap">
                <div className="graph">
                  {graphNodes.slice(1).map((n, i) => {
                    const a = graphNodes[0];
                    const dx = n.x-a.x, dy=n.y-a.y;
                    const length = Math.sqrt(dx*dx+dy*dy);
                    const angle = Math.atan2(dy,dx)*180/Math.PI;
                    return <div key={i} className="edge" style={{left:`${a.x}%`,top:`${a.y}%`,width:`${length}%`,transform:`rotate(${angle}deg)`}}/>;
                  })}
                  {graphNodes.slice(1,4).map((n,i) => {
                    const n2 = graphNodes[i+2];
                    if(!n2) return null;
                    const dx=n2.x-n.x,dy=n2.y-n.y,length=Math.sqrt(dx*dx+dy*dy),angle=Math.atan2(dy,dx)*180/Math.PI;
                    return <div key={"e"+i} className="edge" style={{left:`${n.x}%`,top:`${n.y}%`,width:`${length}%`,transform:`rotate(${angle}deg)`}}/>;
                  })}
                  {graphNodes.map(n => <div key={n.label} className={`node ${n.danger?"danger":""} ${n.medium?"medium":""}`} style={{left:`${n.x}%`,top:`${n.y}%`}}><div className="node-dot"/><b>{n.label}</b><span>{n.type}</span></div>)}
                </div>
                <div className="graph-legend"><b>{money(decision?.proposal?.amount || 5000)} refund</b><br/>Transaction · high risk signal <span className="dot-red"/>HIGH <span className="dot-amber"/>MEDIUM</div>
              </div>
            </section>
          </div>

          <section id="benchmarks" className="panel">
            <div className="panel-head"><div className="section-label">BENCHMARKS <span style={{color:"#b57900",border:"1px solid #f5d173",padding:"3px 6px",borderRadius:8,letterSpacing:0}}>Synthetic data</span></div><h2>Safety performance, side by side</h2><div className="panel-sub">The firewall is measured against simpler decision strategies on the same synthetic adversarial set.</div></div>
            <div className="benchmark">
              <div className="bars">
                {benchmarkRows.map((r:any) => <div className="bar-group" key={r.strategy}><div className="bar" style={{height:`${Math.max(3,r.precision)}%`}}/><div className="bar recall" style={{height:`${Math.max(3,r.recall)}%`}}/><span className="bar-label">{r.strategy}</span></div>)}
              </div>
              <div className="bench-list">
                {benchmarkRows.map((r:any) => <div className={`bench-card ${r.strategy==="FinGuard"?"featured":""}`} key={r.strategy}><div><b>{r.strategy}</b><small>{r.prevented} prevented</small></div><div><small>Precision</small><strong>{r.precision}%</strong></div><div><small>Recall</small><strong>{r.recall}%</strong></div><div><small>Latency</small><strong>{r.latency}</strong></div></div>)}
              </div>
            </div>
          </section>

          <section id="audit" className="panel">
            <div className="panel-head"><div className="section-label">AUDIT TRAIL</div><h2>Chain of custody</h2></div>
            <div className="audit">
              <div className="audit-box"><b>Decision evidence</b><p>Run a firewall decision to open the SHA-256 audit chain.</p><div className="posture-note"><LockKeyhole size={14}/> Each event is linked to the previous hash</div></div>
              <div className="audit-box">
                <b>Current chain</b>
                {decision?.chain_hashes?.length ? <div className="hashes">{decision.chain_hashes.slice(0,6).map((h,i)=><div className="hash" key={i}>{i+1}. {h}</div>)}</div> : <p>No decision chain loaded yet.</p>}
              </div>
            </div>
          </section>

          <div className="two-col">
            <section className="panel">
              <div className="panel-head"><div className="section-label">DECISION STREAM</div><h2>Latest firewall activity</h2></div>
              <div className="stream">
                <div style={{padding: "20px", fontSize: "12px", color: "var(--muted)"}}>See the Live Decisions Feed above.</div>
              </div>
            </section>

            <section id="gateway-control" className="panel">
              <div className="panel-head"><div className="section-label">GATEWAY CONTROL</div><h2>Execution posture</h2></div>
              <div className="posture">
                <div className="posture-grid"><div><small>MODE</small><b>Test only</b></div><div><small>POLICY</small><b className="green">Fail closed</b></div><div><small>HASHING</small><b className="green">SHA-256</b></div></div>
                <div className="posture-note"><CheckCircle2 size={14} color="#00a66a"/> No proposal bypasses the firewall.</div>
              </div>
            </section>
          </div>


        </div>
      </main>
    </div>
  );
}
