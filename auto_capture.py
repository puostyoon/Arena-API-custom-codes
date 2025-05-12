# -----------------------------------------------------------------------------
# Copyright (c) 2024, Lucid Vision Labs, Inc.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------

from arena_api.system import system
from arena_api.buffer import *
from utils import *

import ctypes
import numpy as np
import cv2
import time

'''
Live Stream: Introduction
    This example introduces the basics of running a live stream 
    from a single device. This includes creating a device, selecting
    up stream dimensions, getting buffer cpointer data, creating an
    array of the data and reshaping it to fit image dimensions using
    NumPy and displaying using OpenCV-Python.
'''
TAB1 = "  "
TAB2 = "    "

def sensor_setup(nodes, mode):
    """
    Setup stream dimensions and stream nodemap
        num_channels changes based on the PixelFormat
        Mono 8 would has 1 channel, RGB8 has 3 channels
    """
    stream_packet_size_max = nodes['DeviceStreamChannelPacketSize'].max
    nodes['DeviceStreamChannelPacketSize'].value = stream_packet_size_max
    nodes['num_channels'] = 3 # this node is originally not in the nodemap.
#mode='center_crop', 'binning', 'original'

    if mode=='crop':
        new_width = 400
        new_height = 400
        nodes['Width'].value = new_width 
        nodes['Height'].value = new_height 
        nodes['PixelFormat'].value = 'RGB8' #RGB8
    elif mode=='binning':
        nodes['PixelFormat'].value = 'RGB8' #RGB8
        pass 
    elif mode=='original':
        nodes['PixelFormat'].value = 'RGB8' #RGB8
    else:
        raise NotImplementedError(f'mode {mode} is not implemented.')


    return nodes

def streaming_setup(device):
    """
    Setup stream dimensions and stream nodemap
        num_channels changes based on the PixelFormat
        Mono 8 would has 1 channel, RGB8 has 3 channels

    """
    # Stream nodemap
    tl_stream_nodemap = device.tl_stream_nodemap

    tl_stream_nodemap["StreamBufferHandlingMode"].value = "NewestOnly"
    tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True
    tl_stream_nodemap['StreamPacketResendEnable'].value = True

def create_devices_with_tries():
    '''
    Waits for the user to connect a device
        before raising an exception if it fails
    '''
    tries = 0
    tries_max = 6
    sleep_time_secs = 10
    devices = None
    while tries < tries_max:
        devices = system.create_device()
        if not devices:
            print(
                f'{TAB1}Try {tries+1} of {tries_max}: waiting for {sleep_time_secs} '
                f'secs for a device to be connected!')
            for sec_count in range(sleep_time_secs):
                time.sleep(1)
                print(f'{TAB1}{sec_count + 1 } seconds passed ',
                    '.' * sec_count, end='\r')
            tries += 1
        else:
            return devices
    else:
        raise Exception(f'{TAB1}No device found! Please connect a device and run '
                        f'the example again.')

def stream_image():
    """
    demonstrates live stream
    (1) Start device stream
    (2) Get a buffer and create a copy
    (3) Requeue the buffer
    (4) Calculate bytes per pixel for reshaping
    (5) Create array from buffer cpointer data
    (6) Create a NumPy array with the image shape
    (7) Display the NumPy array using OpenCV
    (8) When Esc is pressed, stop stream and destroy OpenCV windows
    """

    devices = create_devices_with_tries()
    device = system.select_device(devices)
    nodemap = device.nodemap
    nodes = nodemap.get_node(['Width', 'Height', 'PixelFormat', 'DeviceStreamChannelPacketSize'])
    initial_nodes = copy_nodemap_values(nodes)

    # Setup
    streaming_setup(device)
    nodes = sensor_setup(nodes, mode='crop') # mode='crop', 'binning', 'original'. new key 'num_channels' will be added.
    
    set_maximum_exposure(device, fps=1.2)

    # Start streaming
    with device.start_stream(100):
        """
        Infinitely fetch and display buffer data until esc is pressed
        """
        for i in range(2000):
            # Used to display FPS on stream
            curr_frame_time = time.time()

            buffer = device.get_buffer()
            """
            Copy buffer and requeue to avoid running out of buffers
            """
            item = BufferFactory.copy(buffer)
            device.requeue_buffer(buffer)

            buffer_bytes_per_pixel = int(len(item.data)/(item.width * item.height))
            """
            Buffer data as cpointers can be accessed using buffer.pbytes
            """
            array = (ctypes.c_ubyte * nodes['num_channels'] * item.width * item.height).from_address(ctypes.addressof(item.pbytes))
            """
            Create a reshaped NumPy array to display using OpenCV
            """
            npndarray = np.ndarray(buffer=array, dtype=np.uint8, shape=(item.height, item.width, buffer_bytes_per_pixel))
            cv2.imwrite(os.path.join('captured_images', f'original_{time.strftime('%Y%m%d_%H%M%S')}.png'), npndarray)
            
            """
            Destroy the copied item to prevent memory leaks
            """
            BufferFactory.destroy(item)

            """
            Break if esc key is pressed
            """
            key = cv2.waitKey(1)
            if key == 27:
                break
        return_original_node_values(nodes, initial_nodes)
        device.stop_stream()
        cv2.destroyAllWindows()
 
    system.destroy_device()
    
    print(f'{TAB1}Destroyed all created devices')

if __name__ == '__main__':
    print('\nWARNING:\nTHIS EXAMPLE MIGHT CHANGE THE DEVICE(S) SETTINGS!')
    print('\nStreaming started\n')
    stream_image()
    print('\nstreaming finished successfully')
