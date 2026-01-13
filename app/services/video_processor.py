"""
Video processing service for extracting frames and manipulating video files.
"""
import cv2
import os
from typing import Dict, Any, List
import numpy as np


class VideoProcessor:
    """
    Video processing utilities for dashcam videos.
    """
    
    def extract_frames(self, video_path: str, fps: int = 1) -> List[np.ndarray]:
        """
        Extract frames from video at specified frame rate.
        
        Args:
            video_path: Path to video file
            fps: Frames per second to extract (default: 1)
            
        Returns:
            List of frames as numpy arrays
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        frames = []
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video FPS
        video_fps = video.get(cv2.CAP_PROP_FPS)
        frame_interval = int(video_fps / fps) if fps < video_fps else 1
        
        frame_count = 0
        while True:
            ret, frame = video.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frames.append(frame)
            
            frame_count += 1
        
        video.release()
        return frames
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video metadata information.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video duration, resolution, codec, fps
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        info = {
            "duration": video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS),
            "width": int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": video.get(cv2.CAP_PROP_FPS),
            "frame_count": int(video.get(cv2.CAP_PROP_FRAME_COUNT)),
            "codec": int(video.get(cv2.CAP_PROP_FOURCC))
        }
        
        video.release()
        return info
    
    def compress_video(self, video_path: str, output_path: str, quality: int = 23) -> str:
        """
        Compress video using H.264 codec.
        
        Args:
            video_path: Path to input video
            output_path: Path to save compressed video
            quality: CRF quality value (0-51, lower is better quality)
            
        Returns:
            Path to compressed video
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # This is a placeholder - actual compression would use ffmpeg
        # For now, just copy the file
        import shutil
        shutil.copy(video_path, output_path)
        return output_path
    
    def generate_thumbnail(self, video_path: str, output_path: str, timestamp: float = 0.0) -> str:
        """
        Generate a thumbnail image from video.
        
        Args:
            video_path: Path to video file
            output_path: Path to save thumbnail
            timestamp: Timestamp in seconds to capture (default: 0.0)
            
        Returns:
            Path to generated thumbnail
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Set video position to timestamp
        video.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        
        # Read frame
        ret, frame = video.read()
        if not ret:
            video.release()
            raise ValueError("Could not read frame from video")
        
        # Save thumbnail
        cv2.imwrite(output_path, frame)
        
        video.release()
        return output_path
