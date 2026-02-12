import asyncio
import logging

logger = logging.getLogger(__name__)

# Maximum time (seconds) a command is allowed to run before being killed.
DEFAULT_TIMEOUT = 60


async def run_shell_command(
    command: str,
    cwd: str = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> tuple[bool, str]:
    """Run a shell command asynchronously and return (success, output).

    Parameters
    ----------
    command : str
        The shell command to execute.
    cwd : str, optional
        Working directory for the command.
    timeout : int
        Maximum seconds to wait before killing the process.

    Returns
    -------
    tuple[bool, str]
        A tuple of (success: bool, combined_output: str).
    """
    try:
        logger.info("Executing: %s (cwd=%s)", command, cwd)

        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            return False, f"Command timed out after {timeout}s: {command}"

        output = stdout.decode('utf-8', errors='replace')
        err_output = stderr.decode('utf-8', errors='replace')

        # Combine stdout and stderr, but label stderr if both are present.
        if output and err_output:
            combined = f"{output}\n--- stderr ---\n{err_output}"
        elif err_output:
            combined = err_output
        else:
            combined = output

        if not combined.strip():
            combined = "(no output)"

        success = process.returncode == 0
        return success, combined.strip()

    except Exception as e:
        logger.exception("Failed to execute command: %s", command)
        return False, f"Error: {e}"
