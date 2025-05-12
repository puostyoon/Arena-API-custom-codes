import time 
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt 

def copy_nodemap_values(nodes):
    copied_nodes = dict()
    for key, val in nodes.items():
        copied_nodes[key]=val 
    return copied_nodes

def return_original_node_values(nodes, initial_nodes):
    for key, val in initial_nodes.items():
        nodes[key]=val 

def show_split_color_image(npndarray, savedir, fps=None):
    # R, G, B 채널 분리
    r, g, b = cv2.split(npndarray)  # shape: (H, W) 각각

    # 채널 문자 삽입
    cv2.putText(r, 'R', (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(g, 'G', (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(b, 'B', (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3, cv2.LINE_AA)

    # 원래 영상에도 FPS 텍스트 추가
    cv2.putText(npndarray, fps, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

    # 창으로 띄우기
    cv2.imshow('Original (BGR)', cv2.cvtColor(npndarray, cv2.COLOR_BGR2RGB))
    # cv2.imshow('Red Channel', r)
    # cv2.imshow('Green Channel', g)
    # cv2.imshow('Blue Channel', b)
    cv2.imshow('r g b', cv2.resize(np.concatenate([r,g,b], axis=1), dsize=(1500, 500)))

    # ----- 3. 키 입력 감지 -----
    key = cv2.waitKey(1) & 0xFF  # 1ms 대기 (있어야 프레임이 계속 넘어감)
    if key == ord('s'):
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        cv2.imwrite(os.path.join(savedir, f'original_{timestamp}.png'), cv2.cvtColor(npndarray, cv2.COLOR_BGR2RGB))
        cv2.imwrite(os.path.join(savedir, f'red_{timestamp}.png'), r)
        cv2.imwrite(os.path.join(savedir, f'green_{timestamp}.png'), g)
        cv2.imwrite(os.path.join(savedir, f'blue_{timestamp}.png'), b)
        cv2.imwrite(os.path.join(savedir, f'rgb_separate_{timestamp}.png'), np.concatenate([r,g,b], axis=1))
        print(f"✅ Saved images at {timestamp}")
    elif key == 27: # ESC key
        return
    
def set_maximum_exposure(device, fps):
    
    nodemap = device.nodemap
    nodes = nodemap.get_node(['ExposureAuto', 'ExposureTime',
                        'AcquisitionFrameRateEnable',
                        'AcquisitionFrameRate',
                        'BalanceWhiteAuto'])
    nodes['AcquisitionFrameRateEnable'].value = True
    # nodes['AcquisitionFrameRate'].value = nodes['AcquisitionFrameRate'].min

    nodes['AcquisitionFrameRate'].value = float(fps)
    nodes['ExposureAuto'].value = 'Off'
    # nodes['BalanceWhiteAuto'].value = 'Off'
    print("Disable Auto Exposure")

    if nodes['ExposureTime'] is None:
        raise Exception("ExposureTime node not found")
    if nodes['ExposureTime'].is_writable is False:
        raise Exception("ExposureTime node is not writable")

    print(f"Acquisition frame rate: {nodes['AcquisitionFrameRate']}")

    nodes['ExposureTime'].value = nodes['ExposureTime'].max
    
    print(f"Exposure time: {nodes['ExposureTime'].value}")