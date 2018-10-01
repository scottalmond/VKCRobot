

int ENC0[]={7,8};
int ENC1[]={9,10};
boolean ENC0_state[]={false,false};
boolean ENC1_state[]={false,false};

volatile long ENC0_counts=0;
volatile long ENC1_counts=0;

void setup(){
  Serial.begin(115200);
  for(int id=0;id<2;id++)
  {
    pinMode(ENC0[id],INPUT_PULLUP);
    pinMode(ENC1[id],INPUT_PULLUP);
    ENC0_state[id]=digitalRead(ENC0[id])==HIGH;
    ENC1_state[id]=digitalRead(ENC1[id])==HIGH;
    pciSetup(ENC0[id]);
    pciSetup(ENC1[id]);
  }
  sei();
//  PCICR |= _BV(PCIE0);
//  PCICR |= bit( digitalPinToPCICRbit(ENC0[0]) )
  //PCMSK2 |= _BV(PCINT2);
  //PCMSK2 |= _BV(PCINT3);
}

void pciSetup(byte pin){
  Serial.print("SETUP: ");
  Serial.println(pin,DEC);
  *digitalPinToPCMSK(pin) |= bit( digitalPinToPCMSKbit(pin) ); //enable pin
  PCIFR |= bit( digitalPinToPCICRbit(pin) );//clear outstanding interrupt
  PCICR |= bit( digitalPinToPCICRbit(pin) );//enable interrupt for group
}

void loop(){
//if serial command, respond with encoder coun status  
Serial.print(ENC0_counts,DEC);
Serial.print(", ");
Serial.println(ENC1_counts,DEC);
delay(1000);
}

ISR(PCINT2_vect){ //D0 to D7
  ENC0_counts+=1; //placeholder
}

ISR(PCINT0_vect){ //D8 to D14
  ENC1_counts+=1;
}
