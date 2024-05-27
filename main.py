import os
import random
import json 

from utils import *


from flask import Flask, render_template, request, send_file
from flask_socketio import SocketIO, join_room, leave_room

from werkzeug.utils import secure_filename
from run_wsi_tif import mescnn_function

app = Flask(__name__)
socketio = SocketIO(app, debug=True, cors_allowed_origins='*')

# Set the static folder to the 'client' folder
app._static_folder = os.path.abspath("./static/")


report_dir = "./Data/Export/Report"
temp_dir = "./Data/Export/Temp/"
tiles_dir = temp_dir + 'tiler-output/Tiles/'
masks_dir = temp_dir + 'segment-output/Masks/'
crops_dir = temp_dir + 'json2exp-output/Crop-256/'
full_crops_dir = temp_dir + 'json2exp-output/Original/'

class FilterData:
    def __init__(self):
        self.M_filter = False
        self.E_filter = False
        self.S_filter = False
        self.C_filter = False

    def update_from_json(self, json_data):
        self.M_filter = json_data.get("M_filter", False)
        self.E_filter = json_data.get("E_filter", False)
        self.S_filter = json_data.get("S_filter", False)
        self.C_filter = json_data.get("C_filter", False)

filter_data = FilterData()

class ProcessInfo:
    in_progress = False
    file_name = None
    time = None
    crop_amount = None
    classification_csv = []
    selected_crops = []
    histogram = {}
    score = {}
    prob = {}
    type = None
    GGS_count = None
    GGS_filename = []

process_data = ProcessInfo()


@app.route('/')
def home():
    return render_template('index.html', history=get_history(), errored=False)


@app.route('/errored')
def errored():
    return render_template('index.html', errored=True)


currently_analyzing = False
@socketio.on('process_img')
def process_img():
    global currently_analyzing
    if currently_analyzing:
        socketio.emit('message', {"text": 'Already processing an image...', "step": -1}, room=request.sid)
        return
    
    currently_analyzing = True
    mescnn_function(socketio, request.sid, process_data, filter_data)
    currently_analyzing = False

@app.route('/results')
def results():
    if (process_data.file_name != None):
        select_crops(process_data)
        return render_template('results.html',
            score=process_data.score,
            file_name=process_data.file_name, 
            processing_time=process_data.time,
            crop_amount=process_data.crop_amount,
            selected_crops=process_data.selected_crops,
            is_empty=False,
            prob = process_data.prob,
            type=process_data.type,
            history=get_history(),
            GGS_count=process_data.GGS_count,
            GGS_filename=process_data.GGS_filename
        )
    else:
        return render_template('results.html', is_empty=True, history=get_history())
    
@app.route('/results/<crop_index>')
def show_crop_detail(crop_index=0):
    crop_index = int(crop_index)
    if (process_data.file_name != None):
        prob, score = get_img_prob_score(temp_dir, process_data.file_name, crop_index)
        crop_name = crop_file_name(crop_index)
        return render_template('results.html',
            prob = prob,
            score=score,
            file_name=crop_name,
            glomerulus_index=crop_index,
            is_glomerulus=True,
            is_empty=False,
            type="img",
            history=get_history(),
        )
    else:
        return render_template('results.html', is_empty=True, history=get_history())
 
@app.route('/results/GGS/<ggs_index>')
def show_ggs_crop(ggs_index=0):
    ggs_index = int(ggs_index)
    if (process_data.file_name != None):
        ggs_crop_name = process_data.GGS_filename[ggs_index % process_data.GGS_count] # makes sure the index is within the bounds
        return render_template('results.html',
            file_name=ggs_crop_name.split('/')[-1],
            glomerulus_index=ggs_index,
            is_glomerulus=True,
            is_empty=False,
            ggs_filename=process_data.GGS_filename,
            ggs_count=process_data.GGS_count,
            type="ggs",
            history=get_history(),
        )
    else:
        return render_template('results.html', is_empty=True, history=get_history())
 
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hist')
def hist():
    return {'hist': process_data.histogram}


files_path = "./current-files/"
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    # Extract filter data
    filter_data_json = request.form.get('filter')
    if filter_data_json:
        try:
            filter_data_json = json.loads(filter_data_json)
            filter_data.update_from_json(filter_data_json)
        except json.JSONDecodeError:
            return 'Invalid JSON data', 400
   
        
    # If there is a process in progress, return an error
    if process_data.in_progress:
        return 'There is already a process in progress', 400
    
    if file:
        # Check if there is already a file in the folder
        files = os.listdir(files_path)

        # Remove the file(s) in the folder
        for f in files:
            # if (".zip" not in f):
            os.remove(files_path + f)
        

        # Remove the folder "./Data/Export/Temp" and all its contents
        os.system("rm -r ./Data/Export/Temp")
        os.system("rm -r ./Data/Export/QuPathProject")
        os.makedirs('./Data/Export/Temp')

        filename = secure_filename(file.filename)
        file.save(os.path.join(files_path, filename))

        return 'Started analyzing the image', 200
    return 'Error while saving the file', 400


@app.route('/waiting', methods=['GET'])
def waiting():
    return render_template('waiting.html')


@app.route('/tiles')
def send_tiles():
    wsi_path = os.listdir(tiles_dir)[0] + '/'
    tiles = os.listdir(tiles_dir + wsi_path)

    random.shuffle(tiles)
    tiles = tiles[:10]
    
    for i in range(len(tiles)):
        tiles[i] = "/get_tile/" + tiles[i]
    return {'result': tiles}


@app.route('/get_tile/<tile>')
def get_tile(tile):
    wsi_path = os.listdir(tiles_dir)[0] + '/'
    return send_file(tiles_dir + wsi_path + tile)


@app.route('/masks')
def send_masks():
    wsi_path = os.listdir(masks_dir)[0] + '/'
    masks = os.listdir(masks_dir + wsi_path)

    random.shuffle(masks)
    masks = masks[:10]
    
    for i in range(len(masks)):
        masks[i] = "/get_mask/" + masks[i]
    return {'result': masks}


@app.route('/get_mask/<mask>')
def get_mask(mask):
    wsi_path = os.listdir(masks_dir)[0] + '/'
    return send_file(masks_dir + wsi_path + mask)


@app.route('/crops')
def send_crops():
    wsi_path = os.listdir(crops_dir)[0] + '/'
    crops = os.listdir(crops_dir + wsi_path)

    random.shuffle(crops)
    crops = crops[:10]
    
    for i in range(len(crops)):
        crops[i] = "/get_crop/" + crops[i]
    return {'result': crops}

@app.route('/get_ggs/<ggs_index>')
def get_ggs(ggs_index):
    ggs_index = int(ggs_index)
    return send_file(process_data.GGS_filename[ggs_index % process_data.GGS_count].replace('/home/ubuntu/M1', '.'))
    
@app.route('/get_crop')
def get_img():
    img_path = os.listdir(files_path)[0]
    return send_file(files_path + img_path)


@app.route('/get_crop/<crop>')
def get_crop(crop):
    wsi_path = os.listdir(crops_dir)[0] + '/'
    return send_file(crops_dir + wsi_path + crop)


@app.route('/get_full_crop/<crop>')
def get_full_crop(crop):
    wsi_path = os.listdir(full_crops_dir)[0] + '/'
    return send_file(full_crops_dir + wsi_path + crop)



@app.route('/download/<dl_type>')
def download(dl_type):
    # Switch case of the download type
    if dl_type == 'report':
        wsi_path = os.listdir(temp_dir)
        # Remove the file with Oxford in it
        wsi_path = [w for w in wsi_path if '.csv' in w]
        wsi_path = wsi_path[0]
        return send_file(temp_dir + wsi_path)
    elif dl_type == 'crops':
        wsi_path = os.listdir(crops_dir)[0] + '/'
        os.system(f"zip -r {temp_dir}crops.zip {crops_dir + wsi_path}")
        return send_file(temp_dir + 'crops.zip')
    

if __name__ == '__main__':
    socketio.run(app)