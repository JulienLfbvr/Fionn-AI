import pandas as pd
import os
import ast

def detect_crop(row):
    if row['M-bin']:
        return 'M'
    elif row['E-bin']:
        return 'E'
    elif row['S-bin']:
        return 'S'
    else:
        return 'C'
    
def get_history():
    base_path = "./Data/Export/"
    try:
        df = pd.read_csv(base_path + 'Report/Oxford.csv', sep=';')
        history = []
        
        for _, row in df.iterrows():
            name = row.iloc[0]  # First column
            score = ''.join(map(str, row[1:5]))  # Concatenate values from second to fourth column
            history.append({'name': name, 'score': score, 'date': row.iloc[9], 'filesize': int(row.iloc[10]/1_000_000)})
            
        history.reverse()
        return history
    
    except FileNotFoundError:
        return False

def select_crops(process_data):
    csv = process_data.classification_csv
    # Convert M-bin, E-bin, S-bin and C-bin to integers
    csv['M-bin'] = csv['M-bin'].astype('int'); csv['E-bin'] = csv['E-bin'].astype('int');
    csv['S-bin'] = csv['S-bin'].astype('int'); csv['C-bin'] = csv['C-bin'].astype('int');
    
    # Keep only crops that have any of their M-bin, E-bin, S-bin or C-bin = 1
    selected_crops = csv[(csv['M-bin'] == 1) | (csv['E-bin'] == 1) | (csv['S-bin'] == 1) | (csv['C-bin'] == 1)]

    # Shuffle the dataframe
    selected_crops = selected_crops.sample(frac=1)
    selected_crops = selected_crops.head(6)

    # Only keep the filename and what bins are 1
    selected_crops = selected_crops[['filename', 'M-bin', 'E-bin', 'S-bin', 'C-bin']]

    # Only keep the final part of the filename
    selected_crops['filename'] = selected_crops['filename'].map(lambda x: x.split('/')[-1])

    # If the file has M-bin, set it's column "detected" to "M" etc
    selected_crops['detected'] = selected_crops.apply(detect_crop, axis=1)

    # Only keep the filename and detected columns
    selected_crops = selected_crops[['filename', 'detected']]
    
    # Convert the dataframe to a list of dictionaries
    selected_crops = selected_crops.to_dict(orient='records')
    process_data.selected_crops = selected_crops


def crop_file_name(file_index):
    file_index = int(file_index)
    path = "./Data/Export/Temp/"

    wsi_csv = os.listdir(path)
    wsi_csv = [w for w in wsi_csv if '.csv' in w]
    wsi_csv = wsi_csv[0]

    csv_content = pd.read_csv(path + wsi_csv, sep=';', header=None)
    df = csv_content.values.tolist()
    df = pd.DataFrame(df[1:], columns=df[0])

    file_index = file_index % len(df)

    file_name = df.iloc[file_index]['filename'].split('/')[-1]

    return file_name


def get_img_prob_score(temp_dir, file_name, crop_index=None, base_path=""):
    name_img = file_name.split('.')[0]
    df = pd.read_csv(base_path + temp_dir + name_img + '.csv', sep=';')
    
    if (crop_index != None):
        # Only keep the row that is at index (as an int) of the file_name
        file_index = int(crop_index) % len(df)
        df = df.iloc[file_index]
        df = df.to_frame().T
        
    dfp = df.copy()
    dfp = dfp[[c for c in dfp.columns if '-prob' in c]]
    dfp.columns = [c[0] for c in dfp.columns]
    prob = dfp.to_dict(orient='records')[0]
    
    #Only keep columns with "-bin" in it
    df = df[[c for c in df.columns if '-bin' in c]]
    # Only keep the first character of the column name
    df.columns = [c[0] for c in df.columns]
    # Transform to dictionary
    score = df.to_dict(orient='records')[0]

    return [prob, score]


def update_server_data(process_data, file_name, data_type):
    base_path = "./Data/Export/"
    report_dir = "Report/"
    temp_dir = "Temp/"

    wsi_path = os.listdir(base_path + temp_dir)

    wsi_path = [w for w in wsi_path if '.csv' in w]
    wsi_path = wsi_path[0]

    #! Classification
    csv_content = pd.read_csv(base_path + temp_dir + wsi_path, sep=';', header=None)
    df = csv_content.values.tolist()
    df = pd.DataFrame(df[1:], columns=df[0])

    process_data.classification_csv = df.copy()

    if data_type == "img" :
        prob, score = get_img_prob_score(temp_dir, file_name, None, base_path)
        process_data.prob = prob
        process_data.score = score
        # Calculate Oxford score
        oxford_score = sum(process_data.score.values())
        process_data.score["Oxford"] = oxford_score

    else :
        #! Process WSI results
        # Calculate the histogram using the columns of the dataframe
        histogram = df.iloc[:, 5:9].astype('float').sum().to_dict()

        # Only keep the first character of the column name (M-bin -> M)
        histogram = {k[0]: v for k, v in histogram.items()}
        histogram['total'] = len(df)

        process_data.crop_amount = len(df)

        df = pd.read_csv(base_path + report_dir + '/Oxford.csv', sep=';')
        # Only keep the values if the WSI-ID is contained in the filename
        df = df[df['WSI-ID'].str.contains(file_name.split('.')[0])]
        # Only keep the last row
        df = df.tail(1)
        
        # Get the GGS count and filenames
        ggs_filename = df['GGS-filename'].tolist()
        ggs_filename = ast.literal_eval(ggs_filename[0])
        process_data.GGS_filename = ggs_filename
        process_data.GGS_count = df['GGS-count'].values[0]
        process_data.crop_amount += process_data.GGS_count
        
        # Only keep columns with "-score" in it
        df = df[[c for c in df.columns if '-score' in c]]

        # Only keep the second character of each value
        df = df.map(lambda x: int(x[1]))

        # Only keep the first character of the column name
        df.columns = [c[0] for c in df.columns]

        # Transform to dictionary
        oxford = df.to_dict(orient='records')[0]

        process_data.histogram = histogram
        process_data.score = oxford
        # Calculate Oxford score
        oxford_score = sum(process_data.score.values())
        process_data.score["Oxford"] = oxford_score
        