# importing OpenCV, time and Pandas library
import cv2
import serial
from serial.tools import list_ports

# Gerekli kütüphaneler: opencv-python, pyserial

# arduino ile haberleşme kurma
try:
    arduino = serial.Serial(port=serial.tools.list_ports.comports()[0][0], baudrate=9600, timeout=.1)
except:
    print("\nArduino bağlı değil. Sadece görüntü algılama çalışacak!")
    #exit()

# goruntu_degeri (hareket algılanırsa 1, algılanmazsa 0)
goruntu_degeri = 0

# Alarım aktif/pasif
alarm_sistemi_durumu = 1

# Assigning our static_back to None
static_back = None

# Capturing video
video = cv2.VideoCapture(0, cv2.CAP_DSHOW)


def arduino_kontrol():
    global alarm_sistemi_durumu
    if (arduino.inWaiting() > 0):
        alarm_sistemi_durumu = int(arduino.readline())
        print("Arduinodan gelen veri: ", alarm_sistemi_durumu)


# Infinite while loop to treat stack of image as video
while True:
    try:
        arduino_kontrol()
    except:
        pass
    if alarm_sistemi_durumu == 0:  # Görünütü algılamayı durdur
        video.release()
        cv2.destroyAllWindows()
        static_back = None
        continue

    elif alarm_sistemi_durumu == 1:  # Görüntü algılamaya devam et
        if video.isOpened() == False:
            video = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    elif alarm_sistemi_durumu == 2:  # Görüntüyü sıfırla
        if video.isOpened() == False:
            video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        static_back = None
        alarm_sistemi_durumu = 1
    else:
        print("HATA!")
        continue

    # Reading frame(image) from video
    check, frame = video.read()

    # Initializing motion = 0(no motion)
    motion = 0

    # Converting color image to gray_scale image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Converting gray scale image to GaussianBlur
    # so that change can be find easily
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # In first iteration we assign the value
    # of static_back to our first frame
    if static_back is None:
        static_back = gray
        continue

    # Difference between static background
    # and current frame(which is GaussianBlur)
    diff_frame = cv2.absdiff(static_back, gray)

    # If change in between static background and
    # current frame is greater than 30 it will show white color(255)
    thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # Finding contour of moving object
    cnts, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        motion = 1

        (x, y, w, h) = cv2.boundingRect(contour)
        # making green rectangle around the moving object
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

    if motion == 1 and goruntu_degeri == 0:
        try:
            arduino.write("1".encode('utf-8'))  # Görüntü algılandı
        except:
            pass
        goruntu_degeri = 1
    if motion == 0 and goruntu_degeri == 1:
        goruntu_degeri = 0

    # Displaying image in gray_scale
    # cv2.imshow("Gray Frame", gray)

    # Displaying the difference in currentframe to
    # the staticframe(very first_frame)
    # cv2.imshow("Difference Frame", diff_frame)

    # Displaying the black and white image in which if
    # intensity difference greater than 30 it will appear white
    # cv2.imshow("Threshold Frame", thresh_frame)

    # Displaying color frame with contour of motion of object
    cv2.imshow("Color Frame", frame)

    key = cv2.waitKey(1)
    # if q entered whole process will stop
    if key == ord('q'):
        break

    # Eğer y tuşuna basılırsa görüntü sıfırlanır
    if key == ord('y'):
        static_back = gray
        continue

video.release()

# Destroying all the windows
cv2.destroyAllWindows()
