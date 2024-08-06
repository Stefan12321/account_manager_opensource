import logging


def setup_logger_for_thread(path, thread_name) -> logging.Logger:
    # Create a logger for the thread
    logger = logging.getLogger(thread_name)
    logger.setLevel(logging.INFO)

    # Create a file handler to write log messages to a file
    log_file = fr"{path}/logs/{thread_name}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create a stream handler that displays logs in the terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # Create a formatter to specify the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    # Set the logger as the default logger for the thread
    # logging.root = logger
    return logger