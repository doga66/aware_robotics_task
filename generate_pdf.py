from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Akilli Supurge - Sistem Tasarim Raporu', 0, 1, 'C')
        self.ln(5)

pdf = PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Use standard fonts that fpdf has built-in
pdf.set_font("helvetica", size=12)

# Text content
text_intro = """
Bu rapor, Case-1 Akilli Supurge Sistemi icin donanim, haberlesme, maliyet ve algoritmik mimariyi detaylandirmaktadir.

1. Sistem Mimarisi ve Sensor Yerlesimi
Asagidaki semada gorulecegi uzere, titresim (varyans) siddetini en optimal sekilde algilayabilmek adina, LSM6DS3 ivmeolcer sensoru supurge sapinin orta-alt bolgesine yerlestirilmistir. Butun hesaplamalar (Edge Computing) cihaz uzerindeki STM32WLE5 islemcisinde yapilarak ana sunucuya sadece sonuclar iletilir.
"""
pdf.multi_cell(0, 7, text_intro)
pdf.ln(5)

# Add image
try:
    pdf.image('mimari.png', x=15, w=180)
except Exception as e:
    pdf.cell(0, 10, 'Mimari gorseli yuklenemedi.', 0, 1)
pdf.ln(5)

text_lora = """
2. LoRaWAN Haberlesme ve Payload Yapisi
Cihaz her 30 dakikada bir sadece 12 Byte'lik sikistirilmis bir paket gonderir. Gonderilen veriler (Bekleme suresi, aktif sure, supurme sayisi, temizlik mesafesi vs.) byte array'e cevrilir. 

Asagida, STM32WLE5 uzerinde LoRaWAN MAC (LMIC vb.) kullanarak hazirlanan ornek bir gonderim (Transmission) kodu yer almaktadir:
"""
pdf.multi_cell(0, 7, text_lora)
pdf.ln(5)

# C code block
pdf.set_font("courier", size=9)
pdf.set_fill_color(240, 240, 240)
c_code = """
// 12 Byte Payload Hazirlama
uint8_t payload[12];
uint16_t dev_id = 2603;
uint8_t battery = 90; // %90
uint16_t work_time = 1420; // 1420 saniye
uint16_t wait_time = 380;
uint16_t swings = 950;
uint16_t clean_dist = 889; // 889 metre
uint8_t status_code = 0x00; // OK

// Little-endian veya Big-endian formatina gore bit-shift yapilabilir
payload[0] = (dev_id >> 8) & 0xFF; payload[1] = dev_id & 0xFF;
payload[2] = battery;
payload[3] = (work_time >> 8) & 0xFF; payload[4] = work_time & 0xFF;
payload[5] = (wait_time >> 8) & 0xFF; payload[6] = wait_time & 0xFF;
payload[7] = (swings >> 8) & 0xFF; payload[8] = swings & 0xFF;
payload[9] = (clean_dist >> 8) & 0xFF; payload[10] = clean_dist & 0xFF;
payload[11] = status_code;

// LoRaWAN Uzerinden Gonderim (LMIC kutuphanesi ornegi)
void do_send(osjob_t* j) {
    if (LMIC.opmode & OP_TXRXPEND) {
        printf("Islem beklemede, TX iptal.\\n");
    } else {
        // Port 1, Payload, Uzunluk, Onay istenmiyor (0)
        LMIC_setTxData2(1, payload, sizeof(payload), 0);
        printf("Paket kuyruga eklendi.\\n");
    }
}
"""
pdf.multi_cell(0, 5, c_code, fill=True)
pdf.ln(5)

pdf.set_font("helvetica", size=12)
text_rest = """
3. Sistem Maliyeti ve Guc
- Islemci + LoRa: STM32WLE5 (~3.50 $)
- Sensor: LSM6DS3 (~1.50 $)
- Guc: 18650 Li-Ion (~2.50 $)
- Kasa, PCB ve Diger: (~3.60 $)
- Toplam Birim Maliyet (2k Uretim): ~11.10 $

Bu guc mimarisi ile cihaz, sadece veri yolladigi saniyelerde ~120mA cekerken diger anlarda uyuyarak aylarca sarj edilmeden calisabilir.
"""
pdf.multi_cell(0, 7, text_rest)

pdf.output("Nihai_Sistem_Raporu.pdf")
print("PDF basariyla olusturuldu: Nihai_Sistem_Raporu.pdf")
