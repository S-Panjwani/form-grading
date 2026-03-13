import cv2
import mediapipe as mp
import json

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# --- Config ---
INPUT_SOURCE = "video.mp4"
OUTPUT_VIDEO = "output.mp4"
OUTPUT_DATA  = "pose_data.json"
TARGET_FPS   = 12
# --------------

cap = cv2.VideoCapture(INPUT_SOURCE)
source_fps = cap.get(cv2.CAP_PROP_FPS) or 30
frame_interval = max(1, round(source_fps / TARGET_FPS))

width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

writer = cv2.VideoWriter(OUTPUT_VIDEO,
                         cv2.VideoWriter_fourcc(*"mp4v"),
                         TARGET_FPS, (width, height))

all_frames = []
frame_index = 0
analyzed_index = 0

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    frame_index += 1

    if frame_index % frame_interval != 0:
        continue

    timestamp = frame_index / source_fps

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    frame_data = {
        "frame":     frame_index,
        "analyzed":  analyzed_index,
        "timestamp": round(timestamp, 4),
        "landmarks": None
    }

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        frame_data["landmarks"] = [
            {
                "id":         i,
                "name":       mp_pose.PoseLandmark(i).name,
                "x":          round(lm.x, 6),
                "y":          round(lm.y, 6),
                "z":          round(lm.z, 6),
                "visibility": round(lm.visibility, 4)
            }
            for i, lm in enumerate(results.pose_landmarks.landmark)
            if i in {7, 8, 11, 12, 13, 14, 15, 16}
        ]

    all_frames.append(frame_data)
    analyzed_index += 1

    cv2.putText(image, f"Frame: {frame_index}  T: {timestamp:.2f}s",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    writer.write(image)
    cv2.imshow("Pose Tracking (12fps)", image)

    if cv2.waitKey(1) & 0xFF == 27:
        break

with open(OUTPUT_DATA, "w") as f:
    json.dump({"target_fps": TARGET_FPS,
               "total_analyzed_frames": analyzed_index,
               "frames": all_frames}, f, indent=2)

print(f"Done. Analyzed {analyzed_index} frames.")
print(f"Video saved to: {OUTPUT_VIDEO}")
print(f"Pose data saved to: {OUTPUT_DATA}")

cap.release()
writer.release()
cv2.destroyAllWindows()