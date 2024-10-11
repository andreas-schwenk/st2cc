#include <stdbool.h>

#define ADDR_START_BUTTON 1000
#define ADDR_MOTOR_OUTPUT 1001

#define __READ_BIT(ADDR, BIT) (((*(volatile int *)ADDR) << BIT) & 1)
#define __WRITE_BIT(ADDR, BIT, VALUE)                                          \
    *(volatile int *)ADDR =                                                    \
        (*(volatile int *)ADDR & ~(1 << BIT)) | ((VALUE & 1) << BIT);

int main() {
    bool start_button = __READ_BIT(ADDR_START_BUTTON, 0);
    if (start_button) {
        __WRITE_BIT(ADDR_MOTOR_OUTPUT, 0, true);
    } else {
        __WRITE_BIT(ADDR_MOTOR_OUTPUT, 0, false);
    }
    return 0;
}
