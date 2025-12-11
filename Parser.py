import re
import numpy as np
import pandas as pd

def parse_samples(samples_path):
    """
    Reads a text file containing structured data, parses it into a dictionary,
    and returns the data as a pandas DataFrame.

    Parameters:
        filepath (str): Path to the input file.

    Returns:
        pd.DataFrame: A DataFrame constructed from the parsed file contents.
    """

    samples = {
    'time': [],
    'x': [],
    'y': [],
    'pupil': []
    }

    with open(samples_path, 'r') as file: 
    # lines = file.readlines()
        for line in file:
            if line and line[0].isdigit():
                
                parts = [p.strip() for p in line.strip().split('\t')]

                # Extract the first four values and convert to numbers
                time = int(parts[0])
                try:
                    x = float(parts[1])
                except:
                    x = np.nan
                try:
                    y = float(parts[2])
                except:
                    y = np.nan
                pupil = float(parts[3])
                
                samples['time'].append(time) #[TODO]: int or float?
                samples['x'].append(x)
                samples['y'].append(y)
                samples['pupil'].append(pupil)
    
    df = pd.DataFrame(samples)
    return df



def parse_events(events_path, metadata_lines=10):
    metadata = {}
    reading_metadata = True  # Flag to indicate we are still reading metadata
    metadata_count = 0

    events_dict = {}

    with open(events_path, 'r') as file:
        for line in file:
            if reading_metadata:
                # Process metadata lines
                if line.startswith("**"):
                    line_clean = line[2:].strip()
                    if ":" in line_clean:
                        key, value = map(str.strip, line_clean.split(":", 1))
                    else:
                        try:
                            parts = line_clean.split(maxsplit=1)
                            key = parts[0]
                            value = parts[1] if len(parts) > 1 else ""
                        except:
                            pass
                    metadata[key] = value
                    metadata_count += 1
                    if metadata_count >= metadata_lines:
                        # Stop reading metadata after the specified lines
                        reading_metadata = False
                else:
                    # If not metadata, just skip the line
                    continue
            else:
                if line.startswith("MSG") and "TRIALID" in line:
                    trial_id_match = re.search(r'TRIALID\s+(\S+)', line)
                    if trial_id_match:
                        current_trial = trial_id_match.group(1)
                        events_dict[current_trial] = {
                            'image_path': None,
                            'start': None,
                            'end': None,
                            'fixations': {
                                'eye': [],
                                'stime': [],
                                'etime': [],
                                'duration': [],
                                'avrxpos': [],
                                'avrypos': [],
                                'avrpupilsize': []
                            },
                            'saccades': {
                                'eye': [],
                                'stime': [],
                                'etime': [],
                                'duration': [],
                                'sxpos': [],
                                'sypos': [],
                                'expos': [],
                                'eypos': [],
                                'ampl': [],
                                'peakvel': []
                            },
                            'blinks': {
                                'eye': [],
                                'stime': [],
                                'etime': [],
                                'duration': [],
                            } 

                        }
                elif line.startswith("MSG") and 'TRIAL_IMAGE' in line:
                    match = re.search(r'TRIAL_IMAGE\s+(.+)', line)
                    if match:
                        image_path = match.group(1)
                        events_dict[current_trial]['image_path'] = image_path

                elif line.startswith("START"):
                    parts = line.split()
                    events_dict[current_trial]["start"] = int(parts[1]) if len(parts)>=2 else None
                
                elif line.startswith("END"): #[TODO]: res - resolution - what is that
                    parts = line.split()
                    events_dict[current_trial]["end"] = int(parts[1]) if len(parts)>=2 else None
    
                elif line.startswith("EFIX"): #[TODO]: try exept

                    """
                    EFIX <eye> <stime> <etime> <dur> <axp> <ayp> <aps>
                    eye: L for left, R for Right
                    stime: start time of fixation
                    etime: end time of fixation
                    dur: duration of fixation
                    axp: average x position during fixation
                    ayp: average y position during fixation
                    aps: average pupil size
                    """
                    parts = line.split()
                    events_dict[current_trial]['fixations']['eye'].append(parts[1])
                    events_dict[current_trial]['fixations']['stime'].append(int(parts[2]))
                    events_dict[current_trial]['fixations']['etime'].append(int(parts[3]))
                    events_dict[current_trial]['fixations']['duration'].append(int(parts[4]))
                    events_dict[current_trial]['fixations']['avrxpos'].append(float(parts[5]))
                    events_dict[current_trial]['fixations']['avrypos'].append(float(parts[6]))
                    events_dict[current_trial]['fixations']['avrpupilsize'].append(float(parts[7])) #[TODO]: float or int


                elif line.startswith("ESACC"): #[TODO]: try exept

                    """
                    ESACC <eye> <stime> <etime> <dur> <sxp> <syp> <exp> <eyp> <ampl> <pv>
                    eye: L for left, R for Right
                    stime: start time of fixation
                    etime: end time of fixation
                    dur: duration of fixation
                    sxp: start x position of the saccade
                    syp: start y position of the saccade
                    exp: end x position of the saccade
                    eyp: end y position of the saccade
                    ampl: total visual angle covered  which can be divided by
                    (<dur>/1000) to obtain the average velocity.
                    pv: peak velocity
                    """
                    parts = line.split()
                    events_dict[current_trial]['saccades']['eye'].append(parts[1])
                    events_dict[current_trial]['saccades']['stime'].append(parts[2])
                    events_dict[current_trial]['saccades']['etime'].append(parts[3])
                    events_dict[current_trial]['saccades']['duration'].append(parts[4])
                    events_dict[current_trial]['saccades']['sxpos'].append(parts[5])
                    events_dict[current_trial]['saccades']['sypos'].append(parts[6])
                    events_dict[current_trial]['saccades']['expos'].append(parts[7])
                    events_dict[current_trial]['saccades']['eypos'].append(parts[8])
                    events_dict[current_trial]['saccades']['ampl'].append(parts[9])
                    events_dict[current_trial]['saccades']['peakvel'].append(parts[10])


                elif line.startswith("EBLINK"): #[TODO]: try exept

                    """
                    ESACC <eye> <stime> <etime> <dur> 
                    eye: L for left, R for Right
                    stime: start time of blink
                    etime: end time of blink
                    dur: duration of blink
                    """
                    parts = line.split()
                    events_dict[current_trial]['blinks']['eye'].append(parts[1])
                    events_dict[current_trial]['blinks']['stime'].append(parts[2])
                    events_dict[current_trial]['blinks']['etime'].append(parts[3])
                    events_dict[current_trial]['blinks']['duration'].append(parts[4])
    return metadata, events_dict


def convert_dict_to_df(events_dict):
    trial_rows = []
    fixation_rows = []
    saccade_rows = []
    blink_rows = []

    for key_trial, data in events_dict.items():
        image_path = data['image_path']
        start = data['start']
        end = data['end']

        # Trials dataframe rows
        trial_rows.append({
        'trial_id': key_trial,
        'path_name_trial': image_path,
        'start_trial': start,
        'end_trial': end,
        'num_fix': len(data['fixations']['eye']),
        'num_sacc': len(data['saccades']['eye']),
        'num_blinks': len(data['blinks']['eye'])
        })

        # Fixation dataFrame rows
        for i in range(len(data['fixations']['eye'])): #[TODO]: well, probably 'eye' is always the longest but may be not
            fixation_rows.append({
            'trial_id': key_trial,
            'path_name_trial': image_path,
            'eye': data['fixations']['eye'][i],
            'stime': data['fixations']['stime'][i],
            'etime': data['fixations']['etime'][i],
            'duration': data['fixations']['duration'][i],
            'avrxpos': data['fixations']['avrxpos'][i],
            'avrypos': data['fixations']['avrypos'][i],
            'avrpupilsize': data['fixations']['avrpupilsize'][i],
            })


        # Saccade dataFrame rows
        for i in range(len(data['saccades']['eye'])):
            saccade_rows.append({
                'trial_id': key_trial,
                'path_name_trial': image_path,
                'eye': data['saccades']['eye'][i],
                'stime': data['saccades']['stime'][i],
                'etime': data['saccades']['etime'][i],
                'duration': data['saccades']['duration'][i],
                'sxpos': data['saccades']['sxpos'][i],
                'sypos': data['saccades']['sypos'][i],
                'expos': data['saccades']['expos'][i],
                'eypos': data['saccades']['eypos'][i],
                'ampl': data['saccades']['ampl'][i],
                'peakvel': data['saccades']['peakvel'][i],
            })

        # Blink dataFrame rows
        for i in range(len(data['blinks']['eye'])):
            blink_rows.append({
                'trial_id': key_trial,
                'path_name_trial': image_path,
                'eye': data['blinks']['eye'][i],
                'stime': data['blinks']['stime'][i],
                'etime': data['blinks']['etime'][i],
                'duration': data['blinks']['duration'][i],
            })

    df_trial = pd.DataFrame(trial_rows)
    df_fixations = pd.DataFrame(fixation_rows)
    df_saccades = pd.DataFrame(saccade_rows)
    df_blinks = pd.DataFrame(blink_rows)

    return df_trial, df_fixations, df_saccades, df_blinks