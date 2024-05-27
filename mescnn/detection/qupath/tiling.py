import os
import cv2
import time
import shutil
import threading
from mescnn.detection.qupath.utils import tile_region, is_foreground, is_black


def dir_name_from_wsi(path):
    collate = 2 if ('.ome.tif' in path or '.ome.tiff' in path) else 1
    return '.'.join(path.split('.')[:-collate])


class BaseTiler(object):
    def __init__(self, reader, out_dir, tile_ext='jpeg'):
        self.reader = reader
        out_dir = os.path.join(out_dir, dir_name_from_wsi(reader.name))
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)
        os.makedirs(out_dir, exist_ok=True)
        self.out_dir = out_dir
        self.tile_ext = tile_ext

    def tile_image(self, desired_op, tile_size, tile_stride):
        pass

class WholeTilerOpenslide(BaseTiler):
    def __init__(self, reader, out_dir, tile_ext='jpeg'):
        super().__init__(reader, out_dir, tile_ext=tile_ext)

    def tile_image(self, desired_op, tile_size, tile_stride, check_fg=True):
        roi = (0, 0, *self.reader.dimensions)
        tile_coords = tile_region(roi, tile_size, tile_stride)

        def process_tile(tile_coord):
            x, y, h, w = tile_coord
            tile_image = self.reader.read_resolution(x, y, h, w, desired_op, do_rescale=True, read_bgr=True)
            tile_name = f"{self.reader.name}__OP_{desired_op}__ROI_{x}_{y}_{h}_{w}.{self.tile_ext}"
            if not is_black(tile_image):
                if not check_fg or is_foreground(tile_image):
                    tile_path = os.path.join(self.out_dir, tile_name)
                    print(f"Writing to {tile_path}")
                    cv2.imwrite(tile_path, tile_image)

        start = time.time()

        # for coord in tile_coords:
        #     process_tile(coord)

        threads = [threading.Thread(target=process_tile, args=(coord,)) for coord in tile_coords]

        print(f"Starting {len(threads)} threads...")

        # Check the amount of threads on the CPU
        cpu_threads = os.cpu_count()

        # Set max threads to the number of threads on the CPU minus 2
        max_threads = cpu_threads - 2 if cpu_threads > 2 else 1

        for i in range(0, len(threads), max_threads):
            threads_batch = threads[i:i+max_threads]
            for thread in threads_batch:
                thread.start()
            for thread in threads_batch:
                thread.join()
            print(f"Batch {i//max_threads+1} done!")

        print(f"Time taken: {time.time() - start:.2f}s")


class WholeTilerBioformats(BaseTiler):
    def __init__(self, reader, out_dir, tile_ext='jpeg'):
        super().__init__(reader, out_dir, tile_ext=tile_ext)

    def tile_image(self, desired_op, tile_size, tile_stride, check_fg=True):
        for i, dimensions in enumerate(self.reader.dimensions):
            s = self.reader.indexes[i]
            roi = (0, 0, *dimensions)
            tile_coords = tile_region(roi, tile_size, tile_stride)
            for tile_coord in tile_coords:
                x, y, h, w = tile_coord
                tile_image = self.reader.read_resolution(s, x, y, h, w, desired_op, do_rescale=True, read_bgr=True)
                tile_name = f"{self.reader.name}_{s}__OP_{desired_op}__ROI_{x}_{y}_{h}_{w}.{self.tile_ext}"
                if tile_image is not None:
                    if not is_black(tile_image):
                        if not check_fg or is_foreground(tile_image):
                            tile_path = os.path.join(self.out_dir, tile_name)
                            print(f"Writing to {tile_path}")
                            cv2.imwrite(tile_path, tile_image)
