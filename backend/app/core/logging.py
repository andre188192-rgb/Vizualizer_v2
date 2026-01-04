import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='{"level":"%(levelname)s","time":"%(asctime)s","message":"%(message)s"}',
    )
