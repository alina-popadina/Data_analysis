import os
import ast
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg

import os
import ast
import cv2
import numpy as np


# def drawing_traces(stimuli_path, trial_id, timestamps=None, fixations=None, target_area=None):
#     #[TODO]: change path in accrodance with MAC - as img was done in Windows
    
#     file_folder_name = 'training/images'
#     file_name = 'image_'+ trial_id +'.png'
#     #[TODO]: folders should not be written manually
#     img_path = os.path.join(stimuli_path, file_folder_name, file_name)
#     img = mpimg.imread(img_path)

#     height, width = img.shape[:2]
#     dpi = 100 
#     figsize = (width / dpi, height / dpi)
#     fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
#     ax.imshow(img)

#     # Plot fixations
#     sizes = fixations.get('duration', 50)
#     if hasattr(sizes, 'fillna'):
#         sizes = sizes.fillna(50)
#         sizes = sizes * 1000 if sizes.max() < 10 else sizes  # scale if in seconds
    
#     # Duration of fixation is used as dimeter of the scatter circle
#     scatter = ax.scatter(
#         fixations['avrxpos'],
#         fixations['avrypos'],
#         s = sizes,  #[TODO]: ensures that if no duration then it will be 50 - I need to check empty data BEFORE drawing traces
#         c = fixations.get('stime', 'blue'),
#         cmap = 'viridis',
#         alpha = 0.6,
#         edgecolors = 'white'
#     )

#     ax.set_title('Fixations on Trial Image')
#     ax.axis('off')

#     # Optional colorbar if timestamp is available
#     if 'stime' in fixations:
#         fig.colorbar(scatter, ax=ax, label='Timestamp (ms)')
    

#     # Plot traces
#     if timestamps is not None and not timestamps.empty:
#         # Sort by time just in case
#         timestamps_sorted = timestamps.sort_values(by='time')

#         ax.plot(
#             timestamps_sorted['x'],
#             timestamps_sorted['y'],
#             color = 'grey',
#             linewidth = 1,
#             alpha = 0.5,
#             zorder = 1 #behind scatter
#         )


#     # Plot Target area if exist
#     try:
#         target_coords = ast.literal_eval(target_area.iloc[0]['target_coordinates'])
#     except: 
#         target_coords = None
#     if target_area.iloc[0]['target_presence'] and target_coords:
#         print(2)
#         radius = 100
#         circle = patches.Circle(target_coords, radius, edgecolor='red', facecolor='none', linewidth=1, alpha=0.5)
#         ax.add_patch(circle)
    
#     fig.savefig('traces_trial_' + trial_id + '.png')
#     return fig
    



def drawing_traces(read_path, output_path, stimuli_path, trial_id, timestamps=None, fixations=None, target_area=None):
    # file_folder_name = 'training/images'
    file_name = 'image_' + trial_id + '.png'
    img_path = os.path.join(read_path, file_name)

    # Load the original image with OpenCV (BGR format)
    img = cv2.imread(img_path)

    if img is None:
        raise FileNotFoundError(f"Image not found: {img_path}")

    overlay = img.copy()

    # Plot trace lines
    if timestamps is not None and not timestamps.empty:
        timestamps_sorted = timestamps.sort_values(by='time')
        timestamps_sorted = timestamps_sorted.dropna(subset=['x', 'y'])
        points = list(zip(timestamps_sorted['x'].astype(int), timestamps_sorted['y'].astype(int)))

        for i in range(1, len(points)):
            cv2.line(overlay, points[i - 1], points[i], (150, 150, 150), 1)  # grey line

    # Plot fixations
    if fixations is not None and not fixations.empty:
        for _, row in fixations.iterrows():
            x, y = int(row['avrxpos']), int(row['avrypos'])
            duration = row.get('duration', 50)
            if duration < 10:  # likely in seconds, convert to ms
                duration *= 1000
            radius = int(max(5, min(50, duration * 0.05)))  # clip radius
            cv2.circle(overlay, (x, y), radius, (255, 0, 0), -1)  # red filled

    # Plot target area
    if target_area is not None and not target_area.empty:
        try:
            target_coords = ast.literal_eval(target_area.iloc[0]['target_coordinates'])
            if target_area.iloc[0]['target_presence']:
                target_x, target_y = map(int, target_coords)
                cv2.circle(overlay, (target_x, target_y), 100, (0, 0, 255), 2)  # red circle
        except Exception as e:
            print(f"Target area parsing failed: {e}")

    # Blend and save
    alpha = 0.6
    traced_img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
    filename = f'traces_trial_{trial_id}.png'
    write_path = os.path.join(output_path, filename)
    cv2.imwrite(write_path, traced_img)

    return traced_img



def video_tracer(fig, fixations): 
    print(11111)