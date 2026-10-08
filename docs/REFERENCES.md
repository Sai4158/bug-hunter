# References and acknowledgments

Primary documentation used by the project, checked October 8, 2026:

| Tool / source | Use and reference |
| --- | --- |
| Python | Runtime, environments, subprocesses: [Python documentation](https://docs.python.org/3/), [venv](https://docs.python.org/3/library/venv.html) |
| Streamlit | Local interface and UI tests: [documentation](https://docs.streamlit.io/), [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing) |
| Ollama | Local inference and structured chat: [API chat](https://docs.ollama.com/api/chat), [structured outputs](https://docs.ollama.com/capabilities/structured-outputs) |
| Qwen2.5-Coder | Local coding models distributed through [Ollama model library](https://ollama.com/library/qwen2.5-coder) |
| Pylint | Independent static-analysis baseline: [documentation](https://pylint.readthedocs.io/en/stable/) |
| pytest | Before/after checks and regression tests: [usage documentation](https://docs.pytest.org/en/stable/how-to/usage.html) |
| Pydantic | Model-output schemas and validation: [documentation](https://docs.pydantic.dev/latest/) |
| Requests | Local HTTP client: [documentation](https://requests.readthedocs.io/en/latest/) |
| pandas | Evaluation CSV/table handling: [documentation](https://pandas.pydata.org/docs/) |
| psutil | Process identity and helper-owned shutdown: [documentation](https://psutil.readthedocs.io/) |
| Docker Compose | Optional local Ollama environment: [documentation](https://docs.docker.com/compose/) |
| WinGet | Approved Windows prerequisite installation: [official documentation](https://learn.microsoft.com/en-us/windows/package-manager/winget/) |
| GitHub Actions | Automated platform verification: [Python workflow guidance](https://docs.github.com/en/actions/tutorials/build-and-test-code/python), [secure action pinning](https://docs.github.com/en/actions/reference/security/secure-use) |

Bug Hunter was developed as a Penn State SWENG 889 group-project proof of concept.
The standalone repository is maintained under the GitHub account `Sai4158`.
Codex assisted with development, documentation, and verification at the user's
direction. This acknowledgment is not a claim that all generated suggestions
were correct or that every teammate made a particular contribution.

The application's runtime AI is **local Ollama with Qwen coding models**, not an
OpenAI API. The 12 controlled cases, test controls, recorded results, and separate
human-review workflow are project artifacts. Do not replace missing human reviews
with AI-generated accuracy judgments.

Third-party software and model licenses remain their own. Check upstream terms
when redistributing dependencies or model weights; model weights are not included
in this repository. This reference list does not grant a new license to Bug Hunter
or imply endorsement by tool authors or Penn State.
