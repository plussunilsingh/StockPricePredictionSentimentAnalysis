# Deploying Stock Prediction Enterprise to Hugging Face Spaces (Docker)

This guide walks through packaging and deploying this repository as a Docker Space on Hugging Face. It assumes you already have a Hugging Face account and are familiar with basic Git operations.

Overview
- The repository includes a `Dockerfile` and `docker-entrypoint.sh` that create a container with a local `.venv`, installs Python dependencies, starts the backend (uvicorn) on an internal port, and runs the Streamlit frontend on the external port.
- Hugging Face Spaces runs a single exposed web process on the port provided in the `PORT` environment variable; the entrypoint respects `$PORT` and binds Streamlit to it.

Checklist before you deploy
- [ ] Confirm you have a `requirements.txt` (this project includes one). The image will install from it.
- [ ] Decide whether you want to use pre-built wheels or build from source. Some packages (pydantic_core) may require the Rust toolchain when a wheel isn't available for your Python/OS.
- [ ] Ensure sensitive files (API keys, secrets) are stored as Hugging Face secrets or external vaults and not committed to the repo.

Quick local test (build & run)
1. Build the image locally:

```bash
docker build -t stock-prediction-enterprise:latest .
```

2. Run the container locally and map the streamlit port (example maps to 8005):

```bash
docker run -it --rm -p 8005:8005 -e PORT=8005 stock-prediction-enterprise:latest
```

3. Open the UI at http://localhost:8005

Hugging Face Spaces (Docker) deployment
1. Create a new Space on Hugging Face and select "Docker" as the SDK.
2. Clone the new Space repository locally (or push this repo as the Space's repo). For example:

```bash
git clone https://huggingface.co/spaces/<your-username>/<your-space-name>
cd <your-space-name>
# either copy this project's files into the Space repo or add this repo as a remote and push required files
```

3. Make sure the Space repository contains at least:
- `Dockerfile` (already added)
- `docker-entrypoint.sh` (already added)
- `requirements.txt` or other dependency manifest
- Your application code (or a submodule pointing to it)

4. Adjust memory / hardware settings on the Space page if your model and dependencies need more resources.

5. Push changes to the Space repository:

```bash
git add .
git commit -m "Add Docker-based Space files"
git push origin main
```

6. After pushing, Hugging Face will build your Docker image. The build logs appear in the Space UI.

## Using the Slim Docker image (recommended for smaller builds)

A `Dockerfile.slim` has been added which avoids installing Rust/cargo and favors binary wheels. Use this when you want a smaller image and faster builds, provided your dependencies have wheels for Python 3.11 / manylinux.

How to use `Dockerfile.slim` for your Space:

1. Rename or copy `Dockerfile.slim` to `Dockerfile` in the Space repository before committing:

```bash
cp Dockerfile.slim Dockerfile
git add Dockerfile
git commit -m "Use slim Dockerfile for smaller image"
git push origin main
```

2. Alternatively, edit the `Dockerfile` in the Space repo UI and paste the contents of `Dockerfile.slim`.

Notes and best practices when using the slim image
- If pip attempts to build a package from source (and fails), consider:
  - Pinning that package to a version with binary wheels for Python 3.11.
  - Replacing that dependency with an alternative that provides wheels.
- Use `pip download --dest wheelhouse -r requirements.txt` on a machine that can build wheels, then COPY a `wheelhouse/` into the image and `pip install --no-index --find-links wheelhouse -r requirements.txt` to avoid compilation during Docker build.

## Using a wheelhouse to avoid source builds (advanced, recommended for reproducible builds)

If some packages in `requirements.txt` require building native extensions (for example `pydantic-core`), you can prebuild binary wheels on a compatible Linux manylinux image and include them in the Space repository. The Space Dockerfile can then install from the local wheelhouse using `--no-index --find-links /app/wheelhouse` which avoids compilation during the HF build.

Important: build wheels on a Linux manylinux environment matching the target architecture (most Spaces run x86_64 manylinux images). Building wheels on macOS or arm64 may produce incompatible artifacts.

Steps to build a wheelhouse (recommended using Docker):

1. Create an empty wheelhouse directory at the project root:

```bash
mkdir -p wheelhouse
```

2. Use the official manylinux image to build wheels for Python 3.11 (adjust the image for your target architecture if necessary). This example builds wheels for CPython 3.11 on manylinux2014_x86_64:

```bash
# Run from the project root (where requirements.txt is located)
docker run --rm -v "$(pwd)":/io quay.io/pypa/manylinux2014_x86_64 /bin/bash -lc \
  "/opt/python/cp311-cp311/bin/pip wheel -r /io/requirements.txt -w /io/wheelhouse --no-deps"
```

3. Inspect the `wheelhouse/` directory to confirm wheels were created.

4. (Optional) If some packages still fail to build, you can iterate on pinned versions in `requirements.txt` until all required wheels are produced for CPython 3.11.

Deploy with the wheelhouse using the provided helper script

Once `wheelhouse/` is populated, use the deploy helper to copy the wheelhouse into the Space repo and patch the `Dockerfile` to install from it.

Example (use slim Dockerfile + wheelhouse):

```bash
# Make script executable (if not already)
chmod +x ./scripts/deploy_to_hf.sh

# Deploy and request slim Dockerfile + include wheelhouse
./scripts/deploy_to_hf.sh plussunilsingh StockPricePrediction main slim wheelhouse
```

What the script does when `wheelhouse` is requested:
- Copies `wheelhouse/` into the Space repo (this will increase repo size).
- Patches the `Dockerfile` in the Space repo to use:
  `pip install --no-cache-dir --no-index --find-links /app/wheelhouse -r /app/requirements.txt`

Notes and caveats
- The wheelhouse approach ensures the Docker build on Hugging Face will only install binary wheels, avoiding failures and Rust builds — but it increases repository size. If you prefer not to commit a wheelhouse to the Space repo, skip this and use the non-slim Dockerfile (which includes Rust/cargo) or pin packages to prebuilt wheels.
- If your Space must target multiple Python versions or architectures, you'll need to build wheels for each target and include them in the wheelhouse.

Important considerations and tips

- Single exposed port: Spaces exposes a single public port (value in $PORT). Our entrypoint starts the backend internally on 127.0.0.1:8000 and binds Streamlit to $PORT (0.0.0.0:$PORT). Streamlit will therefore be accessible externally and will call the backend via localhost inside the container.

- Large images & build time: The full `requirements.txt` contains packages that need native wheels; builds may be slow and may require Rust or platform-specific build tools. To reduce build time and image size:
  - Favor pinned versions that have prebuilt wheels for Linux (many CI builds use manylinux wheels).
  - Remove development-only packages from `requirements.txt`.
  - Consider building the image on a machine with cached wheels or using a multi-stage build.

- Rust/Pydantic builds: If pip tries to build `pydantic-core` from source, it needs a Rust toolchain. The provided `Dockerfile` installs `cargo` to allow building, but that increases image size. Alternative options:
  - Pin `pydantic-core` to a version with prebuilt wheels for your target platform.
  - Use a base image and Python version with compatible wheels.

- Secrets: Use Hugging Face Space Secrets feature to store API keys (Settings → Secrets). Access secrets via environment variables in your code.

- Logging: The container writes logs to stdout/stderr (streamlit/uvicorn). For persistent logs, you can write to a mounted volume in non-Space deployments.

Troubleshooting
- Build fails on pip wheel compile for `pydantic-core`:
  - Option A: Allow the Dockerfile to install Rust (already included). Check build logs for `maturin`/`cargo` errors.
  - Option B: Pin pydantic/pydantic-core to a stable binary wheel release compatible with the container.

- App starts locally but fails on Spaces:
  - Check the build logs and the runtime logs in the Space UI.
  - Ensure `PORT` is respected and streamlit is bound to 0.0.0.0.

Optional improvements (I can implement)
- Add a `Dockerfile.slim` variant that relies exclusively on binary wheels and excludes cargo to reduce image size.
- Add a `docker-compose.yml` for local development that runs backend and frontend in separate containers and an nginx reverse-proxy.
- Add a health check endpoint and modify entrypoint to poll it (currently the entrypoint waits for backend TCP port).

If you want, I can now:
- Update the `Dockerfile` to remove `cargo` (make it smaller) and pin `pydantic_core`/`pydantic` to wheel-compatible versions.
- Add a `README.md` section summarizing the above steps in repo root.

Which follow-up should I do next? (recommended: update entrypoint to respect $PORT — already done — then optionally make the Dockerfile smaller or add a HF-specific README)
