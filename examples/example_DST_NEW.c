#include <inttypes.h>
#include <stdbool.h>

#define ADDR_I0 1000
#define ADDR_Q0 2000

int main(int argc, char *argv[]) {
    uint8_t i0;
    uint8_t q0;
    bool start_button_a;
    bool start_button_b;
    bool motor_output_a;
    bool motor_output_b;
    while (1) {
        i0 = *(volatile uint8_t *)ADDR_I0;
        start_button_a = i0 & 0x1;
        start_button_b = i0 & 0x3;
        if (start_button_a || start_button_b) {
            motor_output_a = true;
        } else {
            motor_output_b = false;
        }
        q0 = (motor_output_b << 1) | motor_output_a;
        *(volatile uint8_t *)ADDR_Q0 = q0;
    }
    return 0;
}
