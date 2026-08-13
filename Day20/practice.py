import cv2



# Complete the following tasks:

# Read a video using OpenCV.
# Display the video frame by frame.
# Print the video's FPS, width, height, and total number of frames.
# Convert each frame to grayscale.
# Apply Canny Edge Detection to each frame.
# Save the processed video.
# Capture live video from your webcam and display it in real time.


def pretrained_video():

    cap = cv2.VideoCapture("input_video.mp4")

    fps = cap.get(cv2.CAP_PROP_FPS) # fps ratio
    # Resolution of each image:
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # total nunber of frames,live video footage does not have this.


    print(f"FPS: {fps}")
    print(f"Width: {width}, Height: {height}")
    print(f"Total Frames: {total_frames}")
    
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output.avi', fourcc, fps, (width, height), isColor = True)


    while True:

        ret, frame = cap.read()

        if ret is False:
            break

        
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



    while True:

        ret_cam, frame_cam = cam.read()

        if ret_cam is False:
            break

        gray = cv2.cvtColor(frame_cam, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (11,11), 0)
        canny = cv2.Canny(blur, 40, 70)

        can_bgr = cv2.cvtColor(canny, cv2.COLOR_GRAY2BGR)

        out_cam.write(can_bgr)

        cv2.imshow("Original", frame_cam)
        cv2.imshow("Canny", canny)

        if cv2.waitKey(1) == ord("q"):
            break


    
    out_cam.release() 
    cam.release()
    cv2.destroyAllWindows()     


functions = [pretrained_video,live_cam]
user = input("Enter the function you want to run? (pretrained_video,live_cam) pick 1 or 2. ")
if user == "1":
    pretrained_video()
elif user == "2":
    live_cam()
else:
    print("Plz enter valid input.")