"""
Production-Grade Logging System for YOLO Ensemble Pipeline
Provides structured logging with console and file output
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class PipelineLogger:
    """Centralized logging system for the pipeline"""

    def __init__(
        self,
        name: str = "YOLOEnsemble",
        log_file: Optional[str] = None,
        level: str = "INFO",
        console_output: bool = True
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers.clear()

        # Create formatters
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        self.stats = {
            'debug': 0,
            'info': 0,
            'warning': 0,
            'error': 0,
            'critical': 0
        }

    def debug(self, message: str):
        self.logger.debug(message)
        self.stats['debug'] += 1

    def info(self, message: str):
        self.logger.info(message)
        self.stats['info'] += 1

    def warning(self, message: str):
        self.logger.warning(message)
        self.stats['warning'] += 1

    def error(self, message: str):
        self.logger.error(message)
        self.stats['error'] += 1

    def critical(self, message: str):
        self.logger.critical(message)
        self.stats['critical'] += 1

    def section(self, title: str):
        """Log a section header"""
        separator = "=" * 80
        self.info(f"\n{separator}")
        self.info(f"  {title}")
        self.info(f"{separator}")

    def subsection(self, title: str):
        """Log a subsection header"""
        self.info(f"\n--- {title} ---")

    def success(self, message: str):
        """Log a success message"""
        self.info(f"✓ {message}")

    def failure(self, message: str):
        """Log a failure message"""
        self.error(f"✗ {message}")

    def get_stats(self) -> dict:
        """Get logging statistics"""
        return self.stats.copy()

    def save_report(self, output_path: str, data: dict):
        """Save a JSON report"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.info(f"Report saved: {output_file}")


def get_logger(
    name: str = "YOLOEnsemble",
    log_file: Optional[str] = None,
    level: str = "INFO",
    console_output: bool = True
) -> PipelineLogger:
    """Factory function to create a logger"""
    return PipelineLogger(name, log_file, level, console_output)
