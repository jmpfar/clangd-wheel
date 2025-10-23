import logging
import subprocess
from pathlib import Path
import time

import pylspclient.lsp_pydantic_strcuts as lsp_structs
from pylspclient.json_rpc_endpoint import JsonRpcEndpoint
from pylspclient.lsp_client import LspClient
from pylspclient.lsp_endpoint import LspEndpoint
import pytest

log = logging.getLogger(__name__)


def test_init_shutdown_lsp(clangd_server: subprocess.Popen):
    """
    Initializes the LSP client and sends a shutdown request to clangd.
    """

    endpoint = JsonRpcEndpoint(clangd_server.stdin, clangd_server.stdout)
    lsp_endpoint = LspEndpoint(endpoint)

    client = LspClient(lsp_endpoint)

    log.info("Initializing LSP client...")
    response = client.initialize(
        processId=clangd_server.pid,
        rootPath=None,
        rootUri=None,
        initializationOptions=None,
        capabilities=None,
        trace="off",
        workspaceFolders=None,
    )

    assert response is not None, "Initialization response should not be None."
    client.initialized()
    log.info("LSP client initialized successfully.")

    client.shutdown()
    log.info("Shutdown request sent to clangd.")
    client.exit()

    log.info("Waiting for clangd to stop")
    return_code = clangd_server.wait(timeout=2)

    assert return_code == 0, (
        "clangd server should be stopped successfuly after shutdown."
    )


TEST_COMPLETION_CPP = """#include <string>

struct Vec2 {
    double x;
    double y;
};

int main() {
    Vec2 p;
    p.
    return 0;
}"""


def test_clangd_completion(lsp_client: LspClient, clangd_root_dir: Path):
    """
    Tests that clangd provides correct member completions for a struct variable.
    """
    cpp_path = clangd_root_dir / "test_completion.cpp"
    cpp_path.write_text(TEST_COMPLETION_CPP)
    cpp_uri = cpp_path.as_uri()

    lsp_client.didOpen(
        lsp_structs.TextDocumentItem(
            uri=cpp_uri,
            languageId=lsp_structs.LanguageIdentifier.CPP,
            version=1,
            text=TEST_COMPLETION_CPP,
        )
    )

    completion_pos = lsp_structs.Position(line=9, character=6)
    log.info(
        f"Requesting completions at Line {completion_pos.line}, Char {completion_pos.character}"
    )

    response = lsp_client.completion(
        lsp_structs.TextDocumentIdentifier(uri=cpp_uri),
        completion_pos,
        lsp_structs.CompletionContext(
            triggerKind=lsp_structs.CompletionTriggerKind.Invoked
        ),
    )

    assert response is not None, "Did not receive a completion response."
    completion_items = response.items
    assert len(completion_items) > 0, "Completion response has no items."

    completions = {item.insertText for item in completion_items}
    log.info(f"Received completions text: {completions}")

    expected_completions = {"x", "y"}
    missing = expected_completions - completions
    assert not missing, f"Expected completions not found: {missing}"


TEST_DIAGNOSTICS_CPP = """
int main() {
    int x = 3 + 3
    return x;
}"""


@pytest.mark.timeout(5)
def test_clangd_diagnostics(lsp_client: LspClient, clangd_root_dir: Path):
    """
    Tests that clangd correctly reports syntax errors.
    """
    cpp_path = clangd_root_dir / "test_diagnostics.cpp"
    cpp_path.write_text(TEST_DIAGNOSTICS_CPP)
    cpp_uri = cpp_path.as_uri()

    diagnostics = []

    lsp_client.lsp_endpoint.notify_callbacks = {
        "textDocument/publishDiagnostics": lambda params: diagnostics.extend(
            params["diagnostics"]
        )
    }

    lsp_client.didOpen(
        lsp_structs.TextDocumentItem(
            uri=cpp_uri,
            languageId=lsp_structs.LanguageIdentifier.CPP,
            version=1,
            text=TEST_DIAGNOSTICS_CPP,
        )
    )

    log.info("Waiting for diagnostics to be reported...")
    while len(diagnostics) == 0:
        time.sleep(0.5)

    diagnostic_codes = [d["code"] for d in diagnostics]
    assert "expected_semi_declaration" in diagnostic_codes, (
        "Expected semicolon syntax error not found in diagnostics."
    )
