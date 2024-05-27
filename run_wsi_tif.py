import os
import logging
import subprocess
import time

from utils import update_server_data
from mescnn.definitions import ROOT_DIR
from mescnn.classification.gutils.config import OxfordModelNameCNN
from mescnn.detection.model.config import SegmentationModelName
from mescnn.detection.qupath.config import PathMESCnn, PathWSI, get_wsis

def mescnn_function(socketio, room_id, process_data, filter):
    
   
    white_threshold = "205"
    px_threshold = "1000"

    # Find files in the folder "current-file"
    files = os.listdir('./current-files/')
    path = './current-files/' + files[0]
    file_name = ".".join(files[0].split(".")[:-1])

    # Get the WSI and the type of the WSI
    get_wsi_path = get_wsis(path)
    wsis = get_wsi_path[0]
    file_type = get_wsi_path[1]

    # Tests
    test_tile = True
    test_segment = True
    test_qu2json = True
    test_json2exp = True
    test_classify = True

    #! Initialisation
    start_time = time.time()

    wsi_tiff_dir = PathWSI.MESCnn_WSI
    detection_model = SegmentationModelName.CASCADE_R_50_FPN_1x
    path_to_export = PathWSI.MESCnn_EXPORT
    qupath_segm_dir = os.path.join(path_to_export, 'QuPathProject')

    #! Loading effectué
    socketio.emit('message', {"text": 'Loading complete!', "step": -1}, room=room_id)
    socketio.emit('message', {"text": 'Processing image...', "step": -1}, room=room_id)
    socketio.sleep(1)

    if test_tile:
        if wsis[0] is False:
            logging.info("No WSIs found for testing!")
            return
        elif file_type == "wsi":
            for wsi in wsis:
                logging.info(f"{PathMESCnn.TILE} running on {wsi}...")
                subprocess.run(["python", PathMESCnn.TILE,
                                "--wsi", wsi,
                                "--export", path_to_export])
        else:
            test_segment = False
            test_qu2json = False
            test_json2exp = False
                

    #! Fin du tiling
    if file_type == "wsi":
        # Check that tiles exist
        if not os.path.exists(os.path.join(path_to_export, 'Temp/tiler-output/Tiles/' + file_name)):
            socketio.emit('message', {"text": 'Error while creating tiles!', "step": -2}, room=room_id)
            socketio.sleep(5)
            socketio.emit('message', {"text": '/errored', "step": 4}, room=room_id)
            return
        else :
            #! Tiling effectué
            socketio.emit('message', {"text": 'Tiling complete!', "step": 0}, room=room_id)
            socketio.sleep(0.2)


    if test_segment:
        for wsi in wsis:
            socketio.emit('message', {"text": 'Segmentation masks in progress...', "step": -1}, room=room_id)
            logging.info(f"{PathMESCnn.SEGMENT} running on {wsi}...")
            subprocess.run(["python", PathMESCnn.SEGMENT,
                            "--wsi", wsi,
                            "--export", path_to_export,
                            "--qupath", qupath_segm_dir,
                            "--model", detection_model,
                            "--threshold", white_threshold,
                            "--px-threshold", px_threshold,])
    else:
        logging.info(f"Skipping run of {PathMESCnn.SEGMENT}!")


    #! Fin segmentation
    if file_type == "wsi":
        # Check that masks exist
        if not os.path.exists(os.path.join(path_to_export, 'Temp/segment-output/Masks/' + file_name)):
            socketio.emit('message', {"text": 'Error while creating masks!', "step": -2}, room=room_id)
            socketio.sleep(5)
            socketio.emit('message', {"text": '/errored', "step": 4}, room=room_id)
            return
        else:
            #! Masques de segmentation effectués
            socketio.emit('message', {"text": 'Masks generated!', "step": 1}, room=room_id)
            socketio.sleep(0.2)


    if test_qu2json:
        socketio.emit('message', {"text": 'Annotation conversion in progress...', "step": -1}, room=room_id)
        logging.info(f"Running {PathMESCnn.QU2JSON}")
        subprocess.run(["python", PathMESCnn.QU2JSON,
                        "--export", path_to_export,
                        "--wsi-dir", wsi_tiff_dir,
                        "--qupath", qupath_segm_dir])
    else:
        logging.info(f"Skipping run of {PathMESCnn.QU2JSON}")


    #! Fin conversion
    if file_type == "wsi":
        if not os.path.exists(os.path.join(path_to_export, 'Temp/qu2json-output/rois.csv')):
            socketio.emit('message', {"text": 'Error while creating JSON!', "step": -2}, room=room_id)
            socketio.sleep(5)
            socketio.emit('message', {"text": '/errored', "step": 4}, room=room_id)
            return
        else:
            #! Conversion QuPath -> JSON effectuée
            socketio.emit('message', {"text": 'Masks converted to JSON!', "step": -1}, room=room_id)
            socketio.sleep(0.2)


    if test_json2exp:
        socketio.emit('message', {"text": 'Annotation export in progress...', "step": -1}, room=room_id)
        logging.info(f"Running {PathMESCnn.JSON2EXP}")
        subprocess.run(["python", PathMESCnn.JSON2EXP,
                        "--export", path_to_export,
                        "--wsi-dir", wsi_tiff_dir])
    else:
        logging.info(f"Skipping run of {PathMESCnn.JSON2EXP}")


    #! Fin exportation
    if file_type == "wsi":
        if not os.path.exists(os.path.join(path_to_export, 'Temp/json2exp-output/Crop/' + file_name)):
            socketio.emit('message', {"text": 'Error while exporting JSON!', "step": -2}, room=room_id)
            socketio.sleep(5)
            socketio.emit('message', {"text": '/errored', "step": 4}, room=room_id)
            return
        else:
            #! Exportation des glomérules effectuée
            socketio.emit('message', {"text": 'Crops generated!', "step": 2}, room=room_id)
            socketio.sleep(0.2)


    if test_classify:
       
        net_M = OxfordModelNameCNN.EfficientNet_V2_M
        net_E = OxfordModelNameCNN.EfficientNet_V2_M
        net_S = OxfordModelNameCNN.DenseNet161
        net_C = OxfordModelNameCNN.MobileNet_V2
        
        filterM = filter.M_filter
        filterE = filter.E_filter
        filterS = filter.S_filter
        filterC = filter.C_filter
        
        use_vit = False
        
        if file_type == "img":
            img = True
        else:
            img = False

        use_vit_M = use_vit_E = use_vit_S = use_vit_C = use_vit
        if file_type == "wsi":
            socketio.emit('message', {"text": 'Calculating Oxford score...', "step": -1}, room=room_id)
        else:
            socketio.emit('message', {"text": 'Classifying image...', "step": -1}, room=room_id)
        socketio.sleep(0.2)
        logging.info(f"Running {PathMESCnn.CLASSIFY} with {net_M}, {net_E}, {net_S}, {net_C}")
        subprocess.run(["python", PathMESCnn.CLASSIFY,
                        "--root-path", ROOT_DIR,
                        "--export-dir", path_to_export,
                        "--netM", net_M, "--vitM", str(use_vit_M),
                        "--netE", net_E, "--vitE", str(use_vit_E),
                        "--netS", net_S, "--vitS", str(use_vit_S),
                        "--netC", net_C, "--vitC", str(use_vit_C),
                        "--path_wsi", wsis[0],
                        "--img", str(img),
                        "--filterM",str(filterM), "--filterE",str(filterE), 
                        "--filterS",str(filterS), "--filterC",str(filterC)]),

    else:
        logging.info(f"Skipping run of {PathMESCnn.CLASSIFY}")


    try:
        end_time = time.time()
        processing_time = end_time - start_time

        process_data.file_name = files[0]
        process_data.time = processing_time
        process_data.type = file_type

        update_server_data(process_data, process_data.file_name, process_data.type)

        #! Fin
        if file_type == "wsi":
            socketio.emit('message', {"text": 'Score determined!', "step": 3}, room=room_id)
        else:
            socketio.emit('message', {"text": 'Image classified!', "step": 3}, room=room_id)
        socketio.sleep(2)
        socketio.emit('message', {"text": '/results', "step": 4}, room=room_id)

    except:
        #! Erreur
        socketio.emit('message', {"text": 'Error while calculating Oxford score!', "step": -2}, room=room_id)
        socketio.sleep(5)
        socketio.emit('message', {"text": '/errored', "step": 4}, room=room_id)
        return