# INC-2026-1103 — notes-prod

You are the on-call security engineer. It is **Tue 2026-11-03, 08:15 UTC**.

## What happened so far

| Time (UTC) | Event |
|---|---|
| 06:47 | Falco `Critical` alert routed to PagerDuty (only `Critical` and above are paged). |
| 06:52 | Grafana: CPU saturation on all three nodes (`cp-1`, `worker-1`, `worker-2`). |
| 07:05 | Platform on-call ran `kubectl -n kube-system get ds` from the VPN and saw `node-problem-helper`. They did not recognise it and did not touch anything. |
| 08:10 | Support ticket: *"All my notes disappeared since last night, I just created one and it's the only one left."* |

Platform on-call asks: **"Can I just delete the DaemonSet and go back to bed?"**

## Environment

- Source: this repository, public on GitHub, deployed by `.github/workflows/deploy.yml`.
- Self-managed kubeadm cluster. API server public at `https://203.0.113.10:6443`.
- `https://notes.example.com` → `web` Service (LoadBalancer).
- `https://api.notes.example.com` → ingress-nginx (managed in the platform repo) → `api` Service.
- Office/VPN egress: `192.0.2.10`.

Pods at time of incident:

| Pod | IP | Node |
|---|---|---|
| `notes-app/api-6d8f7c9b8-x2kqp` | 10.244.1.17 | worker-1 |
| `notes-app/api-6d8f7c9b8-7tjwm` | 10.244.2.23 | worker-2 |
| `notes-app/db-5f7b9d4c6-kq2lr` | 10.244.1.30 | worker-1 |
| `kube-system/ingress-nginx-controller-…` | 10.244.0.12 | cp-1 |

Node IPs: `cp-1` 10.0.0.11, `worker-1` 10.0.0.12, `worker-2` 10.0.0.13. Service `kubernetes.default.svc` = 10.96.0.1.

## Artifacts

| File | Source | Notes |
|---|---|---|
| `ingress-nginx-api.log` | ingress-nginx, host `api.notes.example.com` | Sampled export for 2026-11-02 19:30 → 2026-11-03 08:00. Default log format; request bodies are not logged. |
| `k8s-audit.jsonl` | kube-apiserver audit log via SIEM | Saved search: every request whose verb is not `get`/`watch`, plus every `get` on `secrets`. Control-plane components, kubelets and built-in controllers are excluded. Range: 2026-10-20 → now. |
| `falco.log` | Falco, all nodes | Range: 2026-11-02 18:00 → now. `custom:` rules are ours. |
| `github-activity.tsv` | GitHub org audit log + Actions run history | Range: repo lifetime. |

The application itself does not write logs. There are no DB query logs, no VPC flow logs and no node shell history.

## The ask

Walk us through it out loud. We care more about how you reason than about finishing.
