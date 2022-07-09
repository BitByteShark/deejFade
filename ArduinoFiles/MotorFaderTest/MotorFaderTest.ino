//see Source:https://www.youtube.com/watch?v=r12wG7ebvnY&t=141s

#define potPin    10
#define enA       9
#define in1       7
#define in2       6
 
void setup() {
    Serial.begin(9600);
    pinMode(potPin, INPUT);
    pinMode(enA, OUTPUT);
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
}
 
void loop() {
    //Lumpy();
    SpringA();
    //SpringB();
}
 
void Lumpy(){
    int val = analogRead(potPin);
    for(int i = 0; i<1024; i+= 200){
       if(val >  i-50 && val < i+50){
          if(val > i+3){
              digitalWrite(in1, LOW); digitalWrite(in2, HIGH); 
              analogWrite(enA, 120);
          }else if(val < i-3){
              digitalWrite(in1, HIGH); digitalWrite(in2, LOW); 
              analogWrite(enA, 120);
          }else{
              analogWrite(enA, LOW);
          }
       }
    }
}
 
void SpringA(){
    int val = analogRead(potPin);
    if(val > 10){
        digitalWrite(in1, LOW);
        digitalWrite(in2, HIGH); 
        analogWrite(enA, map(val, 10, 1024, 100, 255));
    }else{
        analogWrite(enA, LOW);
    }
}
 
void SpringB(){
    int val = analogRead(potPin);
    if(val > 550){
        digitalWrite(in1, LOW);
        digitalWrite(in2, HIGH); 
        analogWrite(enA, map(val, 550, 1024, 120, 255));
    }else if(val < 450){
        digitalWrite(in1, HIGH);
        digitalWrite(in2, LOW); 
        analogWrite(enA, map(val, 450, 0, 120, 255));
    }else{
        analogWrite(enA, LOW);
    }
}
 
void SlideToValue(int targetValue){
  int val = analogRead(potPin);
  if(abs(val - targetValue) > 20){
      if(val > targetValue){
          digitalWrite(in1, LOW);
          digitalWrite(in2, HIGH); 
      }else{
          digitalWrite(in1, HIGH);
          digitalWrite(in2, LOW); 
      }
      analogWrite(enA, max(min(abs(val - targetValue), 255), 200));
  }else{
      // Turn off motor
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);  
      analogWrite(enA, 0);
  }
}
