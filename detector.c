#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define WINDOW_SIZE 200

// Function to calculate variance
double calculate_variance(double data[], int n) {
    if (n == 0) return 0.0;
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        sum += data[i];
    }
    double mean = sum / n;
    
    double variance = 0.0;
    for (int i = 0; i < n; i++) {
        variance += (data[i] - mean) * (data[i] - mean);
    }
    return variance / n;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <Accelerometer.csv> <Gyroscope.csv>\n", argv[0]);
        return 1;
    }

    FILE *acc_file = fopen(argv[1], "r");
    FILE *gyr_file = fopen(argv[2], "r");

    if (!acc_file || !gyr_file) {
        fprintf(stderr, "Error opening files.\n");
        return 1;
    }

    char line[256];
    // Skip headers
    fgets(line, sizeof(line), acc_file);
    fgets(line, sizeof(line), gyr_file);

    double acc_y[WINDOW_SIZE];
    double gyr_x[WINDOW_SIZE];
    double times[WINDOW_SIZE];
    int count = 0;
    
    // PERFORMANS METRIKLERI ICIN DEGISKENLER
    int total_sweeping_seconds = 0;
    int total_sweeping_steps = 0;

    printf("time,state\n");

    while (1) {
        char acc_line[256];
        char gyr_line[256];

        if (!fgets(acc_line, sizeof(acc_line), acc_file) || !fgets(gyr_line, sizeof(gyr_line), gyr_file)) {
            break; // End of file
        }

        // Parse Accelerometer.csv: time,seconds_elapsed,z,y,x
        double a_time, a_sec, a_z, a_y, a_x;
        sscanf(acc_line, "%lf,%lf,%lf,%lf,%lf", &a_time, &a_sec, &a_z, &a_y, &a_x);

        // Parse Gyroscope.csv: time,seconds_elapsed,z,y,x
        double g_time, g_sec, g_z, g_y, g_x;
        sscanf(gyr_line, "%lf,%lf,%lf,%lf,%lf", &g_time, &g_sec, &g_z, &g_y, &g_x);

        acc_y[count] = a_y;
        gyr_x[count] = g_x;
        times[count] = a_sec;
        count++;

        if (count == WINDOW_SIZE) {
            double var_acc_y = calculate_variance(acc_y, WINDOW_SIZE);
            double var_gyr_x = calculate_variance(gyr_x, WINDOW_SIZE);

            int state = 0;
            // 0: Durma & Supurmeme
            // 1: Yurume & Supurmeme
            // 2: Durma & Supurme
            // 3: Yurume & Supurme
            
            if (var_gyr_x > 1.5) { // Sweeping
                if (var_acc_y > 0.3) {
                    state = 3; // Yurume & Supurme
                } else {
                    state = 2; // Durma & Supurme
                }
            } else { // Not Sweeping
                if (var_acc_y > 0.1) {
                    state = 1; // Yurume & Supurmeme
                } else {
                    state = 0; // Durma & Supurmeme
                }
            }
            
            // 1. GERCEK SUPURME SURESI HESAPLAMA
            // Eger state 2 veya 3 ise, o 2 saniyelik pencerede supurme yapilmistir.
            if (state == 2 || state == 3) {
                total_sweeping_seconds += 2; // Pencere boyutu 2 saniye
            }
            
            // 3. GERCEK TEMIZLIK MESAFESI HESAPLAMA (Adim sayimi)
            // Sadece Yürüme & Süpürme durumundaysa (state == 3) adimlari sayiyoruz.
            if (state == 3) {
                // Pencere icindeki ivme ortalamasi
                double mean_y = 0;
                for(int i=0; i<WINDOW_SIZE; i++) mean_y += acc_y[i];
                mean_y /= WINDOW_SIZE;
                
                // Basit Peak Detection (Tepe Noktasi Bulma)
                for(int i = 1; i < WINDOW_SIZE - 1; i++) {
                    if (acc_y[i] > acc_y[i-1] && acc_y[i] > acc_y[i+1]) {
                        // Tepe noktasi ortalamadan belirgin sekilde (ornek: 0.5) yuksekse, adim atilmistir
                        if (acc_y[i] > mean_y + 0.5) {
                            total_sweeping_steps++;
                            i += 20; // 100Hz'de ayni adimi tekrar saymamak icin ~0.2 saniye atla
                        }
                    }
                }
            }
            
            // CSV Ciktisi (Grafikler icin)
            for (int i = 0; i < WINDOW_SIZE; i++) {
                printf("%f,%d\n", times[i], state);
            }
            count = 0;
        }
    }
    
    // Dosya okumasi bittikten sonra, istatistikleri terminale yazdir (stderr kullanarak, ana CSV ciktisini bozmamak icin)
    double distance = total_sweeping_steps * 0.7; // Ortalama bir adim boyu 0.7 metre kabul edilirse
    fprintf(stderr, "===============================================\n");
    fprintf(stderr, "VERI SETI ANALIZ RAPORU (%s)\n", argv[1]);
    fprintf(stderr, "-----------------------------------------------\n");
    fprintf(stderr, "1. Toplam Aktif Supurme Suresi : %d saniye\n", total_sweeping_seconds);
    fprintf(stderr, "3. Gercek Temizlik Mesafesi    : %.2f metre (%d adim)\n", distance, total_sweeping_steps);
    fprintf(stderr, "===============================================\n\n");

    fclose(acc_file);
    fclose(gyr_file);
    return 0;
}
