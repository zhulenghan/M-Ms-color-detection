import cv2
import serial.tools.list_ports
from PIL import Image
import torch
from torchvision import transforms
from model import resnet18
import time
from com import send
from pynput import keyboard
from pynput.keyboard import Key, Controller

keyboard0 = Controller()

isEnd = False


def keyboard_on_release(key):
    global isEnd
    if key == keyboard.Key.esc:
        isEnd = True
        return False

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print("{} is in use".format(device))

data_transform = transforms.Compose(
    [transforms.CenterCrop([256, 256]),
     transforms.Resize(224),
     transforms.ToTensor(),
     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])


net = resnet18(num_classes=7).to(device)
net.load_state_dict(torch.load("weight/mms.pth", map_location=device))
net.eval()


device_exist = 0
port_list = list(serial.tools.list_ports.comports())
port_name = "STM32"
for i in range(0, len(port_list)):
    if port_name in port_list[i].description:
        serial = serial.Serial(port_list[i].device)
        device_exist = 1

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

stopper = keyboard.Listener(on_release=keyboard_on_release)
while 1:

    with keyboard.Listener(
            on_release=keyboard_on_release) as starter:
        starter.join()

    stopper = keyboard.Listener(on_release=keyboard_on_release)
    stopper.start()
    isEnd = False


    start_time = time.time()
    x = 1  # displays the frame rate every 1 second
    counter = 0

    while 1:

        ret, frame = cap.read()
        '''cv2.imshow("capture", frame)'''
        frame_PIL = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image = torch.unsqueeze(data_transform(frame_PIL), dim=0)

        with torch.no_grad():
            output = torch.squeeze(net(image.to(device))).cpu()
            predict = torch.argmax(output).numpy()

        if device_exist:
            send(serial, 0, predict)

        '''print(class_indict[str(predict)])'''

        counter += 1
        if (time.time() - start_time) >= x:

            print("FPS: %.3f" % (counter / (time.time() - start_time)))

            counter = 0
            start_time = time.time()

        if device_exist:
            send(serial, 1, predict)

        if isEnd:
            break
