LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s\t%(levelname)s\t%(filename)s\t%(funcName)s\t%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "basic": {
            "format": "%(asctime)s %(levelname)s-8s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "basic",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": "vgarus.log",
        },
    },
    "loggers": {
        "vgarus": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
        }
    },
}
