# Offline embedding for Omarchy

Layer-2 routing picks a model for a request by comparing its text with a small fixed corpus, using a local embedding model. This guide installs that model so the runtime reads it from disk and never downloads anything. The config to activate it is [`examples/omarchy.offline-embedding.toml.example`](../../examples/omarchy.offline-embedding.toml.example).

> **Status.** These steps match the source verifier. They have not been run on the final ARM artifact. The embedding extra on aarch64, the model files and their recorded hashes, and a no-network run are all still unwitnessed (see [What is and is not proven](#what-is-and-is-not-proven)).

## What the runtime checks at startup

Routing activation is off by default. With `routing_activation = true`, bootstrap builds the embedding classifier before it accepts work, and stops with an error if any of these fail. It never falls back to a download or to another model.

- **Model.** The runtime uses `BAAI/bge-small-en-v1.5` only. `embedding_model_dir` must be an absolute path with no symlink anywhere in it. The directory must hold `config.json`, `tokenizer.json`, `tokenizer_config.json`, `special_tokens_map.json` and `model_optimized.onnx`, plus a `SHA256SUMS` file.
- **`SHA256SUMS`.** Every line is a lowercase SHA-256, two spaces, and a relative file name, which is the format `sha256sum` writes. It must list at least the five model files, and at most 64 entries. Every listed file must exist, and every file in the directory except `SHA256SUMS` must be listed, so stray files fail the check. The recipe below lists exactly the five. Write it in text mode: `sha256sum -b` marks each name with `*`, which the verifier rejects. Every hash is recomputed at startup.
- **Cache.** `embedding_cache_dir` must be absolute, outside the model directory, and under a parent directory that is not a symlink. It must be a directory owned by the harness user with mode exactly `0700`. Bootstrap creates it with `0700` if it does not exist.
- **Extra.** The `embedding` extra (`fastembed` and `onnxruntime`) must be importable.
- **Offline.** After the files pass, FastEmbed is given only the verified model path, the verified cache and `local_files_only=True`.
- **Labels.** `embedding_routing_candidates` must name all four workload classes, each as `provider:model` for an enabled provider. With Ollama alone, every label starts `ollama:`.

## 1. Install the embedding extra without network access

The locked versions for Python 3.12 are `fastembed` 0.8.0 and `onnxruntime` 1.23.2. `uv.lock` records a `cp312` `manylinux_2_28_aarch64` wheel for that `onnxruntime`. Use Python 3.12.

On a staging machine with network access and the same platform (aarch64 Linux, Python 3.12), run the same `uv sync` command below without `--offline` to fill a `uv` cache from the lock, then copy that cache to the Omarchy host. A cache filled on another architecture lacks the aarch64 wheels. On the host, install from the cache only:

```sh
export UV_CACHE_DIR=/absolute/path/to/your/uv-cache
uv sync --frozen --offline --all-packages --extra embedding
```

`--offline` makes `uv` fail if anything is missing from the cache instead of fetching it. `uv sync` is exact by default and installs no extra unless asked, so keep `--offline --extra embedding` on every later sync of this environment. A plain `uv sync --frozen --all-packages`, as in the examples README, removes `fastembed`, and bootstrap then stops with `fastembed is required`.

Check that the packages load from this environment and that ONNX Runtime has its CPU provider:

```sh
uv run --no-sync python -c 'import fastembed, onnxruntime, harness_runtime; print(fastembed.__version__, onnxruntime.__version__); print(fastembed.__file__); print(harness_runtime.__file__); print(onnxruntime.get_available_providers())'
```

Expect `0.8.0 1.23.2`, paths inside the environment's `site-packages` (or this checkout for `harness_runtime`), and `CPUExecutionProvider` in the list. Record the output.

## 2. Get the model files and record where they came from

FastEmbed 0.8.0 maps `BAAI/bge-small-en-v1.5` to the Hugging Face repository `qdrant/bge-small-en-v1.5-onnx-q`, file `model_optimized.onnx`. On the staging machine, download the five files from that repository at a pinned commit, not the moving `main` branch. Record:

- the repository and the full commit id
- the download date
- the SHA-256 of each file

Hugging Face shows a SHA-256 for files stored with Git LFS. If it lists one for `model_optimized.onnx` at your commit, compare it with yours. The JSON files are ordinary Git files there, so the hashes you record are the reference for them. This repository ships no model hashes.

Copy **only** the five files. Download tools can leave metadata or cache folders next to the files, and any extra file fails the startup check.

## 3. Place the model and cache on the host

Choose a model location outside every checkout and backup-restore scope. Use paths with no symlinks; `realpath -e <dir>` must print the path unchanged.

```sh
FILES=/absolute/path/to/the/five/downloaded/files
MODEL=/absolute/path/to/your/models/bge-small-en-v1.5
CACHE=/absolute/path/to/your/embedding-cache
install -d -m 0755 "$MODEL"
(cd "$FILES" && cp config.json tokenizer.json tokenizer_config.json special_tokens_map.json model_optimized.onnx "$MODEL"/)
(cd "$MODEL" && sha256sum config.json model_optimized.onnx special_tokens_map.json tokenizer.json tokenizer_config.json > SHA256SUMS && sha256sum -c SHA256SUMS)
install -d -m 0700 "$CACHE"
ls -la "$MODEL"; stat -c '%U %a %n' "$CACHE"; realpath -e "$MODEL" "$CACHE"
```

The `SHA256SUMS` hashes must match the ones you recorded in step 2. Keep the cache separate from the model directory, not inside it. Both `cd` commands run in subshells, so your shell stays where it was; run step 4 from the root of this checkout.

## 4. Activate the config

```sh
cp examples/omarchy.offline-embedding.toml.example harness.toml
${EDITOR:-vi} harness.toml
```

Replace every placeholder with a literal absolute path. Set up the external state root as [External state root](../how-to-deploy.md#external-state-root-omarchy-production-profile) describes. The example routes software-engineering requests to `ollama:qwen2.5-coder:3b` and the other workloads to `ollama:llama3.2:3b`, so pull both with Ollama, or change the labels to models you have:

```sh
ollama pull llama3.2:3b
ollama pull qwen2.5-coder:3b
uv run --no-sync harness run examples/ollama-first.toml --config harness.toml
```

The routing manifest in the example binds no role or workload, so every request reaches the embedding classifier. If bootstrap stops with one of these messages, fix the cause it names:

| Message contains | Cause |
|---|---|
| `requires embedding_model_dir and embedding_cache_dir` | A path is missing from the config |
| `must be absolute` | A path is relative |
| `missing or symlinked` / `contains a symlink` | The model path goes through a symlink or is not a directory, or a file in it is a symlink |
| `cannot be verified` | Something the check needs does not exist or cannot be read: usually the model directory or its `SHA256SUMS` is missing, or the cache's parent directory does not exist |
| `malformed embedding SHA256SUMS entry` | A line is not `<sha256>  <name>`, for example one written by `sha256sum -b` (`*name`) |
| `SHA256SUMS does not cover the pinned model files` | One of the five files is not listed |
| `files differ from SHA256SUMS` | An extra or missing file |
| `SHA256 mismatch: <file>` | A file changed after hashing |
| `cache must be outside the model` | The cache is inside the model directory, or its parent is a symlink |
| `cache must be a private owned directory` | The cache is not owned by the harness user or is not `0700` |
| `fastembed is required` | The embedding extra is not installed |
| `candidates must name exactly four workload classes` / `require a constructed profile provider:model` | `embedding_routing_candidates` is incomplete or names a provider that is not enabled |

## What is and is not proven

| Claim | Status |
|---|---|
| The example config loads through the runtime config loader, and its four labels pass the corpus check | Source-checked |
| The `sha256sum` layout in step 3 passes the source verifier; an extra file, a changed file or a `0755` cache fails it | Source-checked against synthetic files |
| The embedding extra installs and imports on the final aarch64 artifact | Not run |
| Real model files, with their hashes recorded from a pinned commit | Not recorded |
| A run with outbound network blocked, including the three historical L2 witness nodes named in the Local L2 embedding row of the [profile contract decision](../../.harness/review-evidence/a5-contract-authority/profile-contract-decision-1.md) | Not run |
| Routing chooses between two or more candidates on a live request | Not run |

The runtime itself never enables network access or a model download for this path. Blocking outbound network during the witness run is still the operator's job.
