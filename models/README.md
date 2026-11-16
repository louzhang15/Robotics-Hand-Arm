# Camera model

Download the **Hand Landmarker** task model linked from
[Google's official guide](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
and save it here as `hand_landmarker.task`.

The model weights are not bundled in the Git repository or project ZIP. Review
the publisher's model terms. The software never silently downloads a model.

With the camera dependencies installed, use:

```powershell
python pc/camera.py --model models/hand_landmarker.task --dry
```

During this build pass, MediaPipe 1.2.3, OpenCV contrib 5.0.0.93 (cv2 5.0.0),
NumPy 2.2.6 and the exact HandLandmarker VIDEO options used by the application
were import/constructor checked locally. The model was not downloaded and no
inference or live webcam test was performed. Install only one OpenCV provider;
the camera requirements use opencv-contrib-python, which MediaPipe also requires.
