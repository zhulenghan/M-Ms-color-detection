import serial.tools.list_ports
import cv2

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)



port_list = list(serial.tools.list_ports.comports())

port_name = "STM32"

for i in range(0, len(port_list)):
    if port_name in port_list[i].description:
        serial = serial.Serial(port=port_list[i].device,timeout=2)
        serial = serial.Serial()
if serial.isOpen():
    print('串口已打开')
else:
    print('串口未打开')

data = (1).to_bytes(1, byteorder= "big")
serial.write(data)

while True:
    data = serial.read(20)    #串口读20位数据
    if data != b'':
        break
print ('receive data is :',data)

# 关闭串口
serial.close()

if serial.isOpen():
    print('串口未关闭')
else:
    print('串口已关闭')