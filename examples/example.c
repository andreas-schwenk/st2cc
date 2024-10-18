// This file was generated automatically by st2cc.
// Visit github.com/andreas-schwenk/st2cc

#include <inttypes.h>
#include <stdbool.h>

#define ADDR_I0 0x1000
#define ADDR_Q0 0x2000

int main(int argc, char *argv[]) {
    uint8_t i0;
    uint8_t q0;
    bool sensor0;
    bool sensor1;
    bool sensor2;
    bool actuator0;
    bool actuator1;
    while (1) {
        i0 = *(volatile uint8_t *)ADDR_I0;
        sensor0 = i0 & 0x1;
        sensor1 = i0 & 0x2;
        sensor2 = i0 & 0x4;
        if ((sensor0 || (sensor1 && sensor2))) {
            actuator0 = true;
            actuator1 = true;
        } else {
            actuator0 = false;
            actuator1 = false;
        }
        q0 = actuator0 | (actuator1 << 1);
        *(volatile uint8_t *)ADDR_Q0 = q0;
    }
    return 0;
}
