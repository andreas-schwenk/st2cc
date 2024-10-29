// This file was generated automatically by st2cc.
// Visit github.com/andreas-schwenk/st2cc

#include <inttypes.h>

int factorial(int num) {
    if ((num <= 1)) {
        factorial = 1;
    } else {
        factorial = (num * factorial((num - 1)));
    }
}
#define ADDR_I0 0x1000
#define ADDR_Q0 0x2000

int main(int argc, char *argv[]) {
    uint16_t I0;
    uint16_t Q0;
    int n;
    int result;
    while (1) {
        i0 = *(volatile uint16_t *)ADDR_I0;
        n = i0;
        result = factorial(n);
        q0 = result;
        *(volatile uint16_t *)ADDR_Q0 = q0;
    }
    return 0;
}
