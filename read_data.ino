#include <WiFi101.h>
float analog_input;

char ssid[] = "EEELAB";
char pass[] = "@adelaide";
int status = WL_IDLE_STATUS;
IPAddress server(129,127,225,140);
WiFiClient client;
int j,a;

struct byteInt  {
    int number;
    byte high;
    byte low;
};

struct byteInt xSend;
struct byteInt ySend;

void int2bytes(struct byteInt* number_fnc)  {
  int magnituteNumber;
  if (number_fnc->number >= 0)  {
    number_fnc->high = (number_fnc->number >> 8) & 0xFF;
    number_fnc->low = (number_fnc->number & 0xFF);
  } else {
    magnituteNumber = number_fnc->number * -1;
    number_fnc->high = (magnituteNumber >> 8) & 0xFF;
    number_fnc->high = number_fnc->high ^ 0x80;
    number_fnc->low = magnituteNumber & 0xFF;
  }
}

void setup() {
  // put your setup code here, to run once:
  pinMode(A1, INPUT);
  Serial.begin(115200);
  Serial.println("Connecting to wifi.");
  while (status != WL_CONNECTED) {
    Serial.println("Can't connect to wifi, try again.");
    status = WiFi.begin(ssid, pass);
  }

  delay(5000);

  Serial.println("Connecting to server.");
  j = client.connect(server, 1234);
  while (j != 1)  {
    Serial.println("Can't connect to server, try again.");
    j = client.connect(server, 1234);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  if (client.available()) {
//    Serial.print("Received from client: ");
//    Serial.println(a);
    
    a = client.read();
    if (a == 1){
      analog_input = analogRead(A1);
      Serial.print("Here's what I got: ");
      Serial.println(analog_input);
    
      xSend.number = analog_input;
      int2bytes(&xSend);
//      Serial.print("High byte: ");
//      Serial.println(xSend.high);
//      Serial.print("Low byte: ");
//      Serial.println(xSend.low);
//      Serial.println();
      client.write((byte)xSend.high);
      client.write((byte)xSend.low); 
      client.write((byte)xSend.high);
      client.write((byte)xSend.low); 
    }
  }
}
