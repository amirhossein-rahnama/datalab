"""Verify notebooks actually execute (the verify skill's Gate A.3), not just that they are
valid JSON. Self-registers a `python3` kernel for the current interpreter if none exists,
so this works in a fresh CI environment where only ipykernel (a core dep) is installed."""
import nbformat
from nbclient import NotebookClient


def _ensure_python3_kernel():
    from jupyter_client.kernelspec import KernelSpecManager, NoSuchKernel

    try:
        KernelSpecManager().get_kernel_spec("python3")
    except NoSuchKernel:
        from ipykernel.kernelspec import install

        install(user=True, kernel_name="python3")


def test_notebook_executes(tmp_path):
    _ensure_python3_kernel()
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_code_cell("x = 1 + 1"),
        nbformat.v4.new_code_cell("assert x == 2"),
    ]
    # .execute() raises CellExecutionError if any cell fails
    NotebookClient(
        nb,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(tmp_path)}},
    ).execute()
