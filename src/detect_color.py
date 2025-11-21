# detectcolor.py
import cv2
import numpy as np

# Tuned general ranges (can be adjusted later)
COLOR_RANGES = {
    "garbage": [  # black
        (np.array([0, 0, 0]), np.array([180, 255, 60]))
    ],
    "recycling": [  # blue
        (np.array([85, 80, 20]), np.array([140, 255, 255]))
    ],
    "compost": [  # green
        (np.array([35, 40, 40]), np.array([90, 255, 255]))
    ]
}


def classify_color(frame):
    """
    Returns: 'garbage', 'recycling', 'compost', or 'unknown'
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for label, ranges in COLOR_RANGES.items():
        mask_total = None

        for (lower, upper) in ranges:
            mask = cv2.inRange(hsv, lower, upper)
            mask_total = mask if mask_total is None else mask_total + mask

        # Check coverage
        coverage = cv2.countNonZero(mask_total)

        if coverage > 5000:  # adjust depending on camera distance
            return label

    return "unknown"









##Commented out old code below##


# #!/usr/bin/env python3
# import cv2
# import numpy as np

# # ---------------------------------------------------------
# # Color ranges in HSV for black, blue, and green
# # ---------------------------------------------------------
# COLOR_RANGES = {
#     "black": [
#         (np.array([0, 0, 0]), np.array([180, 255, 70]))  # dark values = black
#     ],
#     "blue": [
#         (np.array([94, 80, 2]), np.array([126, 255, 255]))
#     ],
#     "green": [
#         (np.array([36, 100, 100]), np.array([86, 255, 255]))
#     ]
# }

# # BGR colors for drawing rectangles (adapted for detection with the webcam)
# DRAW_COLORS = {
#     "black": (0, 0, 0),
#     "blue": (255, 0, 0),
#     "green": (0, 255, 0)
# }


# def detect_color(frame, hsv_frame, color_name, ranges):
#     """
#     Detects a specific color and draws bounding boxes.
#     """
#     # Combine multiple ranges (for colors that span across hue)
#     mask_total = None
#     for (lower, upper) in ranges:
#         mask = cv2.inRange(hsv_frame, lower, upper)
#         mask_total = mask if mask_total is None else mask_total + mask

#     # Clean the mask
#     kernel = np.ones((5, 5), np.uint8)
#     mask_clean = cv2.morphologyEx(mask_total, cv2.MORPH_OPEN, kernel)
#     mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_DILATE, kernel)

#     # Contours
#     contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     for cnt in contours:
#         if cv2.contourArea(cnt) > 800:  # filter small noise
#             x, y, w, h = cv2.boundingRect(cnt)
#             cv2.rectangle(frame, (x, y), (x + w, y + h), DRAW_COLORS[color_name], 2)
#             cv2.putText(frame, color_name.upper(), (x, y - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, DRAW_COLORS[color_name], 2)

#     return mask_clean


# def main():
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("❌ Could not open camera")
#         return

#     print("🎥 Camera active — detecting BLACK, BLUE, GREEN (press 'q' to quit)")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

#         # Masks display window
#         mask_display = np.zeros(frame.shape[:2], dtype=np.uint8)

#         # Detect each color
#         for color_name, ranges in COLOR_RANGES.items():
#             mask_clean = detect_color(frame, hsv, color_name, ranges)
#             mask_display = cv2.bitwise_or(mask_display, mask_clean)

#         # Show everything
#         cv2.imshow("Color Detection", frame)
#         cv2.imshow("Masks (Combined)", mask_display)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()
