#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define WINDOW_SIZE 200

// --- 1D KALMAN FILTRESI (Gürültü Azaltma İçin) ---
typedef struct {
    double q; // Süreç gürültüsü (Process noise)
    double r; // Ölçüm gürültüsü (Measurement noise)
    double x; // Tahmin edilen değer (Estimated value)
    double p; // Tahmin hata varyansı (Estimation error covariance)
    double k; // Kalman kazancı (Kalman gain)
} KalmanFilter1D;

void kalman_init(KalmanFilter1D *kf, double q, double r, double p, double initial_value) {
    kf->q = q; kf->r = r; kf->p = p; kf->x = initial_value;
}

double kalman_update(KalmanFilter1D *kf, double measurement) {
    kf->p = kf->p + kf->q; // Tahmin
    kf->k = kf->p / (kf->p + kf->r); // Kazanç
    kf->x = kf->x + kf->k * (measurement - kf->x); // Güncelleme
    kf->p = (1 - kf->k) * kf->p;
    return kf->x;
}
// ------------------------------------------------

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
    if (argc < 3 || argc > 4) {
        fprintf(stderr, "Usage: %s <Accelerometer.csv> <Gyroscope.csv> [--use-kalman]\n", argv[0]);
        return 1;
    }

    int use_kalman = 0;
    if (argc == 4 && strcmp(argv[3], "--use-kalman") == 0) {
        use_kalman = 1;
        fprintf(stderr, "INFO: Kalman Filter is ENABLED for noise reduction.\n");
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

    KalmanFilter1D kf_acc_y;
    KalmanFilter1D kf_gyr_x;
    if (use_kalman) {
        kalman_init(&kf_acc_y, 0.01, 0.1, 1.0, 0.0);
        kalman_init(&kf_gyr_x, 0.01, 0.1, 1.0, 0.0);
    }

    double acc_y[WINDOW_SIZE];
    double gyr_x[WINDOW_SIZE];
    double times[WINDOW_SIZE];
    int count = 0;
    
    // PERFORMANS METRIKLERI
    int total_seconds = 0;
    int waiting_seconds = 0;
    int working_seconds = 0;
    int sweeping_seconds = 0;

    int total_steps = 0;
    int sweeping_steps = 0;
    int swing_count = 0;

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

        if (use_kalman) {
            a_y = kalman_update(&kf_acc_y, a_y);
            g_x = kalman_update(&kf_gyr_x, g_x);
        }

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
            
            // --- SURE HESAPLAMALARI ---
            total_seconds += 2;
            if (state == 0) {
                waiting_seconds += 2;
            } else {
                working_seconds += 2;
            }
            
            if (state == 2 || state == 3) {
                sweeping_seconds += 2;
            }
            
            // --- MESAFE HESAPLAMALARI (ADIM SAYIMI) ---
            if (state == 1 || state == 3) {
                double mean_y = 0;
                for(int i=0; i<WINDOW_SIZE; i++) mean_y += acc_y[i];
                mean_y /= WINDOW_SIZE;
                
                int steps_in_window = 0;
                for(int i = 1; i < WINDOW_SIZE - 1; i++) {
                    if (acc_y[i] > acc_y[i-1] && acc_y[i] > acc_y[i+1]) {
                        if (acc_y[i] > mean_y + 0.5) {
                            steps_in_window++;
                            i += 20; 
                        }
                    }
                }
                total_steps += steps_in_window;
                if (state == 3) {
                    sweeping_steps += steps_in_window;
                }
            }
            
            // --- SUPURME HAREKETI SAYISI (SALINIM/FIRCA DARBESI) ---
            if (state == 2 || state == 3) {
                double mean_gx = 0;
                for(int i=0; i<WINDOW_SIZE; i++) mean_gx += gyr_x[i];
                mean_gx /= WINDOW_SIZE;
                
                for(int i = 1; i < WINDOW_SIZE - 1; i++) {
                    // Pozitif pikleri sayarak tam turlari buluyoruz
                    if (gyr_x[i] > gyr_x[i-1] && gyr_x[i] > gyr_x[i+1]) {
                        if (gyr_x[i] > mean_gx + 1.5) { // 1.5 rad/s esik degeri
                            swing_count++;
                            i += 30; // 100Hz'de ayni piki 0.3 sn icinde tekrar sayma
                        }
                    }
                }
            }
            
            // CSV Ciktisi
            for (int i = 0; i < WINDOW_SIZE; i++) {
                printf("%f,%d\n", times[i], state);
            }
            count = 0;
        }
    }
    
    // PERFORMANS RAPORU YAZDIRMA
    double total_distance = total_steps * 0.7; // Ortalama 0.7m adim
    double cleaning_distance = sweeping_steps * 0.7;

    fprintf(stderr, "===============================================\n");
    fprintf(stderr, "   GUNLUK / HAFTALIK PERFORMANS RAPORU\n");
    fprintf(stderr, "===============================================\n");
    fprintf(stderr, "1. Toplam Kat Edilen Mesafe : %.2f metre\n", total_distance);
    fprintf(stderr, "2. Gercek Temizlik Mesafesi : %.2f metre\n", cleaning_distance);
    fprintf(stderr, "3. Calisma (Aktif) Suresi   : %d saniye\n", working_seconds);
    fprintf(stderr, "4. Bekleme (Bosta) Suresi   : %d saniye\n", waiting_seconds);
    fprintf(stderr, "5. Toplam Supurme Hareketi  : %d salinim\n", swing_count);
    fprintf(stderr, "-----------------------------------------------\n");
    fprintf(stderr, "* Analiz Edilen Toplam Sure : %d saniye\n", total_seconds);
    fprintf(stderr, "===============================================\n\n");

    fclose(acc_file);
    fclose(gyr_file);
    return 0;
}
