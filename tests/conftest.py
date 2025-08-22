import logging
import os
import subprocess
from collections.abc import Iterator

import pytest
from pylspclient.json_rpc_endpoint import JsonRpcEndpoint
from pylspclient.lsp_client import LspClient
from pylspclient.lsp_endpoint import LspEndpoint

import clangd

log = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def clangd_server() -> Iterator[subprocess.Popen]:
    command = clangd._get_executable("clangd")

    log.info(f"Starting clangd server with command: {command.as_posix()}")

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # Potential deadlock, can redirect to file if needed
        # stderr=subprocess.PIPE,
    )

    yield process

    log.info("Tearing down clangd server...")
    if process.poll() is not None:
        log.info("clangd server is already stopped.")
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        log.warning("clangd did not terminate gracefully, killing.")
        process.kill()
        pytest.fail("clangd server did not shut down cleanly.")

    log.debug("clangd server stopped.")


@pytest.fixture(scope="function")
def lsp_client(clangd_server: subprocess.Popen) -> Iterator[LspClient]:
    endpoint = JsonRpcEndpoint(clangd_server.stdin, clangd_server.stdout)
    lsp_endpoint = LspEndpoint(endpoint)

    client = LspClient(lsp_endpoint)
    root_uri = f"file://{os.getcwd()}"

    log.info("Initializing LSP client...")
    response = client.initialize(
        processId=clangd_server.pid,
        rootPath=None,
        rootUri=root_uri,
        initializationOptions=None,
        capabilities=None,
        trace="off",
        workspaceFolders=None,
    )

    assert response is not None, "Initialization response should not be None."
    client.initialized()
    log.debug("LSP client initialized successfully.")

    yield client

    log.info("Shutting down LSP client...")
    client.shutdown()
    client.exit()
    log.debug("LSP client shut down.")
