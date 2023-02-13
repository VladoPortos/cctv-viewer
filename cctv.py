import cv2
import threading
import queue
import numpy as np
import platform
import ctypes
import tkinter as tk
# tkinter require package: python3-tk

# Define the RTP stream URLs
streams = [
    "rtsp://<USER>:<PASS>@<IP>/Streaming/Channels/102",
    "rtsp://<USER>:<PASS>@<IP>/Streaming/Channels/102",
    "rtsp://<USER>:<PASS>@<IP>/Streaming/Channels/102",
    "rtsp://<USER>:<PASS>@<IP>/Streaming/Channels/102"
]

# Define the buffer time
buffer_time = 3

# Define the buffer frame count
fps = 24
buffer_frame_count = fps * buffer_time

# Create a queue for the frames
frame_queue = queue.Queue(maxsize=buffer_frame_count)

# Define the capture function


def capture(stream, queue, idx, stop):
    cap = cv2.VideoCapture(stream)
    while not stop.is_set():
        ret, frame = cap.read()
        if ret:
            if queue.full():
                queue.get()
            queue.put((frame, idx))
        else:
            break
    cap.release()


# Start the capture threads
stop = threading.Event()
threads = [threading.Thread(target=capture, args=(
    stream, frame_queue, idx, stop)) for idx, stream in enumerate(streams)]
for thread in threads:
    thread.start()

# Create the main window
cv2.namedWindow("Streams", cv2.WINDOW_NORMAL)

# Get the screen size
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

# Define the window size
window_size = (screen_width, screen_height)

# Resize the window to full screen
cv2.setWindowProperty("Streams", cv2.WND_PROP_FULLSCREEN,
                      cv2.WINDOW_FULLSCREEN)

# Define the buffer
buffer = [None for _ in range(4)]

# Define the maximize flag
maximize = [False for _ in range(4)]

# Loop until user presses 'q'
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('1'):
        if maximize[0]:
            maximize = [False for i in range(4)]
        else:
            maximize = [True if i == 0 else False for i in range(4)]
    elif key == ord('2'):
        if maximize[1]:
            maximize = [False for i in range(4)]
        else:
            maximize = [True if i == 1 else False for i in range(4)]
    elif key == ord('3'):
        if maximize[2]:
            maximize = [False for i in range(4)]
        else:
            maximize = [True if i == 2 else False for i in range(4)]
    elif key == ord('4'):
        if maximize[3]:
            maximize = [False for i in range(4)]
        else:
            maximize = [True if i == 3 else False for i in range(4)]

    if maximize.count(True) == 1:
        if not frame_queue.empty():
            frame, idx = frame_queue.get()
            buffer[idx] = frame
        else:
            continue
        if all(b is not None for b in buffer):
            idx = maximize.index(True)
            frame = cv2.resize(buffer[idx], (window_size[0], window_size[1]))
            cv2.imshow("Streams", frame)
    else:
        if not frame_queue.empty():
            frame, idx = frame_queue.get()
            buffer[idx] = frame
        else:
            continue
        if all(b is not None for b in buffer):
            frame1 = cv2.resize(buffer[0], (screen_width//2, screen_height//2))
            frame2 = cv2.resize(buffer[1], (screen_width//2, screen_height//2))
            frame3 = cv2.resize(buffer[2], (screen_width//2, screen_height//2))
            frame4 = cv2.resize(buffer[3], (screen_width//2, screen_height//2))
            frame = np.vstack((np.hstack((frame1, frame2)),
                              np.hstack((frame3, frame4))))
            cv2.imshow("Streams", frame)
    if key == ord('q'):
        break


# Destroy the window
cv2.destroyAllWindows()

# Release the capture
stop.set()
for thread in threads:
    thread.join()
