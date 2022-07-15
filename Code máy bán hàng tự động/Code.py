import RPi.GPIO as GPIO
import time
from threading import Thread

import glob

# Define GPIO to LCD mapping
LCD_RS = 5
LCD_E = 6
LCD_D4 = 12
LCD_D5 = 13
LCD_D6 = 16
LCD_D7 = 19
GPIO_Button_1 = 20
GPIO_Button_2 = 26
GPIO_Button_3 = 21
GPIO_Button_Cancel = 17
GPIO_Pump_Motor = 18
GPIO_Heater = 27

# Define some device constants
LCD_WIDTH = 16  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

Coffee_Price = 10000  # Giá một cốc cafe
Coffee_Milk_Price = 15000
Milk_Price = 10000
Product_Price = 0  # Giá sản phẩm hiện tại

Product_List = ["COFFEE", "COFFEE_MILK", "MILK"]
Product_Index = 0
Product_Choose = ""  # Sản phẩm người dùng chọn
Money_Input = 0  # Tiền người dùng đã nạp
Milk_Capacity = 2  # Dung tích bình sữa
Cafe_Capacity = 5  # Cafe capacity = 5kg
Coffee_Capacity = 5  # Dung tích bình cafe
Water_Capacity = 5  # Dung tích bình nước

Remaining_Milk = 1  # Lượng sữa còn lại
Remaining_Coffee = 3
Remaining_Ice = 3
Remaining_Water = 3

Is_People_Input_Money = False  # Nếu người mua đã nạp tiền
Is_People_Choose_Product = False  # Nếu người mua đã chọn sản phẩm

A_Cup_Of_Cafe_Formula = {"Cafe": 0.2, "Milk": 0, "Water": 0.2}  # Công thức cho một tách cafe đen
A_Cup_Of_Cafe_Milk_Formula = {"Cafe": 0.2, "Milk": 0.2, "Water": 0.2}  # Công thức cho một tách cafe sữa
A_Cup_Of_Milk_Formula = {"Cafe": 0, "Milk": 0.5, "Water": 0.2}  # Công thức cho một tách sữa


def check_for_a_cup_coffee():  # Kiểm tra lượng nguyên liệu cho một cốc cafe đen
    return A_Cup_Of_Cafe_Formula["Cafe"] < Remaining_Coffee and A_Cup_Of_Cafe_Formula["Milk"] < Remaining_Milk and \
           A_Cup_Of_Cafe_Formula["Water"] < Remaining_Water


def check_for_a_cup_coffee_milk():  # Kiểm tra lượng nguyên liệu cho một cốc cafe sữa
    return A_Cup_Of_Cafe_Milk_Formula["Cafe"] < Remaining_Coffee and A_Cup_Of_Cafe_Milk_Formula[
        "Milk"] < Remaining_Milk and A_Cup_Of_Cafe_Milk_Formula["Water"] < Remaining_Water


def check_for_a_cup_milk():  # Kiểm tra lượng nguyên liệu cho một cốc sữa
    return A_Cup_Of_Milk_Formula["Cafe"] < Remaining_Coffee and A_Cup_Of_Milk_Formula["Milk"] < Remaining_Milk and \
           A_Cup_Of_Milk_Formula["Water"] < Remaining_Water


def enable_pump_motor_and_heater():
    GPIO.output(GPIO_Pump_Motor, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(GPIO_Pump_Motor, GPIO.LOW)
    GPIO.output(GPIO_Heater, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(GPIO_Heater, GPIO.LOW)
    return


def product_preparation(product_choose):
    enable_pump_motor_and_heater()
    pwm1 = GPIO.PWM(22, 100)  ## PWM Frequency
    pwm1.start(0)
    pwm2 = GPIO.PWM(23, 100)  ## PWM Frequency
    pwm2.start(0)
    pwm3 = GPIO.PWM(24, 100)  ## PWM Frequency
    pwm3.start(0)

    if product_choose == "COFFEE":
        pwm1.ChangeDutyCycle(20)
        time.sleep(A_Cup_Of_Cafe_Formula["Cafe"] / 2 * 5 * 2)
        pwm1.ChangeDutyCycle(15)
        pwm2.ChangeDutyCycle(20)
        time.sleep(A_Cup_Of_Cafe_Formula["Milk"] / 2 * 5 * 2)
        pwm2.ChangeDutyCycle(15)
        pwm3.ChangeDutyCycle(20)
        time.sleep(A_Cup_Of_Cafe_Formula["Water"] / 2 * 5 * 2)
        pwm3.ChangeDutyCycle(15)

        time.sleep(2)
    if product_choose == "COFFEE_MILK":
        pwm1.ChangeDutyCycle(20)
        time.sleep(A_Cup_Of_Cafe_Milk_Formula["Cafe"] / 2 * 5 * 2)
        pwm1.ChangeDutyCycle(15)
        pwm2.ChangeDutyCycle(20)
        time.sleep(A_Cup_Of_Cafe_Milk_Formula["Milk"] / 2 * 5 * 2)
        pwm2.ChangeDutyCycle(15)
        pwm3.ChangeDutyCycle(20)
        time.sleep(A_Cup_Of_Cafe_Milk_Formula["Water"] / 2 * 5 * 2)
        pwm3.ChangeDutyCycle(15)

        time.sleep(2)
    if product_choose == "MILK":
        pwm1.ChangeDutyCycle(20)
        time.sleep(A_Cup_Of_Milk_Formula["Cafe"] / 2 * 5 * 2)
        pwm1.ChangeDutyCycle(15)
        pwm2.ChangeDutyCycle(20)
        time.sleep(A_Cup_Of_Milk_Formula["Milk"] / 2 * 5 * 2)
        pwm2.ChangeDutyCycle(15)
        pwm3.ChangeDutyCycle(20)
        time.sleep(A_Cup_Of_Milk_Formula["Water"] / 2 * 5 * 2)
        pwm3.ChangeDutyCycle(15)

        time.sleep(2)

    return


def program():
    # GPIO.input(GPIO_Button_1, GPIO.LOW)
    global Is_People_Add_Milk_To_Coffee
    global Is_People_Choose_Product
    global Is_People_Input_Money
    global Money_Input
    global Product_Choose
    global Product_Price
    global Coffee_Price
    global Coffee_Milk_Price
    global Milk_Price
    global Number_Product_Choose
    global Product_Index
    global Product_List

    lcd_string("CHON SAN PHAM", LCD_LINE_1)
    # lcd_string("", LCD_LINE_2)
    # lcd_string(Product_Choose, LCD_LINE_2)
    if not Is_People_Choose_Product:
        lcd_string("SP: " + Product_List[Product_Index], LCD_LINE_2)
        if GPIO.input(GPIO_Button_1):
            if Product_Index > 0:
                Product_Index -= 1
                time.sleep(0.5)
            # lcd_string("SP: " + Product_List[Product_Index], LCD_LINE_2)
        if GPIO.input(GPIO_Button_2):
            if Product_Index < 2:
                Product_Index += 1
                time.sleep(0.5)
            # lcd_string("SP: " + Product_List[Product_Index], LCD_LINE_2)
        if GPIO.input(GPIO_Button_3):
            lcd_string("CHON: " + Product_List[Product_Index], LCD_LINE_2)
            if Product_List[Product_Index] == "COFFEE":
                if not check_for_a_cup_coffee():
                    lcd_string("HET HANG !!!!", LCD_LINE_1)
                    time.sleep(2)
                    return
                Product_Price = Coffee_Price
            if Product_List[Product_Index] == "COFFEE_MILK":
                if not check_for_a_cup_coffee_milk():
                    lcd_string("HET HANG !!!!", LCD_LINE_1)
                    time.sleep(2)
                    return
                Product_Price = Coffee_Milk_Price
            if Product_List[Product_Index] == "MILK":
                if not check_for_a_cup_milk():
                    lcd_string("HET HANG !!!!", LCD_LINE_1)
                    time.sleep(2)
                    return
                Product_Price = Milk_Price
            Product_Choose = Product_List[Product_Index]

            Is_People_Choose_Product = True
            time.sleep(2)

    else:
        Is_Check_Milk_For_Coffee = False
        while Is_People_Choose_Product:
            if GPIO.input(17):  # Press cancel button
                lcd_string("DA HUY MUA", LCD_LINE_1)
                lcd_string("", LCD_LINE_2)
                time.sleep(1)
                Is_People_Input_Money = False
                Is_People_Choose_Product = False
                Is_People_Add_Milk_To_Coffee = False
                return

            if Money_Input == 0:
                lcd_string("XIN NAP TIEN", LCD_LINE_1)
            else:
                lcd_string("DA NAP " + str(Money_Input), LCD_LINE_1)
            lcd_string("GIA : " + str(Product_Price), LCD_LINE_2)
            # lcd_string("", LCD_LINE_2)
            if not Is_People_Input_Money:
                # lcd_string("DA NAP " + str(Money_Input), LCD_LINE_1)
                if GPIO.input(GPIO_Button_1):
                    Money_Input += 10000
                    lcd_string("DA NAP " + str(Money_Input), LCD_LINE_1)
                    time.sleep(2)
                    # Is_People_Input_Money = True
                if GPIO.input(GPIO_Button_2):
                    Money_Input += 5000
                    lcd_string("DA NAP " + str(Money_Input), LCD_LINE_1)
                    time.sleep(2)
                    # Is_People_Input_Money = True
                if GPIO.input(GPIO_Button_3):
                    Money_Input += 2000
                    lcd_string("DA NAP " + str(Money_Input), LCD_LINE_1)
                    time.sleep(2)
                    # Is_People_Input_Money = True
                if Product_Choose == "COFFEE":
                    if Money_Input >= Coffee_Price:
                        Is_People_Input_Money = True
                elif Product_Choose == "COFFEE_MILK":
                    if Money_Input >= Coffee_Milk_Price:
                        Is_People_Input_Money = True
                elif Product_Choose == "MILK":
                    if Money_Input >= Milk_Price:
                        Is_People_Input_Money = True

            else:
                while Is_People_Input_Money:
                    lcd_string("", LCD_LINE_2)
                    lcd_string("DANG PHA CHE....", LCD_LINE_1)
                    lcd_string("WAITING....", LCD_LINE_2)

                    # Dong cua
                    pwm = GPIO.PWM(4, 100)
                    pwm.start(0)
                    pwm.ChangeDutyCycle(20)
                    #

                    # Bơm nước
                    thread = Thread(target=enable_pump_motor_and_heater())
                    thread.start()
                    #

                    product_preparation(Product_Choose)
                    pwm.ChangeDutyCycle(15)
                    time.sleep(2)
                    lcd_string("XIN NHAN HANG", LCD_LINE_1)
                    lcd_string("THANK YOU", LCD_LINE_2)
                    time.sleep(2)
                    Is_People_Input_Money = False
                    Is_People_Choose_Product = False
                    Is_People_Add_Milk_To_Coffee = False

                    Money_Input = 0
                    Product_Choose = ""
                    # time.sleep(2)


def main():
    # Main program block
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT)  # RS
    GPIO.setup(LCD_D4, GPIO.OUT)  # DB4
    GPIO.setup(LCD_D5, GPIO.OUT)  # DB5
    GPIO.setup(LCD_D6, GPIO.OUT)  # DB6
    GPIO.setup(LCD_D7, GPIO.OUT)  # DB7

    GPIO.setup(GPIO_Button_1, GPIO.IN)
    GPIO.setup(GPIO_Button_2, GPIO.IN)
    GPIO.setup(GPIO_Button_3, GPIO.IN)
    GPIO.setup(GPIO_Button_Cancel, GPIO.IN)
    GPIO.setup(GPIO_Pump_Motor, GPIO.OUT)
    GPIO.setup(GPIO_Heater, GPIO.OUT)

    # angle1 = 50
    # duty1 = float(angle1) / 10 + 2
    # angle2 = 160
    # duty2 = float(angle2) / 10 + 2.5
    GPIO.setup(4, GPIO.OUT)
    pwm = GPIO.PWM(4, 100)  ## PWM Frequency
    pwm.start(0)
    GPIO.setup(22, GPIO.OUT)
    pwm = GPIO.PWM(22, 100)  ## PWM Frequency
    pwm.start(0)
    GPIO.setup(23, GPIO.OUT)
    pwm = GPIO.PWM(23, 100)  ## PWM Frequency
    pwm.start(0)
    GPIO.setup(24, GPIO.OUT)
    pwm = GPIO.PWM(24, 100)  ## PWM Frequency
    pwm.start(0)
    GPIO.setup(25, GPIO.OUT)
    pwm = GPIO.PWM(25, 100)  ## PWM Frequency
    pwm.start(0)
    """while 1:
        pwm.ChangeDutyCycle(60)  # 16 : 18 do, 17 : 36 do, 18 : 54 do
        # time.sleep(0.8)
        # pwm.ChangeDutyCycle(10)
        time.sleep(5)
        pwm.ChangeDutyCycle(18)
        time.sleep(5)"""
    # Initialise display
    lcd_init()

    while True:
        program()

        # time.sleep(2)


def lcd_init():
    # Initialise display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)


def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command

    GPIO.output(LCD_RS, mode)  # RS

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    lcd_toggle_enable()


def lcd_toggle_enable():
    # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)


def lcd_string(message, line):
    # Send string to display

    message = message.ljust(LCD_WIDTH, " ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)


if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_byte(0x01, LCD_CMD)
        lcd_string("Goodbye!", LCD_LINE_1)
        GPIO.cleanup()
