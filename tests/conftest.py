def pytest_addoption(parser):
    parser.addoption(
        "--remote",
        action="store_true",
        default=False,
        help="Run tests remotely (e.g., via GitHub action)",
    )
