import numpy as np
import matplotlib.pyplot as plt
import os

from mpl_toolkits.mplot3d import Axes3D
from joblib import Parallel, delayed
import multiprocessing
import ipywidgets as widgets
from moviepy.video.VideoClip import VideoClip
from moviepy.video.fx import Crop
from IPython.display import Video

import cv2



def movie_traces(img_path, data_samples, index, video_path):

    if index == 9:
        print(9)

    Fs = 1000
    fps = 50
    dot_radius = 10
    alpha = 0.5
    speed_koef = 1
    speed_koef = 5

    x = np.array(data_samples['x'])
    y = np.array(data_samples['y'])
    
    x_sub = x[::int(Fs/(speed_koef*fps))] #speed_koef*fps = 50
    y_sub = y[::int(Fs/(speed_koef*fps))] #fps = 50

    background_img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)

   # background_img = cv2.imread(img_path)
    cv2.imshow('img', background_img)



    clips = []

    data_samples['time_sec'] = (data_samples['time'] - data_samples['time'].iloc[0])/1000.0
    duration = data_samples['time_sec'].iloc[-1]

    duration = duration * speed_koef

    # for _, row in data_samples.iterrows():
    #     def make_frame(t, x=row['x'], y=row['y'], r=base_radius + row['fixation_duration'] * radius_scale):
    #         frame = background_img.copy()
    #         overlay = frame.copy()
    #         cv2.circle(overlay, (int(x), int(y)), int(r), (255, 0, 0), -1)  # red filled circle
    #         alpha = 0.5
    #         cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    #         return frame
        
    #     duration_ms = row['fixation_duration']
    #     duration_s = max(0.2, duration_ms * scale)
    #     clip = VideoClip(make_frame)


# --- Define make_frame(t): interpolate or get closest gaze point ---
    def make_frame(t):
        #t2 = t/duration
        frame = background_img.copy()
        overlay = frame.copy()
        
        # Get the closest index (or use interpolation)
        # idx = np.searchsorted(data_samples['time_sec'].values, t2)
        # if idx >= len(data_samples):
        #     idx = len(data_samples) - 1

        idx = int(t*fps)
        x_i = x_sub[idx]
        y_i = y_sub[idx]
        
        # x = int(data_samples.iloc[idx]['x'])
        # y = int(data_samples.iloc[idx]['y'])
        if not (np.isnan(x_i) or np.isnan(y_i)):
            cv2.circle(overlay, (int(x_i), int(y_i)), dot_radius, (255, 0, 0), -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        assert frame.shape == (1080, 1920, 3), f"Frame shape is {frame.shape}, expected (1080, 1920, 3)"
        return frame

    # --- Create and save clip ---
    clip = VideoClip(make_frame, duration=duration)
    filename = f'gaze_idx_{index}_vel_{speed_koef}_fps_{fps}.mp4'
    write_path = os.path.join(video_path, filename)
    clip.write_videofile(write_path, fps=fps, codec='libx264', ffmpeg_params=["-crf", "17"])

    


# def mplfig_to_npimage(fig):
#     """
#     Convert a Matplotlib figure to a NumPy RGB image array.

#     This function renders the given Matplotlib figure's canvas,
#     extracts its pixel data as an RGB byte buffer, and reshapes it
#     into a NumPy array of shape (height, width, 3) suitable for
#     image processing or video frame creation.

#     Parameters:
#     -----------
#     fig : matplotlib.figure.Figure
#         The Matplotlib figure to convert.

#     Returns:
#     --------
#     np.ndarray
#         A 3D NumPy array representing the RGB image of the figure.
#     """

#     # Render the figure canvas
#     fig.canvas.draw()
#     # Get the width and height of the figure
#     w, h = fig.canvas.get_width_height()
#     # Extract the RGB buffer from the figure
#     buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
#     # Reshape buffer to (height, width, 3)
#     buf.shape = (h, w, 3)
#     return buf


# def plt_anim(t, fig, axs=None):

#     # axs.clear()
#     # axs.axis('equal')
#     # axs.set_xlim([-2,2])
#     # axs.set_ylim([-2,2])

#     #npimage_ = moviepy.video.io.bindings.mplfig_to_npimage(fig)
#     # video.io.bindings import mplfig_to_npimage
#     return mplfig_to_npimage(fig)

# # duration = 10 #[TODO]: change to be max len of t array
# # fps = 5
# # name = 'test' #[TODO]: naming automatically from the name of initial image file

# # animation = VideoClip(lambda t: plt_anim(t), duration=duration)
# # animation.write_videofile(name+".mp4",fps=fps)


