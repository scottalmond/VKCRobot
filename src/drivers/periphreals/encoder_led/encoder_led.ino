
const int ENCODER_COUNT=2;
const int PINS_PER_ENCODER=8;
const int LED_COUNT=4;

//pin assignments
// MePed Arduino AtMega328 Nano pinout: http://www.meped.io/sites/default/files/inline-images/mePed%20PCB%20v1.3%20Labels%2C%20500px.jpg
// EAW0J-C24-AE0128L absolute encoder: https://www.mouser.com/datasheet/2/54/ce-777357.pdf
//encoder A pin 1 to S0 on mePed
//encoder B pin 1 to A7 on mePed
const int ENCODER_PINS[ENCODER_COUNT][PINS_PER_ENCODER]={
  /*LSB*/{2,3,4,5,6,7,8,9},/*MSB*/
  /*LSB*/{A7,A6,A5,A4,A3,A2,A1,A0}/*MSB*/
};
const int LED_PINS[LED_COUNT]={10,11,12,13};

const int GRAY_CODE_LENGTH=256;//256;
int ENCODER_LOOKUP[GRAY_CODE_LENGTH];

void setup()
{
  //init pins with ~20k ohm pull-ups
  for(int encoder_iter=0;encoder_iter<ENCODER_COUNT;encoder_iter++)
  {
    for(int pin_iter=0;pin_iter<PINS_PER_ENCODER;pin_iter++)
    {
      int pin=ENCODER_PINS[encoder_iter][pin_iter];
      //if(pin==A7)
      //  pinMode(pin,INPUT);
      //else
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
  /*for(int gray_code_value=0;gray_code_value<GRAY_CODE_LENGTH;gray_code_value++)
  {
    int binary_code=0;
    int gray_code=0;
    int prev_msb=0;
    int conversion=0;
    int bit_mask=0;
    // http://electronicstutemaster.blogspot.com/2012/06/simple-method-for-converson-of-gray.html
    for(int bit_index=7;bit_index>=0;bit_index--)
    {
      prev_msb=prev_msb>>1;
      bit_mask=1<<bit_index;
      conversion=( gray_code_value & bit_mask ) ^ prev_msb;
      binary_code |= conversion;
      prev_msb=conversion;
    }
    //Serial.print(gray_code_value,DEC);
    Serial.print(gray_code_value,BIN);
    Serial.print("\t");
    //Serial.println(binary_code,DEC);
    Serial.print(binary_code,BIN);
    Serial.print("\t");
    Serial.print(gray_code_value,DEC);
    Serial.print("\t");
    Serial.print(binary_code,DEC);
    Serial.println();
  }*/
  for(int iter=0;iter<GRAY_CODE_LENGTH;iter++)
    ENCODER_LOOKUP[iter]=-1;//iunvalid value at unspecified index
  
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
}

boolean is_high=false;
void loop()
{
  digitalWrite(13,is_high);
  is_high=!is_high;
  delay(1000);
  //ENCODER_COUNT
  boolean val=0;
  for(int encoder_iter=0;encoder_iter<1;encoder_iter++)
  {
    int encoded_reading=0;
    for(int pin_iter=0;pin_iter<PINS_PER_ENCODER;pin_iter++)
    {
      int pin=ENCODER_PINS[encoder_iter][pin_iter];
      if(pin==A6 || pin==A7) //not sure why Arduino Nano can't read these pins correctly with digitalRead, so read manually with analogRead and convert
        val=analogRead(pin)>512;
      else
        val=digitalRead(pin)==HIGH;
      encoded_reading |= val<<pin_iter;
      //if(val) Serial.print("1");
      //else Serial.print("0");
    }
    //if(encoder_iter==0) Serial.print(" ");
    //else Serial.println();
    int binary_reading=ENCODER_LOOKUP[encoded_reading];
    for(int iter=7;iter>=1;iter--)
      if(encoded_reading< (1<<iter) ) Serial.print("0");
    Serial.print(encoded_reading,BIN);
    Serial.print("\t");
    Serial.print(binary_reading,DEC);
    /*Serial.print("\t");
    Serial.print(analogRead(A7),DEC);
    Serial.print("\t");
    Serial.print(analogRead(A5),DEC);
    Serial.print("\t");
    Serial.print(analogRead(A0),DEC);*/
    Serial.println();
  }
}
