# Summary

Set up a local Kubernetes learning environment on Windows using the smallest working path:

1. Re-check environment and report findings.
2. Reuse the existing `kubectl` already on PATH.
3. Install `minikube` with `winget`.
4. Start Docker Desktop if it is not running, then verify `docker info`.
5. Start `minikube` with the Docker driver and verify node readiness.
6. Install `k8sgpt` from the official GitHub Windows release method.
7. Pause and ask for a real API key.
8. Configure the provider using the exact flags exposed by the installed `k8sgpt`.
9. Deploy, break, diagnose, explain, and fix a sample `nginx` deployment.
10. End with a short rerun cheat sheet.

# Current State Analysis

Observed from read-only exploration on this machine:

- `wsl --status` succeeds and shows:
  - Default Distribution: `Ubuntu-24.04`
  - Default Version: `2`
- `node -v` returns `v24.15.0`
- `npm -v` returns `11.12.1`
- `winget --version` returns `v1.29.280`
- `kubectl` is already present at `C:\Program Files\Docker\Docker\resources\bin\kubectl.exe`
- `minikube` is not installed
- `k8sgpt` is not installed
- `docker info` fails because the Docker Desktop Linux engine pipe is missing
- `Get-Process` does not find `Docker Desktop` or `com.docker.backend`

Implications:

- WSL2 is installed and usable.
- Docker Desktop is not running right now, so cluster startup would fail until the Docker engine comes up.
- No Windows restart is currently indicated by any discovery step.
- `kubectl` does not need reinstalling unless the user later asks for a standalone package anyway.

External facts checked during planning:

- `winget` currently lists `Kubernetes.minikube`.
- `winget` currently lists `Kubernetes.kubectl`.
- No `winget` package was found for `k8sgpt` during planning.
- The official `k8sgpt` Windows installation docs point to downloading the latest Windows binary from GitHub Releases and adding it to PATH.
- Current `k8sgpt` provider docs show provider names have changed across versions, so execution must inspect the installed CLI with `k8sgpt auth add --help` before choosing flags.
- Current provider docs show native `Groq` may exist in newer versions; per user preference, execution should prefer native `groq` if available, otherwise use the OpenAI-compatible fallback path.

# Assumptions And Decisions

- Reuse the existing `kubectl` instead of installing a duplicate.
- Prefer `winget` for `minikube` because it is present and already has the package.
- Attempt to launch Docker Desktop during execution if it is still stopped.
- Do not assume any `k8sgpt` backend name from docs alone; trust the installed binary help output first.
- Gemini is the first-choice provider if the user supplies a Google AI Studio key.
- If the user does not have a Gemini key, use Groq.
- If the installed `k8sgpt` supports native `groq`, use it.
- If native `groq` is not supported, fall back to `localai` with `--baseurl https://api.groq.com/openai/v1`.
- Do not proceed past provider setup until the user supplies a real API key.
- Do not run anything that would require a Windows restart without pausing and informing the user first.
- If `winget` or PATH writes require elevation, stop and call that out before continuing.

# Proposed Changes

## Workspace File

- `c:\Users\thang\Downloads\K8S_minikube_learning\.trae\documents\minikube-k8sgpt-local-learning-plan.md`
  - What: Stores the approved execution plan.
  - Why: Required by plan mode.
  - How: Created during planning only.

## System-Level Changes During Execution

- Existing `kubectl` installation on PATH
  - What: Verify version only.
  - Why: Already present, so no duplicate install is needed.
  - How: Run `kubectl version --client` before cluster work.

- Windows package manager state via `winget`
  - What: Install `minikube`.
  - Why: Needed to create a local Kubernetes cluster.
  - How: Use the current `winget` package for `Kubernetes.minikube`, then verify with `minikube version`.

- Docker Desktop process and engine
  - What: Ensure Docker Desktop is running and reachable.
  - Why: `minikube --driver=docker` depends on a working Docker engine.
  - How: Re-run `docker info`; if it still fails, attempt to launch Docker Desktop, wait, then verify again before moving on.

- Local Kubernetes state managed by `minikube`
  - What: Create a local cluster using the Docker driver.
  - Why: Needed for the learning environment and sample workload.
  - How: Run `minikube start --driver=docker`, then verify with `kubectl get nodes`.

- `k8sgpt` Windows binary
  - What: Install the latest Windows release from the official GitHub Releases page.
  - Why: No `winget` package was found during planning, and official Windows docs point to releases.
  - How: Download the correct Windows binary/archive, place it in a user-accessible location, ensure PATH works for the current shell, then verify with `k8sgpt version`.

- User-scoped `k8sgpt` auth configuration
  - What: Add one AI provider configuration.
  - Why: Required for `k8sgpt analyze --explain`.
  - How:
    - Ask the user for either a Gemini or Groq API key.
    - Inspect `k8sgpt auth add --help`.
    - If Gemini key: use the exact installed backend/flags for Google Gemini.
    - If Groq key: prefer native `groq` if available; otherwise use `localai --baseurl https://api.groq.com/openai/v1`.
    - Verify with `k8sgpt auth list`.

- Sample Kubernetes workload
  - What: Create, expose, break, diagnose, and repair a small deployment.
  - Why: Demonstrates the complete learning loop the user requested.
  - How:
    - Deploy `demo-app` from `nginx` with 2 replicas.
    - Expose it as a `NodePort`.
    - Verify pods are `Running`.
    - Change the image to `nginx:this-tag-does-not-exist`.
    - Verify a pod reaches `ErrImagePull` or `ImagePullBackOff`.
    - Run `k8sgpt analyze --explain` and show full output.
    - Explain the diagnosis in plain language.
    - Fix the deployment by setting `nginx:latest`.
    - Verify pods return to `Running`.

# Execution Plan

1. Environment gate
   - Run:
     - `wsl --status`
     - `docker info`
     - `node -v`
     - `npm -v`
     - `kubectl version --client`
   - Verify:
     - WSL default version is `2`
     - `kubectl` responds
     - Node and npm respond
   - Decision:
     - If `docker info` fails, report that Docker Desktop is not ready, attempt to launch Docker Desktop, then retry before any install or cluster step.

2. Install and verify `minikube`
   - Run the `winget` install for `Kubernetes.minikube`.
   - Verify with `minikube version`.
   - If `winget` requests admin approval or fails due to permission scope, stop and tell the user before continuing.

3. Bring up cluster
   - Run `minikube start --driver=docker`.
   - Verify with `kubectl get nodes`.
   - Success criteria: a single minikube node reports `Ready`.

4. Install and verify `k8sgpt`
   - Check the official `k8sgpt-ai/k8sgpt` release assets at execution time.
   - Install using the official Windows binary path.
   - Verify with `k8sgpt version`.
   - If PATH changes require opening a fresh shell, do that without rebooting.

5. Provider pause point
   - Ask the user to paste either:
     - a Google AI Studio Gemini API key, or
     - a Groq API key
   - Do not continue until a real key is supplied.

6. Provider configuration
   - Inspect `k8sgpt auth add --help`.
   - Configure the supplied provider using the exact backend name and flags supported by the installed version.
   - Verify with `k8sgpt auth list`.

7. Happy-path sample deployment
   - Run:
     - `kubectl create deployment demo-app --image=nginx --replicas=2`
     - `kubectl expose deployment demo-app --port=80 --type=NodePort`
   - Verify:
     - `kubectl get pods`
     - pods are `Running`

8. Intentionally break the app
   - Run `kubectl set image deployment/demo-app nginx=nginx:this-tag-does-not-exist`
   - Verify:
     - `kubectl get pods`
     - at least one pod enters `ErrImagePull` or `ImagePullBackOff`

9. Diagnose with `k8sgpt`
   - Run `k8sgpt analyze --explain`
   - Show the full output to the user.
   - Success criteria: output identifies the broken image pull problem clearly enough to act on it.

10. Explain and repair
   - Explain the `k8sgpt` output in plain language.
   - Run the fix by setting `nginx:latest`.
   - Verify with `kubectl get pods` until replicas return to `Running`.

11. Final handoff
   - Provide:
     - what was installed
     - which free API key/provider is in use
     - the exact command sequence to reproduce the break/diagnose/fix loop later

# Verification Steps

- Environment:
  - `wsl --status`
  - `docker info`
  - `node -v`
  - `npm -v`
  - `kubectl version --client`

- Install verification:
  - `minikube version`
  - `k8sgpt version`

- Cluster verification:
  - `kubectl get nodes`
  - `kubectl get pods`
  - `kubectl get svc demo-app`

- Provider verification:
  - `k8sgpt auth add --help`
  - `k8sgpt auth list`

- Diagnosis verification:
  - `k8sgpt analyze --explain`

- Repair verification:
  - `kubectl set image deployment/demo-app nginx=nginx:latest`
  - `kubectl rollout status deployment/demo-app`
  - `kubectl get pods`

# Known Risks

- Docker Desktop is currently stopped, so execution will pause there unless launching it succeeds.
- `winget` installs may require elevation depending on package scope and machine policy.
- `k8sgpt` backend names differ by version, so provider setup must be driven by the installed CLI help, not by memory or older docs.
- Free-tier API providers can rate limit or reject unsupported models; if that happens, execution should choose a supported free model exposed by the installed provider/backend combination.
