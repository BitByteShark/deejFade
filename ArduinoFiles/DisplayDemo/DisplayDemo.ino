#include "lcdgfx.h"
#include "lcdgfx_gui.h"
#include "owl.h"

// The parameters are  RST pin, BUS number, CS pin, DC pin, FREQ (0 means default), CLK pin, MOSI pin
DisplayIL9163_128x128x16_SPI display(3,{-1, 4, 5, 0,-1,-1}); // Use this line for Atmega328p
//DisplayIL9163_128x128x16_SPI display(3,{-1, -1, 4, 0, -1, -1}); // FOR ATTINY
//DisplayIL9163_128x128x16_SPI display(-1,{-1, 0, 1, 0, -1, -1); // Use this line for nano pi (RST not used, 0=CE, gpio1=D/C)
//DisplayIL9163_128x128x16_SPI display(24,{-1, 0, 23, 0,-1,-1}); // Use this line for Raspberry  (gpio24=RST, 0=CE, gpio23=D/C)
//DisplayIL9163_128x128x16_SPI display(22,{-1, 5, 21, 0,-1,-1}); // Use this line for ESP32 (VSPI)  (gpio22=RST, gpio5=CE for VSPI, gpio21=D/C)
//DisplayIL9163_128x128x16_SPI display(4,{-1, -1, 5, 0,-1,-1});  // Use this line for ESP8266 Arduino style rst=4, CS=-1, DC=5
                                                               // And ESP8266 RTOS IDF. GPIO4 is D2, GPIO5 is D1 on NodeMCU boards
static void bitmapDemo()
{
    display.setColor(RGB_COLOR16(64,64,255));
    display.drawBitmap1(0, 0, 128, 64, Owl);
    //display.drawXBitmap(0, 0, 40, 32, Owl);
    lcd_delay(1000);
}

void setup()
{
    display.begin();
    display.setFixedFont(ssd1306xled_font6x8);
    display.fill( 0x0000 );
}

uint8_t rotation = 0;

void loop()
{
    lcd_delay(500);
    bitmapDemo();
    display.getInterface().setRotation((++rotation) & 0x03);
    display.fill(0x00);
    display.setColor(RGB_COLOR16(255,255,255));
}
