#include "Seeed_MPR121_driver.h"

Mpr121 mpr121;
int touch_States[8];
int previous_States[8] = {0};
int channels[8] = {0, 1, 2, 3, 8, 9, 10, 11};


void setup()
{
  Serial.begin(115200);
  if (mpr121.begin() < 0)
  {
    Serial.println("Can't detect device!!!!");
  }
  else
  {
    Serial.println("mpr121 init OK!");
  }
  delay(100);
}

void loop() {
  bool valueChanged = false;

  for (int i = 0; i < 8; i++) {
    touch_States[i] = Check_Touch_State(channels[i]);

    // Check if the value has changed
    if (touch_States[i] != previous_States[i]) {
      valueChanged = true;  // A change was detected
      previous_States[i] = touch_States[i];  // Update the previous state
    }
  }

  // Send values only if a change was detected
  if (valueChanged) {
    for (int i = 0; i < 8; i++) {
      Serial.print(touch_States[i]);
    }
  }
  delay(100);
}


int Check_Touch_State(int channel){
  // Read the touch status register
  u16 result = mpr121.check_status_register(); 

  // Make sure the channel is within valid range (0-11)
  if (channel < 0 || channel >= CHANNEL_NUM)
  {
    Serial.println("Invalid channel number!");
    return -1;  // Return -1 if invalid channel number
  }

  // Check the touch state of the specified channel
  if (result & (1 << channel))
  {
    return 1;  // Channel is pressed
  }
  else
  {
    return 0;  // Channel is not pressed (released)
  }
}
