#include <iostream>
#include <time.h>

#define TICKS_PER_SECOND 10000000LL
#define EPOCH_DIFFERENCE 11644473600LL

int main()
{
    time_t time = 1230768000.0;
    auto ticks = (static_cast<long long>(time) + EPOCH_DIFFERENCE) * TICKS_PER_SECOND;
    std::cout << "ft.dwHighDateTime=" << static_cast<uint32_t>(ticks >> 32) << std::endl;
    std::cout << "ft.dwLowDateTime=" << static_cast<uint32_t>(ticks) << std::endl;
    return 0;
}
