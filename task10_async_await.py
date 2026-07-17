"""Task 10: sequential coroutine execution with async and await."""

import asyncio


async def drive_signal():
    signal = 0
    print(f"signal={signal}")
    await asyncio.sleep(0.02)
    signal = 1
    print(f"signal={signal}")
    await asyncio.sleep(0.03)
    signal = 0
    print(f"signal={signal}")
    return signal


async def main():
    final_value = await drive_signal()
    print(f"final signal={final_value}")


if __name__ == "__main__":
    asyncio.run(main())
