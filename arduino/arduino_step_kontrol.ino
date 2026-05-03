#include <Stepper.h> // Step motor kütüphanesini dahil et

// --- Step Motor Ayarları ---
// 1. Motorunuzun bir tam turu (360 derece) için adım sayısını tanımlayın.
//    Örnek: 28BYJ-48 step motorlar için genellikle 2048 (tam adım) veya 4096 (yarım adım) kullanılır.
//    Örnek: NEMA 17 (1.8 derece/adım) için 200 adım (360 / 1.8 = 200).
const int STEPS_PER_REVOLUTION = 2048; // <<< MOTORUNUZA GÖRE BU DEĞERİ DEĞİŞTİRİN!

// 2. Step motor sürücünüzün Arduino'ya bağlı olduğu pinleri tanımlayın.
//    IN1 -> Arduino Pin 2
//    IN2 -> Arduino Pin 3
//    IN3 -> Arduino Pin 4
//    IN4 -> Arduino Pin 5
const int motorPin1 = 2;  // IN1 pinine bağlı Arduino pini
const int motorPin2 = 3;  // IN2 pinine bağlı Arduino pini
const int motorPin3 = 4;  // IN3 pinine bağlı Arduino pini
const int motorPin4 = 5;  // IN4 pinine bağlı Arduino pini

// Stepper kütüphanesi için bir step motor nesnesi oluşturun
// Standart pin sıralaması: (IN1, IN2, IN3, IN4)
Stepper myStepper(STEPS_PER_REVOLUTION, motorPin1, motorPin2, motorPin3, motorPin4);
// Bazı motor/sürücü kombinasyonları için (özellikle 28BYJ-48) şu sıralama gerekebilir:
// Stepper myStepper(STEPS_PER_REVOLUTION, motorPin1, motorPin3, motorPin2, motorPin4); 
// Eğer motorunuz istediğiniz yönde dönmüyorsa veya düzgün çalışmıyorsa diğer sıralamayı deneyin.


// --- Komutlara Karşılık Gelen Hedef Açılar ---
// Python'dan '0' geldiğinde -> 0 derece
// Python'dan '1' geldiğinde -> 36 derece
// ...
const int hedefAcilar[] = {
    0,   // '0' için
    36,  // '1' için
    72,  // '2' için
    108, // '3' için
    144, // '4' için
    180, // '5' için
    216, // '6' için
    252, // '7' için
    288, // '8' için
    324  // '9' için
};

long mevcutAdimlar = 0; // Motorun mevcut konumunu adım cinsinden takip et

void setup() {
  Serial.begin(9600); // Python ile aynı baud hızında seri haberleşmeyi başlat
  
  // Step motorun hızını ayarla (RPM - devir/dakika)
  // Motorunuza ve sürücünüze göre uygun bir hız seçin.
  // 28BYJ-48 için genellikle 10-15 RPM arası güvenlidir.
  myStepper.setSpeed(12); // <<< HIZI İSTERSENİZ AYARLAYIN

  Serial.println("Step Motor Kontrolu Hazir.");
  Serial.println("Arduino Pinleri: IN1=2, IN2=3, IN3=4, IN4=5");
  Serial.println("Python'dan komut bekleniyor ('0'-'9')...");
}

void loop() {
  if (Serial.available() > 0) { // Eğer seri porttan okunacak veri varsa
    char komut = Serial.read(); // Gelen karakteri oku

    Serial.print("Python'dan komut alindi: ");
    Serial.println(komut);

    int hedefAci = -1; // Geçersiz bir başlangıç değeri

    // Gelen komut '0' ile '9' arasında mı kontrol et
    if (komut >= '0' && komut <= '9') {
      int komutIndex = komut - '0'; // Karakteri ('0'->0, '1'->1 vb.) integer index'e çevir
      hedefAci = hedefAcilar[komutIndex];
    } else {
      Serial.println("Gecersiz komut! Lutfen '0' ile '9' arasinda bir karakter gonderin.");
      return; // Geçersiz komutsa fonksiyondan çık
    }

    Serial.print("Hedef Aci: ");
    Serial.print(hedefAci);
    Serial.println(" derece");

    // Hedef açıyı adım sayısına çevir
    long hedefAdimlar = map(hedefAci, 0, 360, 0, STEPS_PER_REVOLUTION);

    // Mevcut konumdan hedef konuma gitmek için gereken adım sayısı
    long adimFarki = hedefAdimlar - mevcutAdimlar;

    Serial.print("Mevcut Adimlar: ");
    Serial.println(mevcutAdimlar);
    Serial.print("Hedef Adimlar: ");
    Serial.println(hedefAdimlar);
    Serial.print("Atilacak Adim Sayisi: ");
    Serial.println(adimFarki);

    if (adimFarki != 0) {
      myStepper.step(adimFarki); // Motoru belirtilen adım kadar döndür
      mevcutAdimlar += adimFarki;   // Mevcut konumu güncelle
      Serial.println("Motor hareket ettirildi.");
    } else {
      Serial.println("Motor zaten hedef konumda.");
    }
    Serial.println("---------------------------------");
  }
}
