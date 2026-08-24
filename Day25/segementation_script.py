import cv2
import numpy as np


def to_grayscale(img_bgr):

    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)


def binary_threshold(gray, thresh_val=127, max_val=255):

    _ , result = cv2.threshold(gray, thresh_val, max_val, cv2.THRESH_BINARY)
    return result


def adaptive_threshold(gray, block_size=11, c=2):

    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c)


def otsu_threshold(gray):

    # Otsu's thresholding.Automatically computes the optimal global threshold value by maximizing between-class variance (works best on bimodal histograms).A light Gaussian blur first reduces noise-driven histogram spikes.
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh_val, result = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return result, thresh_val


def watershed_segmentation(img_bgr):

    # Returns the original image with segment boundaries drawn in red, plus the raw markers array.
    gray = to_grayscale(img_bgr)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(
        blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # remove small noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)

    # sure background
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    # sure foreground via distance transform
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.5 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)

    # unknown region = background - foreground
    unknown = cv2.subtract(sure_bg, sure_fg)

   
    _ , markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    markers = cv2.watershed(img_bgr.copy(), markers)
    output = img_bgr.copy()
    output[markers == -1] = [0, 0, 255]  # red boundaries

    return output, markers


def remove_background_grabcut(img_bgr, rect=None, iterations=5):

    h, w = img_bgr.shape[:2]
    if rect is None:
        margin_x, margin_y = int(w * 0.05), int(h * 0.05)
        rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    cv2.grabCut(img_bgr, mask, rect, bgd_model, fgd_model, iterations, cv2.GC_INIT_WITH_RECT)

    # 0/2 = background, 1/3 = foreground
    binary_mask = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

    foreground = img_bgr * binary_mask[:, :, np.newaxis]
    white_bg = np.full_like(img_bgr, 255)
    result = np.where(binary_mask[:, :, np.newaxis] == 1, foreground, white_bg)

    return result, binary_mask * 255


def simple_foreground_mask(gray):

    otsu_result, _ = otsu_threshold(gray)
    white_ratio = np.count_nonzero(otsu_result == 255) / otsu_result.size
    if white_ratio > 0.5:
        # background is the majority white -> invert so foreground = white
        otsu_result = cv2.bitwise_not(otsu_result)
    return otsu_result