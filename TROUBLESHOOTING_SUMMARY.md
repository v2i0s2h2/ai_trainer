# AI Trainer Development Environment Troubleshooting Summary

This document summarizes the steps taken to diagnose and fix a series of issues while setting up the AI Trainer development environment on an Ubuntu server.

The core underlying issue discovered is that the server is running on an older CPU architecture that is incompatible with many modern, pre-compiled software binaries (like TensorFlow, Git, and Node.js). This leads to low-level errors like `Illegal Instruction` and `Segmentation fault`.

---

### Issue 1: Backend Setup Script Failure

-   **Problem:** Running `./scripts/setup_backend.sh` failed with the error `print_warning: command not found`.
-   **Diagnosis:** The script contained typos, calling undefined functions like `print_warning` instead of the correctly defined `log_warning`.
-   **Solution:** The script `scripts/setup_backend.sh` was corrected to use the `log_*` functions instead of `print_*`.
    ```bash
    # The 'replace' tool was used to fix the script internally.
    ```

---

### Issue 2: Missing `email-validator` Package

-   **Problem:** After setting up the virtual environment, running the backend (`python3 src/backend/main.py`) failed with `ImportError: email-validator is not installed`.
-   **Diagnosis:** The `pydantic` library required the `email-validator` package for email validation, but it was not listed as a dependency.
-   **Solution:** The `requirements.txt` file was updated to include the `[email]` extra for `pydantic`.
    ```bash
    # Original line in requirements.txt
    # pydantic>=2.5.0

    # Modified line in requirements.txt
    # pydantic[email]>=2.5.0
    ```
    The user was then instructed to re-run the backend setup script.

---

### Issue 3: `Illegal instruction (core dumped)` in Python

-   **Problem:** After fixing the email validator issue, the backend still crashed immediately on launch with `Illegal instruction (core dumped)`.
-   **Diagnosis:** This low-level error indicated that the `tensorflow` library binary was compiled for a more modern CPU than the one on the server.
-   **Solution:** Uninstall the incompatible libraries and reinstall CPU-specific/headless versions.
    ```bash
    # Uninstall old packages
    pip uninstall tensorflow tensorflow-io-gcs-filesystem mediapipe opencv-python opencv-contrib-python -y

    # Install CPU-compatible packages
    pip install tensorflow-cpu opencv-python-headless mediapipe
    ```

---

### Issue 4: Frontend `SyntaxError`

-   **Problem:** Running `./scripts/dev.sh` started the backend successfully, but the frontend failed with `SyntaxError: Unexpected reserved word`.
-   **Diagnosis:** The warnings from `npm` and the error itself indicated that the system's Node.js version (`v12.22.9`) was too old for the project's frontend dependencies (Svelte, Vite).

---

### Issue 5: `nvm` Installation Failure

-   **Problem:** Attempting to install `nvm` (Node Version Manager) with the standard `curl` script failed with `error: git-remote-https died of signal 4`.
-   **Diagnosis:** This is another `Illegal Instruction` error, showing that the system's `git` binary is also incompatible with the old CPU.
-   **Solution:** A manual installation of `nvm` was performed to avoid using the broken `git` command.
    ```bash
    # 1. Download the source code tarball
    curl -L -o nvm.tar.gz https://github.com/nvm-sh/nvm/archive/refs/tags/v0.39.7.tar.gz

    # 2. Create directory and extract the code
    mkdir -p ~/.nvm
    tar -xzf nvm.tar.gz -C ~/.nvm --strip-components=1

    # 3. Add nvm configuration to .bashrc
    echo '' >> ~/.bashrc
    echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
    echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
    ```

---

### Issue 6: `Segmentation fault` in Frontend

-   **Problem:** Even after successfully upgrading Node.js to `v18` and then `v20`, the frontend server still crashed with `Segmentation fault (core dumped)` right after starting.
-   **Diagnosis:** This confirms the root cause. The pre-compiled Node.js binaries (`v18`, `v20`) downloaded by `nvm` are also incompatible with the server's old CPU, crashing under the load of running the Vite dev server.
-   **Solution Steps Taken:**
    1.  Upgraded to Node.js v18 (`nvm install 18`). The segfault persisted.
    2.  Identified `EBADENGINE` warnings from `npm` indicating some packages needed Node v20+.
    3.  Upgraded to Node.js v20 (`nvm install 20`). The segfault still persisted.
    4.  A full, clean `npm install` was performed after each Node.js version change.
        ```bash
        rm -rf node_modules
        rm -f package-lock.json
        npm install
        ```

---

### Next Step (Pending)

-   **Final Diagnosis:** The server's CPU is too old to run modern, standard pre-compiled binaries for essential development tools.
-   **Proposed Solution:** The only remaining technical solution on this machine is to compile Node.js from its source code. This will create a Node.js binary that is 100% compatible with the server's specific CPU.
-   **Status:** The user has decided to perform this step later.

