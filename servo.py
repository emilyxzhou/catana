def servocall():
    import RPi.GPIO as GPIO
    import time

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(17,GPIO.OUT)

    servo = GPIO.PWM(17,50)
    servo.start(0)

    time.sleep(2)

    duty = 7

    while duty <= 10:
        servo.ChangeDutyCycle(duty)
        time.sleep(0.25)
        duty = duty + 1

    time.sleep(2)


    servo.stop()
    GPIO.cleanup()
