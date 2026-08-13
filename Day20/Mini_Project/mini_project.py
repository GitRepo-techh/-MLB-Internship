import cv2



# Build a Python application that processes both a recorded video and your webcam feed.

# Your application should:
# Read a video file.
# Display the original and processed frames.
# Convert frames to grayscale.
# Apply Gaussian Blur.
# Apply Canny Edge Detection.
# Display the processed video in real time.
# Save the processed video as a new file.


def pretrained_video(video_path, output_path):

    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS) # fps ratio
    # Resolution of each image:
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # total nunber of frames,live video footage does not have this.


    print(f"FPS: {fps}")
    print(f"Width: {width}, Height: {height}")
    print(f"Total Frames: {total_frames}")
    
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor = True)

    if not cap.isOpened():
      print("Error: could not open video source.")
      return

    while True:

        ret, frame = cap.read()

        if ret is False:
            break

        frame = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(15,15), 0) # This helps reduce the noise in the video.
        canny = cv2.Canny(blur, 50, 90)

        canny_bgr = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)

        out.write(canny_bgr)

        cv2.imshow("Original", frame)
        cv2.imshow("Blur", blur)
        cv2.imshow("Canny Edges", canny)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
          break

    cap.release()
    out.release()                 # finalizes the output file
    cv2.destroyAllWindows()


def live_cam():
    cam = cv2.VideoCapture(0)

    fps_cam = cam.get(cv2.CAP_PROP_FPS)

    w = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH)) 
    h = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))



    print(f"FPS: {fps_cam}")
    print(f"Width: {w}, Height: {h}")


    fourcc_cam = cv2.VideoWriter_fourcc(*'MJPG')
    out_cam = cv2.VideoWriter('output_cam.avi', fourcc_cam, fps_cam, (w, h), isColor = True)

    if not cam.isOpened():
        print("Error: could not open video source.")
        return


    while True:

        ret_cam, frame_cam = cam.read()

        if ret_cam is False:
            break

        gray = cv2.cvtColor(frame_cam, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (11,11), 0)
        canny = cv2.Canny(blur, 40, 80)

        can_bgr = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)

        out_cam.write(can_bgr)

        cv2.imshow("Original", frame_cam)
        cv2.imshow("Canny", canny)

        if cv2.waitKey(1) == ord("q"):
            break


    
    out_cam.release() 
    cam.release()
    cv2.destroyAllWindows()     


videos = {
    "video1.mp4": "output1.avi",
    "video2.mp4": "output2.avi",
    "video3.mp4": "output3.avi",
}
 
for input_video, output_video in videos.items():
    pretrained_video(input_video, output_video)
functions = [live_cam]
user = input("Run live webcam? (y/n) ")
if user.lower() == "y":
    live_cam()
