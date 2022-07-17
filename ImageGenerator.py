import cv2

# Farbsystem für lcdgfx: BBBGGGRR
# blue:XXX00000
# green:000XXX00
# red:000000XX

blue_max_Value=pow(2,3)-1
green_max_Value=pow(2,3)-1
red_max_Value=(pow(2,2)-1)

img_Path="/home/bitbyteshark/Coding/deejFade/FirefoxLogo128x128_Input.png"
#img_Path="/home/bitbyteshark/Coding/deejFade/DiscordLogo128x128_Input.png"
#img_Path="/home/bitbyteshark/Coding/deejFade/SpotifyLogo128x128_Input.png"

cvimg=cv2.imread(img_Path)

pixel_8bit_color_values=[]
for row in cvimg:
    for pixel in row:
        blue_value_255=pixel[0]
        green_value_255=pixel[1]
        red_value_255=pixel[2]
        
        #farbwert durch maximalwert teilen --> 0-1 und dann mit 8bit max-Wert scalen
        binary_blue_component=int(round((blue_value_255/255)*blue_max_Value))<<5
        binary_green_component=int(round((green_value_255/255)*green_max_Value))<<2
        binary_red_component=int(round((red_value_255/255)*red_max_Value))<<0
        
        pixel_color_value_8bit=binary_red_component + binary_green_component + binary_blue_component
        pixel_8bit_color_values.append(pixel_color_value_8bit)

hex_color_list=','.join(map(hex,pixel_8bit_color_values))



#https://www.digole.com/tools/PicturetoC_Hex_converter.php
#https://github.com/robertgallup/python-bmp2hex/blob/master/bmp2hex.py

# =============================================================================
# from PIL import Image
# 
# image=Image.open(img_Path)
# result = image.quantize(colors=256, method=2)
# result.save(file_out)
# data=result.getdata()
# =============================================================================
