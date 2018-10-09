//code functions:
//read serial input, ex:
//  "1,1,0,0\n" --> turns on LEDS 0 and 1, rest OFF
//  "0,1,1,0\n" --> turns on LEDS 1 and 2, rest OFF
//read absolute encoders
//parse raw readings to engineering units (0-127 positions in circle correspond to 0 to 360 degrees)
//output (10 numbers in csv format with a new line character at the end):
//  first 3 numbers are revolution count, sub-position count, and error count for encoder A
//  next 3 numbers are the same for encoder B
//  last four numbers of ON (1) and OFF (0) state of the four LEDS
//  "11,22,33,44,55,66,1,0,0,1\n" --> Encoder A is on revolution 11, with a subposition of 22 (360*22/128 = degrees), and has encountered 33 bad readings
//    Encoder B is on revolution 44, with a subposition of 55 (360*55/128 = degrees) nad has encoutnered 66 bad readings
//    LED 0 is ON (1), LED 1 is OFF (0), LED 2 is OFF (0), LED 3 is ON (1)

//consts
const boolean IS_DEBUG=false;//extra info in print statements
const int ENCODER_COUNT=2;
const int PINS_PER_ENCODER=8;
const int LED_COUNT=4;

//encoders
//pin assignments
// MePed Arduino AtMega328 Nano pinout: http://www.meped.io/sites/default/files/inline-images/mePed%20PCB%20v1.3%20Labels%2C%20500px.jpg
// EAW0J-C24-AE0128L absolute encoder: https://www.mouser.com/datasheet/2/54/ce-777357.pdf
//encoder A pin 1 to S0 on mePed
//encoder B pin 1 to A7 on mePed
const int ENCODER_PINS[ENCODER_COUNT][PINS_PER_ENCODER]={
  /*LSB*/{2,3,4,5,6,7,8,9}/*MSB*/
  /*LSB*/,{A0,A1,A2,A3,A4,A5,A6,A7}/*MSB*/
};
const int ENCODER_CODE_LENGTH=256;//number of indexes in lookup table
const int ENCODER_MAX_VALUE=127;//max value after decrypting
int ENCODER_LOOKUP[ENCODER_CODE_LENGTH];
int encoder_revolutions[ENCODER_COUNT]={0,0};//15"wheel circumference, rolls over at 7.5 miles driven since startup
int encoder_last_position[ENCODER_COUNT]={0,0};
int encoder_bad_reading_counter[ENCODER_COUNT]{0,0};

//LEDs
const int LED_PINS[LED_COUNT]={10,11,12,13};
boolean led_state[LED_COUNT]={false,false,false,false};

void setup()
{
  //init pins with ~20k ohm pull-ups
  for(int encoder_iter=0;encoder_iter<ENCODER_COUNT;encoder_iter++)
  {
    for(int pin_iter=0;pin_iter<PINS_PER_ENCODER;pin_iter++)
    {
      int pin=ENCODER_PINS[encoder_iter][pin_iter];
      if(pin==A6 || pin==A7)
        pinMode(pin,INPUT);
      else
        pinMode(pin,INPUT_PULLUP);
    }
  }
  for(int led_iter=0;led_iter<LED_COUNT;led_iter++)
  {
    int pin=LED_PINS[led_iter];
    pinMode(pin,OUTPUT);
  }
  Serial.begin(115200);
  
  //populate lookup table
  //first step is default invalid values since not every index is used
  for(int iter=0;iter<ENCODER_CODE_LENGTH;iter++)
    ENCODER_LOOKUP[iter]=-1;//invalid value at unspecified index
  
  //map raw readings to meaningful values between 0 and 128
  // hard coded from https://www.kynix.com/uploadfiles/pdf0125/EAW0J-C24-AE0128L.pdf
  ENCODER_LOOKUP[127]=  0;
  ENCODER_LOOKUP[ 63]=  1;
  ENCODER_LOOKUP[ 62]=  2;
  ENCODER_LOOKUP[ 58]=  3;
  ENCODER_LOOKUP[ 56]=  4;
  ENCODER_LOOKUP[184]=  5;
  ENCODER_LOOKUP[152]=  6;
  ENCODER_LOOKUP[ 24]=  7;
  ENCODER_LOOKUP[  8]=  8;
  ENCODER_LOOKUP[ 72]=  9;
  ENCODER_LOOKUP[ 73]= 10;
  ENCODER_LOOKUP[ 77]= 11;
  ENCODER_LOOKUP[ 79]= 12;
  ENCODER_LOOKUP[ 15]= 13;
  ENCODER_LOOKUP[ 47]= 14;
  ENCODER_LOOKUP[175]= 15;
  ENCODER_LOOKUP[191]= 16;
  ENCODER_LOOKUP[159]= 17;
  ENCODER_LOOKUP[ 31]= 18;
  ENCODER_LOOKUP[ 29]= 19;
  ENCODER_LOOKUP[ 28]= 20;
  ENCODER_LOOKUP[ 92]= 21;
  ENCODER_LOOKUP[ 76]= 22;
  ENCODER_LOOKUP[ 12]= 23;
  ENCODER_LOOKUP[  4]= 24;
  ENCODER_LOOKUP[ 36]= 25;
  ENCODER_LOOKUP[164]= 26;
  ENCODER_LOOKUP[166]= 27;
  ENCODER_LOOKUP[167]= 28;
  ENCODER_LOOKUP[135]= 29;
  ENCODER_LOOKUP[151]= 30;
  ENCODER_LOOKUP[215]= 31;
  ENCODER_LOOKUP[223]= 32;
  ENCODER_LOOKUP[207]= 33;
  ENCODER_LOOKUP[143]= 34;
  ENCODER_LOOKUP[142]= 35;
  ENCODER_LOOKUP[ 14]= 36;
  ENCODER_LOOKUP[ 46]= 37;
  ENCODER_LOOKUP[ 38]= 38;
  ENCODER_LOOKUP[  6]= 39;
  ENCODER_LOOKUP[  2]= 40;
  ENCODER_LOOKUP[ 18]= 41;
  ENCODER_LOOKUP[ 82]= 42;
  ENCODER_LOOKUP[ 83]= 43;
  ENCODER_LOOKUP[211]= 44;
  ENCODER_LOOKUP[195]= 45;
  ENCODER_LOOKUP[203]= 46;
  ENCODER_LOOKUP[235]= 47;
  ENCODER_LOOKUP[239]= 48;
  ENCODER_LOOKUP[231]= 49;
  ENCODER_LOOKUP[199]= 50;
  ENCODER_LOOKUP[ 71]= 51;
  ENCODER_LOOKUP[  7]= 52;
  ENCODER_LOOKUP[ 23]= 53;
  ENCODER_LOOKUP[ 19]= 54;
  ENCODER_LOOKUP[  3]= 55;
  ENCODER_LOOKUP[  1]= 56;
  ENCODER_LOOKUP[  9]= 57;
  ENCODER_LOOKUP[ 41]= 58;
  ENCODER_LOOKUP[169]= 59;
  ENCODER_LOOKUP[233]= 60;
  ENCODER_LOOKUP[225]= 61;
  ENCODER_LOOKUP[229]= 62;
  ENCODER_LOOKUP[245]= 63;
  ENCODER_LOOKUP[247]= 64;
  ENCODER_LOOKUP[243]= 65;
  ENCODER_LOOKUP[227]= 66;
  ENCODER_LOOKUP[163]= 67;
  ENCODER_LOOKUP[131]= 68;
  ENCODER_LOOKUP[139]= 69;
  ENCODER_LOOKUP[137]= 70;
  ENCODER_LOOKUP[129]= 71;
  ENCODER_LOOKUP[128]= 72;
  ENCODER_LOOKUP[132]= 73;
  ENCODER_LOOKUP[148]= 74;
  ENCODER_LOOKUP[212]= 75;
  ENCODER_LOOKUP[244]= 76;
  ENCODER_LOOKUP[240]= 77;
  ENCODER_LOOKUP[242]= 78;
  ENCODER_LOOKUP[250]= 79;
  ENCODER_LOOKUP[251]= 80;
  ENCODER_LOOKUP[249]= 81;
  ENCODER_LOOKUP[241]= 82;
  ENCODER_LOOKUP[209]= 83;
  ENCODER_LOOKUP[193]= 84;
  ENCODER_LOOKUP[197]= 85;
  ENCODER_LOOKUP[196]= 86;
  ENCODER_LOOKUP[192]= 87;
  ENCODER_LOOKUP[ 64]= 88;
  ENCODER_LOOKUP[ 66]= 89;
  ENCODER_LOOKUP[ 74]= 90;
  ENCODER_LOOKUP[106]= 91;
  ENCODER_LOOKUP[122]= 92;
  ENCODER_LOOKUP[120]= 93;
  ENCODER_LOOKUP[121]= 94;
  ENCODER_LOOKUP[125]= 95;
  ENCODER_LOOKUP[253]= 96;
  ENCODER_LOOKUP[252]= 97;
  ENCODER_LOOKUP[248]= 98;
  ENCODER_LOOKUP[232]= 99;
  ENCODER_LOOKUP[224]=100;
  ENCODER_LOOKUP[226]=101;
  ENCODER_LOOKUP[ 98]=102;
  ENCODER_LOOKUP[ 96]=103;
  ENCODER_LOOKUP[ 32]=104;
  ENCODER_LOOKUP[ 33]=105;
  ENCODER_LOOKUP[ 37]=106;
  ENCODER_LOOKUP[ 53]=107;
  ENCODER_LOOKUP[ 61]=108;
  ENCODER_LOOKUP[ 60]=109;
  ENCODER_LOOKUP[188]=110;
  ENCODER_LOOKUP[190]=111;
  ENCODER_LOOKUP[254]=112;
  ENCODER_LOOKUP[126]=113;
  ENCODER_LOOKUP[124]=114;
  ENCODER_LOOKUP[116]=115;
  ENCODER_LOOKUP[112]=116;
  ENCODER_LOOKUP[113]=117;
  ENCODER_LOOKUP[ 49]=118;
  ENCODER_LOOKUP[ 48]=119;
  ENCODER_LOOKUP[ 16]=120;
  ENCODER_LOOKUP[144]=121;
  ENCODER_LOOKUP[146]=122;
  ENCODER_LOOKUP[154]=123;
  ENCODER_LOOKUP[158]=124;
  ENCODER_LOOKUP[ 30]=125;
  ENCODER_LOOKUP[ 94]=126;
  ENCODER_LOOKUP[ 95]=127;
  
  for(int encoder_iter=0;encoder_iter<ENCODER_COUNT;encoder_iter++)
  {
    encoder_last_position[encoder_iter]=get_encoder_sub_position(encoder_iter);
    if(encoder_last_position[encoder_iter]<0)
      encoder_last_position[encoder_iter]=0;//set to 0 on bad reading
  }
}

void loop()
{
  delay(50); //20 ms delay = ~30% load on RPi, 50 ms of delay = ~15% load on RPi
  parse_serial_input();//accept led input as a string: "0,1,1,0\n1,1,0,0\n" etc
  for(int led_iter=0;led_iter<LED_COUNT;led_iter++)
  {
    digitalWrite(LED_PINS[led_iter],led_state[led_iter]);
  }
  for(int encoder_iter=0;encoder_iter<ENCODER_COUNT;encoder_iter++)
  {
    int binary_reading=get_encoder_sub_position(encoder_iter);
    set_encoder_macro_position(encoder_iter,binary_reading);
  }
  for(int encoder_iter=0;encoder_iter<ENCODER_COUNT;encoder_iter++)
  {
    Serial.print(encoder_revolutions[encoder_iter]);
    Serial.print(",");
    Serial.print(encoder_last_position[encoder_iter]);
    Serial.print(",");
    Serial.print(encoder_bad_reading_counter[encoder_iter]);
    Serial.print(",");
  }
  for(int led_iter=0;led_iter<LED_COUNT;led_iter++)
  {
    boolean this_led_state=led_state[led_iter];
    Serial.print(this_led_state,DEC);
    if(led_iter!=(LED_COUNT-1))
      Serial.print(",");
  }
  Serial.println();
}

//clear the serial input buffer, store as text
int input_led_index=0;
void parse_serial_input()
{
  while(Serial.available())
  {
    char this_char=Serial.read();
    switch(this_char){
      case ',':
        input_led_index+=1;
        if(input_led_index>=LED_COUNT)
          input_led_index=LED_COUNT-1;
      break;
      case '0':
        led_state[input_led_index]=false;
      break;
      case '1':
        led_state[input_led_index]=true;
      break;
      case '\n':
        input_led_index=0;
      break;
      case 'p':
        Serial.println("p");//simple hello world ping response
      break;
      default:
      //no action on invalid value (ignore it)
      break;
    }
  }
}

//given an encoder index (0 to 1) and a reading (0 to 127)
//parse it into local variables (what it means for the revolution counter)
void set_encoder_macro_position(int encoder_index,int this_reading)
{
  int last_reading=encoder_last_position[encoder_index];
  if(this_reading<0)
  {
    encoder_bad_reading_counter[encoder_index]=encoder_bad_reading_counter[encoder_index]+1;
  }else{
    int delta_reading=this_reading-last_reading;//change in sub-position of wheel
    int delta_rotation=0;//change in the integer number of rotations of the wheel
    if(delta_reading>ENCODER_MAX_VALUE/2)//jumped from 0 to 127
      delta_rotation=-1;
    else if(delta_reading<-ENCODER_MAX_VALUE/2)//jumped from 127 to 0
      delta_rotation=1;
    encoder_last_position[encoder_index]=this_reading;
    encoder_revolutions[encoder_index]=encoder_revolutions[encoder_index]+delta_rotation;
  }
}

//get just the 0-127 raw reading of the encoder
//returns -1 on error in parsing
int get_raw_encoder_reading(int encoder_index)
{
  int encoded_reading=0;
  int val=0;//single bit reading
  for(int pin_iter=0;pin_iter<PINS_PER_ENCODER;pin_iter++)
  {
    int pin=ENCODER_PINS[encoder_index][pin_iter];
    if(pin==A6 || pin==A7) //not sure why Arduino Nano can't read these pins correctly with digitalRead, so read manually with analogRead and convert
      val=analogRead(pin)>512;
    else
      val=digitalRead(pin)==HIGH;
    encoded_reading |= val<<pin_iter;
  }
  /* //debug printout
  for(int iter=7;iter>=1;iter--)
    if(encoded_reading< (1<<iter) ) Serial.print("0");
  Serial.print(encoded_reading,BIN);//raw binary reading with leading zeros
  Serial.print("\t");
  Serial.print(binary_reading,DEC);//decoded reading
  Serial.println();*/
  return encoded_reading;
}

//map raw reading to meaningful decimal
int get_encoder_sub_position(int encoder_index)
{
  int encoded_reading=get_raw_encoder_reading(encoder_index);
  if(IS_DEBUG)
  {
    for(int iter=7;iter>=1;iter--)
      if(encoded_reading< (1<<iter) ) Serial.print("0");
    Serial.print(encoded_reading,BIN);
    Serial.print(" ");
  }
  int binary_reading=ENCODER_LOOKUP[encoded_reading];
  return binary_reading;
}
