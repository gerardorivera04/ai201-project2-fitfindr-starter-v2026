# Running FitFindr

**Selected path: Path B - local with logs.**

FitFindr runs on the local machine behind a small HTTP server. A real run
record is written to disk, rather than relying only on terminal output.

---

## Environment requirements

- **Operating system:** macOS, Linux, or Windows
- **Python:** 3.11, 3.12, or 3.13. Python 3.14 is not supported.
- **Verified Python in this repository:** 3.13.15
- **Memory/disk:** 4 GB RAM recommended; at least 2 GB free disk
- **Required secret:** `GEMINI_API_KEY` in a local `.env` file
- **Model:** `gemini-3.5-flash-lite`
- **Model files:** none. The model is accessed through Gemini's API, so there
  is no local model weight or model-file size to report.
- **Application data:** `data/listings.json` and the wardrobe data under
  `utils/data_loader.py`; the checked-in `data/` directory is 24 KB.
- **Network:** required for model calls

Dependencies are exact-pinned in `requirements.txt`. Do not use
`pip install --upgrade`.

---

## Clean-checkout setup

Run these commands from the repository's parent directory.

**macOS / Linux**

```bash
git clone https://github.com/gerardorivera04/ai201-project2-fitfindr-starter-v2026.git fitfindr
cd fitfindr

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

cp .env.example .env
```

**Windows (PowerShell)**

```powershell
git clone <repository-url> fitfindr
cd fitfindr

python -m venv .venv
.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Copy-Item .env.example .env
```

Open `.env` and replace `GEMINI_API_KEY=your_key_here` with your actual key.
Never commit `.env`; it is excluded by `.gitignore`.

Verify the setup:

```bash
python test.py
```

The environment is ready when `test.py` reports no `FAIL` lines.

---

## Exact start command

From the activated virtual environment at the root of the clean checkout:

```bash
python serve.py
```

The server is available at:

```text
http://localhost:5000
```

Port `5000` is the default. It is also commonly used by macOS AirPlay
Receiver or another process already running on the machine. If the default
port is unavailable, use a different port instead of changing project code.

Verify it is running:

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{"status":"ok"}
```

Run one real FitFindr request:

```bash
curl -X POST http://localhost:5000/ask \
  -H 'Content-Type: application/json' \
  -d '{"query":"vintage graphic tee under $30"}'
```

Use this command to stop the server: `Ctrl-C`.

The server binds to `0.0.0.0` and reads `PORT` when set. When `PORT` is
unset, it uses `5000`. For example:

```bash
PORT=5001 python serve.py
curl http://localhost:5001/health
```

---

## Structured run records

Every HTTP agent run writes one JSON Lines entry to `logs/runs.jsonl`.
Successful responses and failures must both be recorded. A missing output,
invalid request, model failure, timeout, or rejected input is not silent: it
is retained with `status` and `error` fields.

Each entry has the following named fields:

| Field | Meaning |
|---|---|
| `timestamp` | UTC time at which the request was recorded |
| `run_id` | Identifier unique to this run |
| `input` | The submitted query |
| `output` | Selected item, outfit, and fit card when successful |
| `status` | `success` or `error` |
| `duration_ms` | Wall-clock duration of the complete agent run |
| `model` | Model name used for the run |
| `model_calls` | Number of model calls made |
| `prompt_tokens` | Prompt tokens reported by the provider |
| `output_tokens` | Output tokens reported by the provider |
| `cache_hits` | Responses served from the local cache |
| `error` | `null` on success, otherwise a readable failure description |

Example successful entry:

```json
{"timestamp":"2026-11-17T20:54:42Z","run_id":"6179a882","input":"vintage graphic tee under $30","output":"selected a matching listing and created an outfit and fit card","status":"success","duration_ms":1234,"model":"gemini-3.5-flash-lite","model_calls":2,"prompt_tokens":1683,"output_tokens":492,"cache_hits":0,"error":null}
```

Example rejected-input entry:

```json
{"timestamp":"2026-11-17T20:55:10Z","run_id":"4a8e1c23","input":"","output":null,"status":"error","duration_ms":1,"model":"gemini-3.5-flash-lite","model_calls":0,"prompt_tokens":0,"output_tokens":0,"cache_hits":0,"error":"Send JSON with a query field"}
```

The current commit should contain a real `logs/runs.jsonl`, not placeholder
entries. To inspect it:

```bash
tail -n 20 logs/runs.jsonl
```

---

## Cost measurement

For one measured run, caching must be disabled:

```bash
AI201_CACHE=0 python serve.py
```

On Windows PowerShell:

```powershell
$env:AI201_CACHE="0"
python serve.py
```

Send the same normal request ten times. For every run, record:

- wall-clock `duration_ms`
- provider-reported `prompt_tokens`
- provider-reported `output_tokens`
- `model_calls`

Take the arithmetic mean of all ten runs and paste the result in README.md
under `What It Costs`. This is the measured cost of an agent run; the API
pricing page is only an estimate.

---

## Troubleshooting

If `test.py` says the key is missing, confirm `.env` exists at the repository
root and contains `GEMINI_API_KEY`.

**Port 5000 is already in use**

First, determine whether another process is using the port:

**macOS / Linux**

```bash
lsof -nP -iTCP:5000 -sTCP:LISTEN
```

**Windows (PowerShell)**

```powershell
Get-NetTCPConnection -State Listen -LocalPort 5000 |
  Select-Object LocalAddress, LocalPort, OwningProcess
```

If the listener is another FitFindr instance started by you, stop that
process with `Ctrl-C` in its terminal. Do not stop a system process unless
you recognize it.

On macOS, `ControlCenter` or `ControlCe` commonly owns port 5000 because
AirPlay Receiver is enabled. You can disable **AirPlay Receiver** in
**System Settings > General > AirDrop & Handoff** or
**System Settings > General > Sharing**, depending on your macOS version.
That restores the default port, but disabling the setting is optional.

The recommended fallback is to use another port. On macOS or Linux:

```bash
PORT=5001 python serve.py
curl http://localhost:5001/health
curl -X POST http://localhost:5001/ask \
  -H 'Content-Type: application/json' \
  -d '{"query":"vintage graphic tee under $30"}'
```

On Windows PowerShell:

```powershell
$env:PORT="5001"
python serve.py
```

In a second PowerShell terminal:

```powershell
Invoke-RestMethod -Uri http://localhost:5001/health -Method Get
```

If `python serve.py` cannot import a package, activate `.venv` and run:

```bash
python -m pip install -r requirements.txt
```

---

## Other commands

Start with the data. Your tools will only be as good as your understanding of
what they're reading, and ten minutes here saves an hour of confused debugging.

```bash
python app.py fields                    # what a listing and a wardrobe item hold
python app.py listings --full -n 6      # read six listings all the way through
python app.py examples                  # queries worth trying
python app.py ask 'vintage graphic tee under $30'
```

> **Quote your queries with single quotes**, on every operating system. In
> PowerShell, `"vintage graphic tee under $30"` in double quotes silently
> becomes `vintage graphic tee under ` — PowerShell reads `$30` as a variable
> and substitutes nothing. You get results with no price ceiling and no error
> saying so. Single quotes are literal in PowerShell, bash and zsh alike.

That last one runs the loop. All three tools are stubs, so it will tell you the
loop isn't built yet. **That's the correct starting position** — it runs, and it
does nothing.

---

## Every command

| Command | What it does |
|---|---|
| `python test.py` | Checks your environment. Run it whenever something feels off |
| `python app.py fields` | The fields a listing and a wardrobe item have — **Milestone 1** |
| `python app.py listings` | Browse the data. `--full` for whole records, `-n` for how many |
| `python app.py examples` | Queries worth trying, including one that matches nothing |
| `python app.py ask '...'` | Run the agent on one query — **single quotes** |
| `python app.py ask` | Keep asking until you press Enter on an empty line |
| `python agent.py` | Runs both example paths — one that matches, one that can't |
| `python mcp_server.py` | Starts your MCP server — **unit 4** |
| `python mcp_client.py` | Asks the server what it offers — **unit 4** |
| `python run_eval.py --label before` | Runs every scenario five times and writes the run log — **unit 4** |
| `python serve.py` | Serves the agent over HTTP instead of exiting — **unit 9** |

Useful flags on `ask`:

| Flag | What it does |
|---|---|
| `--trace` | Print the loop step by step, once you've added the trace calls |
| `--empty-wardrobe` | Run as a user with nothing saved — one of unit 4's failure modes |

---

## Which command goes with which milestone

### Unit 3 — the build

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Read the data, run the starter | `app.py fields`, `app.py listings --full`, `app.py ask` |
| 2 | Spec your three tools | README, **Tool Inventory** |
| 3 | Write your acceptance criteria | `criteria.md` |
| 4 | Build the three tools | `tools.py`, tested one at a time from a terminal |
| 5 | Wire the loop and the state | `agent.py::run_agent` |
| 6 | Write it up | README |

### Unit 4 — the test

| Milestone | What you're doing | Where |
|---|---|---|
| 1 | Move one tool onto MCP | `mcp_server.py`, then `mcp_client.call_tool` in `run_agent` |
| 2 | Break it on purpose, then trace it | `trace.py`, `app.py ask --trace` |
| 3 | Run your test | `scenarios.py`, then `run_eval.py --label before` |
| 4 | Call each criterion, diagnose the misses | README |
| 5 | Fix one thing and re-run | `run_eval.py --label after` |
| 6 | Say what's still broken | README |

---

## Running it somewhere else — **unit 9**

Everything above exits when the command finishes. A host has nothing to keep
running, so before you can deploy this you need something that stays up.
`serve.py` is that: the same `run_agent()`, behind two HTTP routes.

On your machine:

```bash
python serve.py
curl -X POST http://localhost:5000/ask \
  -H 'Content-Type: application/json' \
  -d '{"query": "vintage graphic tee under $30"}'
```

On a host, the start command is:

```bash
gunicorn serve:app
```

| Thing | What it means |
|---|---|
| `PORT` | The host tells your app which port to listen on by setting this. Both `serve.py` and `gunicorn` read it, and `serve.py` falls back to `5000` on your machine. Don't hard-code a port |
| `POST /ask` | `{"query": "...", "wardrobe": {...}}` — wardrobe optional. Returns the session dict, `error` and all |
| `GET /health` | Says `ok` if the app is awake |
| It answers one request at a time | On purpose. A second request waits for the first to finish, and prints `[serve] another request is still running` while it waits. An MCP tool call starts a whole second Python process, and the free tier's 512 MB has no room for two of those at once — and `generate.py`'s rate-limit counting assumes one caller. The reasoning is written out in `serve.py` |
| `gunicorn serve:app`, exactly | Not `-k gevent`, not `-k eventlet`, not wrapped for uvicorn. `mcp_client.call_tool` uses `asyncio.run()`, which won't start inside a running event loop, so an async worker breaks **every** MCP call — and only once you've deployed it |
| The first request is slow | The free tier puts your app to sleep after about fifteen minutes of nothing. The next request wakes it up and waits for it — around a minute. Not a bug, and worth knowing before you demo it |

`serve.py` ships with **no logging and no timing in it**, on purpose. You add
that yourself in the follow-along, before you deploy — instrumenting first is
the point of the session.

---

## Where everything lives

| File | What it does |
|---|---|
| `config.py` | Every setting worth changing — **TEMPERATURE and the cache are at the top** |
| `tools.py` | Your three tools. **Stubs — you build these** |
| `agent.py` | The planning loop and the session. **Stub — you build this** |
| `generate.py` | The only thing that calls out to a service. Handles pacing and quota |
| `trace.py` | The trace helper, and the loop's stop condition |
| `app.py` | The command line |
| `serve.py` | The same agent over HTTP, for deploying — **unit 9** |
| `mcp_server.py` | Your MCP server — **unit 4, you register the tool** |
| `mcp_client.py` | Calling an MCP tool from your agent. Given to you |
| `scenarios.py` | What your test runs. **You fill this in** |
| `run_eval.py` | Runs the scenarios repeatedly and writes the run log |
| `criteria.md` | Your five acceptance criteria. **You fill this in** |
| `data/` | 40 listings and the wardrobe schema |
| `utils/data_loader.py` | Loading the data. Use this rather than reading the files yourself |
| `results/` | Run logs. **Commit these** — they're your evidence |

---

## The two settings people go looking for

Both are at the top of `config.py`, and the brief points at them by name.

If your fit cards come out **word-for-word identical** every time, it is one of:

- **`CACHE_ENABLED`** — while you build, identical prompts reuse the answer
  already received. That's deliberate; it makes debugging free. `run_eval.py`
  turns it off automatically.
- **`TEMPERATURE`** — at `0.0` the model gives you the same words every time.
  It ships at `0.9`.

---

## About rate limits

**This is the heaviest pair in the course for call volume.** Two of your three
tools call the model, so one agent run is several requests, and a few runs back
to back while debugging can cross the per-minute limit.

`generate.py` handles it:

- **It paces itself** and says when it's waiting. **A pause is the starter
  doing its job, not a bug.**
- **It reuses answers** to prompts already sent, while you build.
- **It stops** if a session makes an unreasonable number of calls, rather than
  draining your day's allowance. For an agent, that usually means a loop isn't
  ending — look for that before raising the number.
- **It counts your calls** and prints the total when you exit.

`config.MAX_ITERATIONS` is the loop's own stop condition. Your loop this unit
is short enough that you may never hit it. Keep it — a missing stop condition
is the most common architectural failure in production agents.

---

## When something goes wrong

| What you see | What it means |
|---|---|
| `The planning loop isn't built yet` | Correct, at the start. That's the TODO in `agent.py` |
| `No GEMINI_API_KEY found` | No `.env`, or the key wasn't pasted in. On Windows check it didn't save as `.env.txt` |
| A message saying the model couldn't be reached | Usually a bad key. This is also **exactly what unit 4 Milestone 2 asks you to trigger on purpose** |
| `[rate limit] ... Waiting 34s` | Working as intended. Leave it |
| `[serve] another request is still running` | Also working as intended. `serve.py` answers one request at a time; yours is queued behind one that's mid-run |
| `QuotaGuard: This session has made 300 requests` | A loop isn't ending. Find it before raising the budget |
| `The loop ran 11 times, past MAX_ITERATIONS` | Same thing, caught earlier |
| `The server doesn't offer a tool called '...'` | Nothing registered in `mcp_server.py` yet, or the name doesn't match |
| MCP returns a string where you expected a list | You're not going through `mcp_client.call_tool`, which unwraps it |
| Fit cards identical every run | `CACHE_ENABLED` or `TEMPERATURE`. See above |
| `--trace` prints nothing | You haven't added `trace.step()` calls yet — unit 4, Milestone 2 |
| `IncompleteFieldDefinitionWarning: Field 'lifespan'` | Harmless noise from the MCP library's dependencies. Not your code, not an error. Ignore it |
| A price ceiling you typed is being ignored | You used double quotes in PowerShell. `$30` vanished. Use single quotes |
| `UnicodeEncodeError: 'charmap' codec can't encode` | Shouldn't happen — `config.py` sets the console to UTF-8. If you see it, you're running a file that doesn't import `config` |

Still stuck after one honest attempt? Post in the help channel with the full
error, what you ran, and what you expected.

---

## A note on committing

At least four new commits in unit 3, at least four more in unit 4. Your commit
history is what shows your criteria existed before your results did.

**Do not delete and recreate this repository.** You submit the same URL both
units.

`results/` is deliberately **not** in `.gitignore`.
