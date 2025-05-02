import cv2

def show_split_color_image(npndarray, fps=None):
    # R, G, B 채널 분리
    r, g, b = cv2.split(npndarray)  # shape: (H, W) 각각

    # 채널 문자 삽입
    cv2.putText(r, 'R', (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
    cv2.putText(g, 'G', (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)
    cv2.putText(b, 'B', (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 3, cv2.LINE_AA)

    # 원래 영상에도 FPS 텍스트 추가
    cv2.putText(npndarray, fps, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (100, 255, 0), 3, cv2.LINE_AA)

    # 창으로 띄우기
    cv2.imshow('Original (BGR)', cv2.cvtColor(npndarray, cv2.COLOR_BGR2RGB))
    cv2.imshow('Red Channel', r)
    cv2.imshow('Green Channel', g)
    cv2.imshow('Blue Channel', b)
    
def set_maximum_exposure(device, fps):
	
	nodemap = device.nodemap
	nodes = nodemap.get_node(['ExposureAuto', 'ExposureTime',
						'AcquisitionFrameRateEnable',
						'AcquisitionFrameRate'])
	nodes['AcquisitionFrameRateEnable'].value = True
	# nodes['AcquisitionFrameRate'].value = nodes['AcquisitionFrameRate'].min
	nodes['AcquisitionFrameRate'].value = float(fps)
	nodes['ExposureAuto'].value = 'Off'
	print("Disable Auto Exposure")

	if nodes['ExposureTime'] is None:
		raise Exception("ExposureTime node not found")
	if nodes['ExposureTime'].is_writable is False:
		raise Exception("ExposureTime node is not writable")

	print(f"Acquisition frame rate: {nodes['AcquisitionFrameRate']}")

	nodes['ExposureTime'].value = nodes['ExposureTime'].max
	
	print(f"Exposure time: {nodes['ExposureTime'].value}")