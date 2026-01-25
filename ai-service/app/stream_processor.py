"""
Stream Processing Module for RTSP/HTTP Video Streams
"""
import cv2
import numpy as np
import asyncio
import logging
import uuid
from typing import Dict, Optional, Callable
from datetime import datetime
import threading
from queue import Queue

from .config import settings

logger = logging.getLogger(__name__)


class StreamProcessor:
    """
    Process video streams (RTSP/HTTP) for real-time detection
    """

    def __init__(self, ensemble_model):
        """
        Initialize stream processor

        Args:
            ensemble_model: YOLOv8Ensemble instance
        """
        self.model = ensemble_model
        self.active_streams: Dict[str, Dict] = {}
        self.stop_events: Dict[str, threading.Event] = {}

    async def process_stream(
        self,
        stream_url: str,
        camera_id: str,
        duration: int = 60,
        frame_skip: int = 5,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Process a video stream asynchronously

        Args:
            stream_url: RTSP or HTTP stream URL
            camera_id: Camera identifier
            duration: Processing duration in seconds
            frame_skip: Process every Nth frame
            callback: Optional callback for detections

        Returns:
            Task ID for tracking
        """
        task_id = str(uuid.uuid4())

        # Create stop event for this stream
        stop_event = threading.Event()
        self.stop_events[task_id] = stop_event

        # Store stream info
        self.active_streams[task_id] = {
            "camera_id": camera_id,
            "stream_url": stream_url,
            "status": "starting",
            "started_at": datetime.utcnow().isoformat(),
            "detections": []
        }

        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_stream_thread,
            args=(task_id, stream_url, camera_id, duration, frame_skip, callback, stop_event)
        )
        thread.daemon = True
        thread.start()

        logger.info(f"Stream processing started: task_id={task_id}, camera={camera_id}")

        return task_id

    def _process_stream_thread(
        self,
        task_id: str,
        stream_url: str,
        camera_id: str,
        duration: int,
        frame_skip: int,
        callback: Optional[Callable],
        stop_event: threading.Event
    ):
        """
        Process stream in a separate thread

        Args:
            task_id: Task identifier
            stream_url: Stream URL
            camera_id: Camera ID
            duration: Max duration in seconds
            frame_skip: Frame skip rate
            callback: Optional callback function
            stop_event: Threading event to stop processing
        """
        cap = None

        try:
            # Open video stream
            logger.info(f"Opening stream: {stream_url}")
            cap = cv2.VideoCapture(stream_url)

            if not cap.isOpened():
                logger.error(f"Failed to open stream: {stream_url}")
                self.active_streams[task_id]["status"] = "failed"
                self.active_streams[task_id]["error"] = "Failed to open stream"
                return

            self.active_streams[task_id]["status"] = "processing"

            frame_count = 0
            detection_count = 0
            start_time = datetime.utcnow()

            while not stop_event.is_set():
                # Check duration
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                if elapsed > duration:
                    logger.info(f"Stream {task_id} reached max duration")
                    break

                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Failed to read frame from stream {task_id}")
                    break

                frame_count += 1

                # Skip frames
                if frame_count % frame_skip != 0:
                    continue

                # Run detection
                try:
                    result = self.model.detect(frame, camera_id=camera_id)
                    result["timestamp"] = datetime.utcnow().isoformat() + "Z"
                    result["frame_number"] = frame_count

                    # Store detection if threat detected
                    if result["threat_detected"]:
                        detection_count += 1
                        self.active_streams[task_id]["detections"].append(result)

                        logger.info(
                            f"Stream {task_id}: Threat detected at frame {frame_count} "
                            f"({result['event']}, conf={result['confidence']:.2f})"
                        )

                        # Call callback if provided
                        if callback:
                            try:
                                callback(task_id, result)
                            except Exception as e:
                                logger.error(f"Callback error: {str(e)}")

                except Exception as e:
                    logger.error(f"Detection error in stream {task_id}: {str(e)}")

            # Processing complete
            self.active_streams[task_id]["status"] = "completed"
            self.active_streams[task_id]["frames_processed"] = frame_count
            self.active_streams[task_id]["detections_count"] = detection_count
            self.active_streams[task_id]["completed_at"] = datetime.utcnow().isoformat()

            logger.info(
                f"Stream {task_id} completed: "
                f"{frame_count} frames, {detection_count} detections"
            )

        except Exception as e:
            logger.error(f"Stream processing error: {str(e)}", exc_info=True)
            self.active_streams[task_id]["status"] = "failed"
            self.active_streams[task_id]["error"] = str(e)

        finally:
            if cap:
                cap.release()

            # Cleanup
            if task_id in self.stop_events:
                del self.stop_events[task_id]

    def stop_stream(self, task_id: str):
        """
        Stop a running stream processing task

        Args:
            task_id: Task identifier
        """
        if task_id in self.stop_events:
            logger.info(f"Stopping stream: {task_id}")
            self.stop_events[task_id].set()
            return True
        return False

    def get_stream_status(self, task_id: str) -> Optional[Dict]:
        """
        Get status of a stream processing task

        Args:
            task_id: Task identifier

        Returns:
            Stream status or None if not found
        """
        return self.active_streams.get(task_id)

    def get_all_streams(self) -> Dict[str, Dict]:
        """
        Get all active streams

        Returns:
            Dictionary of all streams
        """
        return self.active_streams

    def cleanup(self):
        """Stop all active streams"""
        logger.info("Stopping all active streams...")
        for task_id in list(self.stop_events.keys()):
            self.stop_stream(task_id)
        logger.info("All streams stopped")
