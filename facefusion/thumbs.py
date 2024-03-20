import os
import cv2

def gen_tumb(file_path, output_thumb_name):
  """Extract frames from the video and creates thumbnails for one of each"""
  # Extract frames from video
  print("Extract frames from video and save")
  frames = video_to_frames(file_path)
  os.makedirs('/usr/src/app/thumbs', exist_ok=True)
  thumb_path = f'/usr/src/app/thumbs/{output_thumb_name}.png'
  cv2.imwrite(thumb_path, frames[0])

  return thumb_path

def video_to_frames(video_filename):
    """Extract frames from video"""
    cap = cv2.VideoCapture(video_filename)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    frames = []
    if cap.isOpened() and video_length > 0:
        frame_ids = [0]
        if video_length >= 4:
            frame_ids = [
                         round(video_length * 0.5),
                        ]
        count = 0
        success, image = cap.read()
        while success:
            if count in frame_ids:
                frames.append(image)
            success, image = cap.read()
            count += 1
    return frames
