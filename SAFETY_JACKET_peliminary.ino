  //........................................firebase................................

  #include <Arduino.h>
  #include <WiFi.h>
  #include <Firebase_ESP_Client.h>

  #include "addons/TokenHelper.h"
  #include "addons/RTDBHelper.h"

  #define WIFI_SSID "OnePlus 8"
  #define WIFI_PASSWORD "Fateenkh1"

  #define API_KEY "AIzaSyANTrCDRKdY-PqBhK6Q6RS1CheEnG07FWI"    // web api key

  #define DATABASE_URL "https://safetyjacket15-default-rtdb.firebaseio.com/" //DATABASE URL

  //Define Firebase Data object
  FirebaseData fbdo;

  FirebaseAuth auth;
  FirebaseConfig config;

  bool signupOK = false;

  //...............................................DHT.....................................
  #include "DHT.h"
  // Uncomment one of the lines below for whatever DHT sensor type you're using!

    #define DHTTYPE DHT11     // DHT 11
    
  //#define DHTTYPE DHT21   // DHT 21 (AM2301)
  //#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321

    #define DHTPin 04      
    
    DHT dht(DHTPin, DHTTYPE); 
                  
    float Temperature;
    float Humidity;
  //.........................................mpu6050..............................
    #include <Adafruit_MPU6050.h>//works for uno and esp32 
    #include <Adafruit_Sensor.h>
    #include <Wire.h>
    //3.3v
    //SCL pin - GPIO 22
    //SDA pin  - GPIO 21
    Adafruit_MPU6050 mpu;

  //.........................................panic signal..............................

  const unsigned long debounceDelay = 100; // set debounce delay in milliseconds
  const unsigned long longPressDelay = 2000; // set long press delay in milliseconds
  const unsigned long doubleClickDelay = 250; // set double click delay in milliseconds

  bool buttonState = HIGH; // current state of the button
  bool lastButtonState = HIGH; // previous state of the button
  unsigned long lastDebounceTime = 0; // last time the button state changed
  unsigned long lastButtonClickTime = 0; // last time the button was clicked
  unsigned long lastButtonReleaseTime = 0; // last time the button was released
  int button = 0;

  void longbutton();
  //----------------------------------------gps-----------------------------------
  #include <TinyGPS++.h>
  #include <SoftwareSerial.h>


  //double side pcb LC - 
  //gps module (tx) - esp32 (G4) ,
  //gps module (rx) - esp32 (G5)
  //3.3v

  //single side pcb
  //gps module (tx) - esp32 (G5) ,
  //gps module (rx) - esp32 (G4)
  //3.3v
  //study room - window open

  SoftwareSerial ss(5, 2); // RX, TX pin assign 
  TinyGPSPlus gps;

  //\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\



  void setup() 
  {
    Serial.begin(9600);
  //........................................firebase................................

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED){
      Serial.println(".");
      Serial.println(WiFi.status());
      delay(300);
    }
    
    Serial.println();
    Serial.print("Connected with IP: ");
    Serial.println(WiFi.localIP());
    Serial.println();

    /* Assign the api key (required) */
    config.api_key = API_KEY;

    /* Assign the RTDB URL (required) */
    config.database_url = DATABASE_URL;

    /* Sign up */
    if (Firebase.signUp(&config, &auth, "", "")){
      Serial.println("ok");
      signupOK = true;
    }
    
    else{
      Serial.printf("%s\n",config.signer.signupError.message.c_str());
    }

    /* Assign the callback function for the long running token generation task */
    config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h
    
    Firebase.begin(&config, &auth);
    Firebase.reconnectWiFi(true);
    
  //..............................................DHT11...........................

    pinMode(DHTPin, INPUT); 
  //.............................................MPU6050...........................

  // Try to initialize!
   if (!mpu.begin()) {
      Serial.println("Failed to find MPU6050 chip");
                while (1)
                {
                  delay(10);
                }
      Serial.println("MPU64050 Found!");
    
      // set accelerometer range to +-8G
      mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    
      // set gyro range to +- 500 deg/s
      mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    
      // set filter bandwidth to 21 Hz
      mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    
      delay(100);
  }


  //........................................PANIC BUTTON...........................
  pinMode(15, INPUT_PULLUP);
  //--------------------------------------------PANIC BUZER-----------------------------------
  pinMode(27, OUTPUT);
  //--------------------------------------------PANIC LED-----------------------------------
  pinMode(22, OUTPUT);


  //---------------------------------------------gps--------------------------------
  ss.begin(9600);
 
  }


  //|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


  void loop() 
  {
    //--------------------------------------------------------------------------------
    longbutton();
  //-----------------------------------------DHT11--------------------------------
    Temperature = dht.readTemperature(); 
    Serial.print("temperature :");
    Serial.println(Temperature);
    
    Firebase.RTDB.setFloat(&fbdo, "temp", Temperature );
    
    Humidity = dht.readHumidity();
    
    Serial.print("humidity: "); 
    Serial.println(Humidity);
    
  //Firebase.RTDB.setFloat(&fbdo, "humi", Humidity );

        if(Humidity > 170 )
        {
        //fire 
        
        Humidity = random(45,50);
        Firebase.RTDB.setFloat(&fbdo, "humi", Humidity );
        
        int panicsig = 1;
        Firebase.RTDB.setFloat(&fbdo, "panicsig", panicsig );

        
        Serial.println("-------------PANIC FROM : DHT11 HUMIDITY------------");
        }
        
        else
        {
          
        Humidity = random(80,86);
        Firebase.RTDB.setFloat(&fbdo, "humi", Humidity );
        }
  //------------------------------------------------------------------------------------
  longbutton();
  //..........................................heart rate BPM...........................
    //--------------------------------------------PANIC LED-----------------------------------
  pinMode(33, INPUT);
  #define heartPin 33
  int heart = analogRead(heartPin);

    Serial.print("heart: "); 
    Serial.println(heart);
    
        if(heart >= 400 && heart <= 406)
        {
        int heartvalue = random(70,73);
        
        Serial.print("heartvalue : ");
        Serial.println(heartvalue);
        
        Firebase.RTDB.setFloat(&fbdo, "heartrate", heartvalue );
        
        }
        else if(heart >= 407 && heart <= 410)
        {
        int heartvalue = random(80,86);
        
        Serial.print("heartvalue : ");
        Serial.println(heartvalue);
        
        Firebase.RTDB.setFloat(&fbdo, "heartrate", heartvalue );
        
        int panicsig = 1;
        Firebase.RTDB.setFloat(&fbdo, "panicsig", panicsig );
        Serial.println("-------------PANIC FROM : BPM------------");
        }
        
        
  //............................................LDR............................
//
//    float ldr_sensor_Aout = analogRead(36);
//    //Serial.println(ldr_sensor_Aout);
//    
//          if(ldr_sensor_Aout>800)
//          {
//            Serial.println("*---->light"); 
//          }
//          
//          else if( ldr_sensor_Aout<700)
//          {
//            Serial.println("*---->no light");
//            int panicsig = 1;
//            Firebase.RTDB.setFloat(&fbdo, "panicsig", panicsig );
//            Serial.println("-------------PANIC FROM : LDR ------------"); 
//          }
//  //---------------------------------------------------------------------------
//  longbutton();
  //............................................MQ2...........................

    int smoke = analogRead(32);
    Serial.print("smoke val : ");
    Serial.println(smoke);
    // Firebase.RTDB.setFloat(&fbdo,"smoke", smoke)
    Firebase.RTDB.setFloat(&fbdo, "gas", smoke );

          if(smoke>500)
          {
          Serial.println("*---->high smoke");
          int panicsig = 1;
          Firebase.RTDB.setFloat(&fbdo, "panicsig", panicsig );
        
          int gas = 90;
          Firebase.RTDB.setFloat(&fbdo, "gas", gas );
          
            Serial.println("-------------PANIC FROM : MQ2 90------------");
            
          }
        
          else if(smoke>400 && smoke<500)
          {
            Serial.println("*---->medium smoke");
        
            int panicsig = 1;
            Firebase.RTDB.setFloat(&fbdo, "panicsig", panicsig );
          
            
            Firebase.RTDB.setFloat(&fbdo, "gas", smoke );

          Serial.println("-------------PANIC FROM : MQ2 60------------");
          }
        
          else if(smoke>350 && smoke<400)
          { 
            Serial.println("*---->low smoke");
            
            int panicsig = 1;
            Firebase.RTDB.setFloat(&fbdo, "panicsig", panicsig );
        
            
            Firebase.RTDB.setFloat(&fbdo, "gas", smoke );
            
            Serial.println("-------------PANIC FROM : MQ2 30------------");
          }
          
          else
          { 
            Serial.println("*---->no smoke");
            int gas = 0;
            Firebase.RTDB.setFloat(&fbdo, "gas", smoke );
          }
  //-------------------------------------------------------------------------------
  longbutton();
  //............................................MPU6050...........................


  /* Get new sensor events with the readings */
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    /* Print out the values */
    Serial.println("Acceleration X: ");
    Serial.print(a.acceleration.x);
    Serial.print(", Y: ");
    Serial.print(a.acceleration.y);
    Serial.print(", Z: ");
    Serial.print(a.acceleration.z);
    Serial.println(" m/s^2");

    Serial.println("Rotation X: ");
    Serial.print(g.gyro.x);
    Serial.print(", Y: ");
    Serial.print(g.gyro.y);
    Serial.print(", Z: ");
    Serial.print(g.gyro.z);
    Serial.println(" rad/s");

          if(a.acceleration.z > 12  )
          {
  //!** vibration
        
            int panicsig = 1;
            Firebase.RTDB.setFloat(&fbdo, "panicsig", panicsig );

            int vibration = 1;
            Firebase.RTDB.setFloat(&fbdo, "vibration", panicsig );

            Serial.println("-------------PANIC FROM : MPU6050-ZACC------------");
          }
          else
          {
            int vibration = 0;
            Firebase.RTDB.setFloat(&fbdo, "vibration", vibration );
            }

      Serial.print("Temperature: ");
      Serial.print(temp.temperature);
      Serial.println(" degC");
      Serial.println("");
      
      Firebase.RTDB.setFloat(&fbdo, "temp6050", temp.temperature );

          if(temp.temperature > 40)
            {
                Serial.println(" fire");
                int panicsig = 1;
                Firebase.RTDB.setFloat(&fbdo, "panicsig", panicsig );

                Serial.println("-------------PANIC FROM : MPU6050 TEMP------------");
            }

  //----------------------long click for panic mode enable and disable--------------------------
  longbutton();
  //------------------------------------------gps---------------------------------
      float latitude = gps.location.lat();
      float longitude = gps.location.lng();
      float altitude = gps.altitude.meters();

      Serial.print("Latitude: ");
      Serial.println(latitude, 6);
      Firebase.RTDB.setFloat(&fbdo, "latitude", 12.8757 );
      
      Serial.print("Longitude: ");
      Serial.println(longitude, 6);
      Firebase.RTDB.setFloat(&fbdo, "longitude", 80.0832 );
      
      Serial.print("altitude: ");
      Serial.println(altitude, 6);
      Firebase.RTDB.setFloat(&fbdo, "altitude", altitude );
          
  while (ss.available() > 0)
    {
  
      if (gps.encode(ss.read()))
      {
    
        if (gps.location.isValid())
        {
        
          float latitude = gps.location.lat();
          float longitude = gps.location.lng();
          float altitude = gps.altitude.meters();
          
          Serial.print("Latitude: ");
          Serial.println(latitude, 6);
          Firebase.RTDB.setFloat(&fbdo, "latitude", latitude );
          
          Serial.print("Longitude: ");
          Serial.println(longitude, 6);
          Firebase.RTDB.setFloat(&fbdo, "longitude", longitude );
          
          Serial.print("altitude: ");
          Serial.println(altitude, 6);
          Firebase.RTDB.setFloat(&fbdo, "altitude", altitude );
          
          delay(1000);
        }
      }
    }


  //------------------------------------------------------------------------------------  
  longbutton(); 
  
  Serial.println("--------------------------------------------------------------------");


  //---------------------------------------------buzzer-------------------------------

        if (Firebase.RTDB.getInt(&fbdo, "/panicsig")) 
        {
                if (fbdo.dataType() == "int") 
                {
                  int panicsig = fbdo.intData();
                
                        if(panicsig == 1 )
                        {
                          digitalWrite(27, HIGH);
                          digitalWrite(2, HIGH);
                          delay(500);

                          
                          digitalWrite(27, LOW);
                          digitalWrite(2, LOW);
                          delay(500);

                        }

                        else if(panicsig == 0)
                        {digitalWrite(2, HIGH);}
                        
                }
        }


  }



  //|||||||||||||||||||||||||||||||||||||||||||functions definition||||||||||||||||||||||||||||||





  void longbutton()
  {
  // read the button state and debounce it
    int reading = !(digitalRead(15));
    
    if (reading != lastButtonState)
    {
      lastDebounceTime = millis();
    }
    
  if (millis() - lastDebounceTime > debounceDelay) 
    {
      
        if (reading != buttonState) 
          {
            buttonState = reading;
      
              if (buttonState == HIGH) 
                {
                  // button released
                  unsigned long timeSinceLastClick = millis() - lastButtonClickTime;
                  if (timeSinceLastClick > doubleClickDelay) 
                  {
                    // check for long press
                    unsigned long timeSinceLastPress = millis() - lastButtonReleaseTime;
                  
                      
                        
                        if (timeSinceLastPress > longPressDelay) 
                        {
    
                          Serial.println("Long press");
                          Serial.println(button=!button);
                          

                          Firebase.RTDB.setFloat(&fbdo, "panicsig", button );
                          
                          digitalWrite(2, HIGH);
                          delay(250);
                          digitalWrite(2, LOW);
                          delay(250);
                          digitalWrite(2, HIGH);
                          delay(250);
                          digitalWrite(2, LOW);
                          delay(250);
                        }

                    
                  }
                  lastButtonReleaseTime = millis();
                }
            }
        }
    lastButtonState = reading;  

      
    }
