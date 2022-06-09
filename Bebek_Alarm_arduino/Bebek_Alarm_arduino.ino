#include <SoftwareSerial.h>

#define ses_girisi A0 // Ses sensörü Envelope -> A0
#define pir_girisi 5  // PIR sensörü OUT -> D5
#define TX 10         // Bluetooth TX -> 10
#define RX 11         // Bluetooth RX -> 11

SoftwareSerial bluetooth(TX, RX); // Bluetooth haberleşme ayarı

int sistem_durumu = HIGH;  // Sensör kontrolü
int ses_degeri;           // Ses sensörü giriş değeri
int hareket_degeri;       // PIR sensörü giriş değeri
int goruntu_degeri;       // Görüntü işleme giriş değeri
int hareket_durumu = LOW;
int ses_durumu = LOW;
int goruntu_durumu = LOW;

/*
   alarm(0); // Haberleşme başarıyla sağlandı.
   alarm(5); // Bebek uyandı.
   sistem_durumu = HIGH; // Sistem aktif, sensörleri kontrol et
   sistem_durumu = 2; // Sistemi başlat/devam ettir
   sistem_durumu = 3; // Sistemi 10 saniye ertele
   sistem_durumu = 4; // Görüntüyü sıfırla
   Serial.println(0); // Görüntüyü durdur
   Serial.println(1); // Görüntüyü devam ettir
   Serial.println(2); // Görüntüyü sıfırla
*/

void setup() {
  Serial.begin(9600);
  bluetooth.begin(9600);
  pinMode(ses_girisi, INPUT);     // Ses sensörü giriş
  pinMode(pir_girisi, INPUT); // PIR sensörü giriş
}

void loop() {

  if ( sistem_durumu == HIGH ) { // Sistem aktif, sensörleri kontrol et
    //ses_algilama();
    hareket_algilama();
    //goruntu_algilama();
    alarm_kontrol();
  }
  else if ( sistem_durumu == 2 ) { // Sistemi başlat/devam ettir
    alarm(0); // Haberleşme başarıyla sağlandı.
    sensor_reset();
    sistem_durumu = HIGH;
  }
  else if ( sistem_durumu == 3 ) { // Sistemi 10 saniye ertele
    delay(10000);
    alarm(0); // Haberleşme başarıyla sağlandı.
    sensor_reset();
    sistem_durumu = HIGH;
  }
  else if ( sistem_durumu == 4 ) { // Görüntüyü sıfırla
    Serial.println(2); // Görüntüyü sıfırla
    sistem_durumu = HIGH;
    sensor_reset();
    delay(200);
  }

  telefon_kontrol(); // Telefondan gelen yönergeleri dinle

  delay(1000);
}

void alarm_kontrol() {
  if ( ses_durumu == HIGH || hareket_durumu == HIGH || goruntu_durumu == HIGH ) {
    alarm(5); // Bebek uyandı.
    sensor_reset();
  }
}

void ses_algilama() {
  ses_degeri = analogRead(ses_girisi);

  if ( ses_degeri > 120 && ses_degeri <= 500 ) {
    ses_durumu = HIGH;
  }
}

void hareket_algilama() {
  hareket_degeri = digitalRead(pir_girisi);
  if ( hareket_degeri == HIGH ) {
    hareket_durumu = HIGH;
  }
}

void goruntu_algilama() {
  if ( Serial.available() ) {
    goruntu_degeri = Serial.parseInt();

    if ( goruntu_degeri == HIGH ) {
      goruntu_durumu = HIGH;
    }
  }
}

void alarm(int alarm_durumu) {
  bluetooth.println(alarm_durumu);
}

void telefon_kontrol() {
  if ( bluetooth.available() ) {
    sistem_durumu = bluetooth.parseInt();

    if ( sistem_durumu == 0 ) {
      Serial.println(0); // Görüntüyü durdur
      sensor_reset();
    }
    else if ( sistem_durumu == 2 ) {
      Serial.println(1); // Görüntüyü devam ettir
      sensor_reset();
      delay(200);
      Serial.println(2); // Görüntüyü sıfırla
    }
  }
}

void sensor_reset() {
  hareket_durumu = LOW;
  ses_durumu = LOW;
  goruntu_durumu = LOW;
}
