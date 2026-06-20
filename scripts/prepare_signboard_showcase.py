import cv2
import numpy as np
from pathlib import Path

out = Path("data/sample_images/signboard_showcase")
out.mkdir(parents=True, exist_ok=True)

def base():
    img = np.ones((720, 1280, 3), dtype=np.uint8) * 235
    cv2.rectangle(img, (0, 0), (1280, 120), (70, 70, 70), -1)
    cv2.rectangle(img, (0, 520), (1280, 720), (90, 90, 90), -1)
    cv2.line(img, (0, 620), (1280, 620), (255, 255, 255), 6)
    return img

def save_no_entry():
    img = base()
    cv2.circle(img, (640, 300), 120, (0, 0, 220), -1)
    cv2.rectangle(img, (540, 275), (740, 325), (255, 255, 255), -1)
    cv2.putText(img, "NO ENTRY", (500, 470), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3)
    cv2.imwrite(str(out / "signboard_showcase_01_no_entry.jpg"), img)

def save_stop():
    img = base()
    pts = np.array([[590, 160], [690, 160], [760, 230], [760, 330], [690, 400], [590, 400], [520, 330], [520, 230]], np.int32)
    cv2.fillPoly(img, [pts], (0, 0, 220))
    cv2.putText(img, "STOP", (555, 305), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 5)
    cv2.imwrite(str(out / "signboard_showcase_02_stop.jpg"), img)

def save_speed():
    img = base()
    cv2.circle(img, (640, 300), 130, (0, 0, 220), -1)
    cv2.circle(img, (640, 300), 100, (255, 255, 255), -1)
    cv2.putText(img, "40", (585, 325), cv2.FONT_HERSHEY_SIMPLEX, 2.4, (0, 0, 0), 6)
    cv2.putText(img, "SPEED LIMIT", (480, 470), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
    cv2.imwrite(str(out / "signboard_showcase_03_speed_40.jpg"), img)

def save_turn():
    img = base()
    cv2.rectangle(img, (500, 170), (780, 430), (255, 255, 255), -1)
    cv2.rectangle(img, (500, 170), (780, 430), (0, 0, 0), 4)
    cv2.arrowedLine(img, (570, 300), (730, 300), (0, 0, 0), 18, tipLength=0.35)
    cv2.putText(img, "RIGHT TURN", (470, 480), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
    cv2.imwrite(str(out / "signboard_showcase_04_right_turn.jpg"), img)

save_no_entry()
save_stop()
save_speed()
save_turn()

print("Created signboard showcase images:", len(list(out.glob("*.jpg"))))
