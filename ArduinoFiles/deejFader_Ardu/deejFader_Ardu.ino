const int numButtons=6;
const int potiPin=10;
const int buttonPin[numButtons] = {21,20,19,18,4,8};
const int ledPin = 5;
const int motorDrPin_ENB=9;
const int motoDrPin_IN4=6;
const int motoDrPin_IN3=7;
const int threshold=7;

int buttonState[numButtons]={LOW,LOW,LOW,LOW,LOW,LOW};//HIGH=unpressed, LOW=pressed
int prevButtonState[numButtons]={LOW,LOW,LOW,LOW,LOW,LOW};
int potiValue=0;
String serialMessage="";
String serialString="";

int sessionSoundLevel=0;
int currentSessionID=0;
int prevSessionID=0;
int prevSentVolumeValue=NULL;
bool sliderMovementSucess=false;
unsigned int sliderMotorizedMovementSuccessTimer = 1;
unsigned int sliderMotorizedMovementTimer = 1;//above 0 acts as indicator for active motorized movement
unsigned int sliderManualMovementTimer = 0;//above 0 acts as indicator for active manual movement


void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(potiPin, INPUT);
  pinMode(motorDrPin_ENB, OUTPUT);
  pinMode(motoDrPin_IN3, OUTPUT);
  pinMode(motoDrPin_IN4, OUTPUT);

  for (int i = 0; i < numButtons; i++) {
   pinMode(buttonPin[i], INPUT_PULLUP);
  }
  Serial.begin(9600);
}

void loop() {
  //read button states
  for (int i=0; i<numButtons; i++) {
   buttonState[i]=digitalRead(buttonPin[i]);
  }
  digitalWrite(ledPin,LOW);

  //check buttoninput
  //initiate session switch from current PID onwards based on button input
  if (buttonState[0]==LOW && prevButtonState[0]==HIGH){
    serialMessage=standardizeFormatString(currentSessionID,6)+"|sC|p";//sessionChange|previous
    Serial.println(serialMessage);
  }else if (buttonState[1]==LOW && prevButtonState[1]==HIGH){
    serialMessage=standardizeFormatString(currentSessionID,6)+"|sC|n";//sessionChange|next
    Serial.println(serialMessage);
  }

  //read Serial chunkwise
  //incoming text holds information about the next PID and its soundlevel
  if (Serial.available() > 0){
    char varChunk=NULL;
    String incomingText="";
    String incomingCommand="";
    while (Serial.available() > 0) {
      varChunk=Serial.read();
      incomingText+=varChunk;
    }
    currentSessionID=incomingText.substring(0,6).toInt();
    incomingCommand=incomingText.substring(7,9).toInt();
    sessionSoundLevel=incomingText.substring(10,14).toInt();
    if (incomingCommand="sI"){
      digitalWrite(ledPin,HIGH);
      sliderMotorizedMovementTimer=1;//initiates motorized slider movement
    }
    //Debug:
    //Serial.println(standardizeFormatString(currentSessionID,6)+"|"+incomingCommand+"|"+standardizeFormatString(sessionSoundLevel,4));
  }
  
  //sessionchange Event
  /*
  if (prevSessionID!=currentSessionID){
    digitalWrite(ledPin,HIGH);
    sliderMotorizedMovementTimer=1;//initiates motorized slider movement
  }
  */

  //AUTOMATIC MOVEMENT BLOCK
  if (sliderMotorizedMovementTimer!=0){
    sliderManualMovementTimer=0;//finish manual movement
    sliderMotorizedMovementTimer++;//count up whole movementtime until unsuccessful stop condition
    sliderMovementSucess=SlideToValue(sessionSoundLevel);
    if (sliderMovementSucess){//count successful iterations and allows finish if the slider reached the target location and stays within borders safely
      sliderMotorizedMovementSuccessTimer++;
    }else{
      sliderMotorizedMovementSuccessTimer=0;
    }
    if (sliderMotorizedMovementTimer>=800|sliderMotorizedMovementSuccessTimer>=100){//stop condition if either successful ur unsuccessful maxTime is reached
      digitalWrite(motoDrPin_IN3, LOW);
      digitalWrite(motoDrPin_IN4, LOW);
      analogWrite(motorDrPin_ENB, 0);
      sliderMotorizedMovementTimer=0;//reset timers
      sliderMotorizedMovementSuccessTimer=0;
    }
  }

  //MANUAL MOVEMENT BLOCK
  potiValue = analogRead(potiPin);     //read the value from the sensor and map range from 0-1024 to 0-100
  if (sliderMotorizedMovementTimer==0){//no manual overwrite allowed if slider is currently moved by the motor
    int slidingDiff=abs(potiValue-sessionSoundLevel);
    if (sliderManualMovementTimer!=0 || slidingDiff>threshold+2){
      //slider starts to recognize manual input if difference between memorized session level and continuous read exceeds the threshold
      //after initial threshold also minimal movement is registered until no movement is detected for multiple iterations
      if (slidingDiff<3){//2 should be possible too
        sliderManualMovementTimer++;//count up thorugh time with high sensitivity if no new movement detected
      }else{
        sliderManualMovementTimer=1;//restart count if new movement is detected
      }
      sessionSoundLevel=potiValue;//within the manual movement phase we always write new values
      if (sliderManualMovementTimer>=300){//250
        sliderManualMovementTimer=0;//exit condition
      }
    }
  }

  //send information about soundlevelchange based on manual movement
  if (sliderManualMovementTimer>0){//check if manual movement is currently happening
    if (prevSentVolumeValue==NULL || abs(prevSentVolumeValue-sessionSoundLevel)>threshold){//just send changing Values
      serialString=standardizeFormatString(currentSessionID,6)+"|vL|"+standardizeFormatString(sessionSoundLevel,4);//volumeLevel Change
      Serial.println(serialString);
      prevSentVolumeValue=sessionSoundLevel;
    }
  }else{
    prevSentVolumeValue=NULL;
  }
  
  //memorize this iterations button states to check for button press or release events and just register singtle time buttonpress
  for (int i=0; i<numButtons; i++) {
   prevButtonState[i]=buttonState[i];
  }
  prevSessionID=currentSessionID;
}

int intIncrementWrapped(int number, int minEnd, int maxEnd, bool upwards) {
  if (upwards){
    if (number>=minEnd && number<maxEnd){
      return ++number;
    }else{
      return minEnd;
    }
  } else {
    if (number>minEnd && number<=maxEnd){
      return --number;
    }else{
      return maxEnd;
    }
  }
}

//pad string from int with leading zeros for fix number of characters in string
String standardizeFormatString(int integer, int numberOfChars){
  char buffer[7];
  int n;
  // I know ... I'm sorry
  if (numberOfChars==4){
    n=sprintf(buffer, "%04d", integer);//prints the formatted number into the Buffer, see: http://www.cplusplus.com/reference/cstdio/sprintf/
  }else if(numberOfChars==6){
    n=sprintf(buffer, "%06d", integer);//prints the formatted number into the Buffer, see: http://www.cplusplus.com/reference/cstdio/sprintf/
  }else{
    return;
  }
  return String(buffer);
}

bool SlideToValue(int targetValue){
  int val = analogRead(potiPin);
  if(abs(val - targetValue) >= threshold){
    //Case wenn sich der Schieber Außerhalb des Zielbereichs um den Zielwert befindet
      if(val > targetValue){
        //Schieber ist zu hoch
          digitalWrite(motoDrPin_IN3, LOW);
          digitalWrite(motoDrPin_IN4, HIGH); 
      }else{
        //Schieber ist zu niedrig
          digitalWrite(motoDrPin_IN3, HIGH);
          digitalWrite(motoDrPin_IN4, LOW); 
      }
      //analogWrite(motorDrPin_ENB,130);
      //analogWrite(motorDrPin_ENB,250);
      analogWrite(motorDrPin_ENB, max(min(abs(val - targetValue), 200), 130));
      //SpeedValue is equal to the distance between Slider and target but max 240 and min 130
      return 0;
  }else{
    //Case Schieber ist im Zielbereich
    
      // Turn off motor
      digitalWrite(motoDrPin_IN3, LOW);
      digitalWrite(motoDrPin_IN4, LOW);  
      analogWrite(motorDrPin_ENB, 0);
      return true;
  }
}
