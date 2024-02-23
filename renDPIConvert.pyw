from PIL import Image
import os
import struct
import zlib
import time
from plyer import notification
import PySimpleGUI as sg
import ctypes
from ctypes import windll, create_unicode_buffer


def edit_png_dpi(png_file, dpi):
    try:
        img = Image.open(png_file)
        img = img.convert("RGBA")
        dpi_x, dpi_y = dpi
        phys_chunk_data = struct.pack("!LLB", int(dpi_x/0.0254), int(dpi_y/0.0254), 1)

        # Convert to bytes
        phys_chunk_type = b'pHYs'
        phys_chunk_length = len(phys_chunk_data)

        phys_chunk_crc = struct.pack("!L", zlib.crc32(phys_chunk_type + phys_chunk_data) & 0xffffffff)

        # Create the modified PNG file
        with open(png_file, 'rb') as f:
            png_data = f.read()

        if b'pHYs' in png_data:
            # Find the position of the pHYs chunk
            pos = png_data.find(b'pHYs')
            png_data = png_data[:pos + 4] + phys_chunk_data + phys_chunk_crc + png_data[pos + 8 + 9:]
        else:
            idat_pos = png_data.find(b'IDAT') - 4
            png_data = png_data[:idat_pos] + phys_chunk_length.to_bytes(4, byteorder='big') + phys_chunk_type + phys_chunk_data + phys_chunk_crc + png_data[idat_pos:]

        with open(png_file, 'wb') as f:
            f.write(png_data)
        print("Successfully for:", png_file)
    except Exception as e:
        print("An error occurred:", str(e))

def make_gui():
    sg.theme('DarkGray2')

    layout = [
        [sg.Text('Select a folder:')],
        [sg.Input(key="path"), sg.FolderBrowse()],
        [sg.Text('DPI:'), sg.Input('300', key="dpi_x", size=(10, 1)), sg.Button('Change DPI', size=(16,1))],
        [sg.Output(size=(52, 10))]
    ]

    window = sg.Window("PNG DPI Changer", layout)

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Change DPI":
            path = values["path"]
            dpi_x = int(values["dpi_x"])
            dpi_y = dpi_x

            if os.path.isfile(path):
                edit_png_dpi(path, (dpi_x, dpi_y))
            if os.path.isdir(path):
                # パスのチェック ルートディレクトリは許可しない
                if os.path.abspath(path) == os.path.abspath(os.path.join(path, os.pardir)):
                    print(f"root is not allow path: {path}")
                    raise ValueError(f"root is not allow path: {path}")
                    sys.exit()
                # 開始時刻を記録
                start_time = time.time()
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(".png"):
                            edit_png_dpi(os.path.join(root, file), (dpi_x, dpi_y))

                end_time = time.time()
                processing_time = end_time - start_time
                if processing_time > 3:
                    notification.notify(title=py_name, message="Done.", timeout=5)
            else:
                print("Please select a valid folder.")

    window.close()

if __name__ == "__main__":
    py_name = os.path.basename(__file__)
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        pass
    make_gui()
