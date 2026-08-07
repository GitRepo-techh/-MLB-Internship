import cv2
import numpy as np




def to_grayscale(image):


    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def resize_image(image, width=None, height=None, scale=None):


    if scale is not None:
        return cv2.resize(image, (0, 0), fx=scale, fy=scale)
    if width is None or height is None:
        raise ValueError("Provide either scale, or both width and height.")
    return cv2.resize(image, (width, height))


def rotate_image(image, angle):


    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, matrix, (w, h))


def flip_image(image, mode="horizontal"):


    flip_code = {"horizontal": 1, "vertical": 0, "both": -1}
    if mode not in flip_code:
        raise ValueError("mode must be 'horizontal', 'vertical' or 'both'")
    return cv2.flip(image, flip_code[mode])


def crop_image(image, x1, y1, x2, y2):


    h, w = image.shape[:2]
    x1, x2 = sorted((max(0, min(x1, w)), max(0, min(x2, w))))
    y1, y2 = sorted((max(0, min(y1, h)), max(0, min(y2, h))))
    return image[y1:y2, x1:x2]




def draw_rectangle(image, pt1, pt2, color=(234, 65, 136), thickness=2):
    out = image.copy()
    cv2.rectangle(out, pt1, pt2, color, thickness)
    return out


def draw_line(image, pt1, pt2, color=(255, 32, 0), thickness=2):
    out = image.copy()
    cv2.line(out, pt1, pt2, color, thickness)
    return out


def draw_circle(image, center, radius, color=(10, 25, 100), thickness=2):
    out = image.copy()
    cv2.circle(out, center, radius, color, thickness)
    return out


def draw_polygon(image, points, color=(0, 255, 0), thickness=2, closed=True):
    """points: list of (x, y) tuples."""
    out = image.copy()
    pts = np.array(points, np.int32).reshape((-1, 1, 2))
    cv2.polylines(out, [pts], closed, color, thickness)
    return out


def add_text(image, text, position=(10, 100), color=(0, 0, 255),
             font_scale=1, thickness=2, font=cv2.FONT_HERSHEY_SIMPLEX):
    out = image.copy()
    cv2.putText(out, text, position, font, font_scale, color, thickness)
    return out


# ---------------------------------------------------------------------
# UNDO SUPPORT (history stack helpers -- use with st.session_state)
# ---------------------------------------------------------------------
# In app.py:
#   if "history" not in st.session_state:
#       st.session_state.history = [original_image]
#
#   # after ANY operation (draw, crop, rotate, etc.):
#   st.session_state.history.append(new_image)
#
#   # current image to display/process is always:
#   current_image = st.session_state.history[-1]
#
#   # Undo button:
#   if st.button("Undo") and len(st.session_state.history) > 1:
#       st.session_state.history = undo(st.session_state.history)

def undo(history):
    """Pop the last state off a history stack, keeping at least the
    original image (index 0) so undo can never leave you with nothing."""
    if len(history) > 1:
        history.pop()
    return history


# ---------------------------------------------------------------------
# SAVE / DOWNLOAD
# ---------------------------------------------------------------------

def encode_for_download(image, ext=".png"):

  
    success, buffer = cv2.imencode(ext, image)
    if not success:
        raise ValueError("Could not encode image for download.")
    return buffer.tobytes()


def save_image(image, path):
    """Save directly to disk instead of/in addition to a download button."""
    cv2.imwrite(path, image)
    return path