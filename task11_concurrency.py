"""Task 11: fork/join-style concurrency with asyncio tasks."""

import asyncio


async def drive_a():
    for value in (0, 1, 0):
        await asyncio.sleep(0.01)
        print(f"driver A -> {value}")
    return "A complete"


async def drive_b():
    for value in (1, 0):
        await asyncio.sleep(0.015)
        print(f"driver B -> {value}")
    return "B complete"


async def main():
    task_a = asyncio.create_task(drive_a())
    task_b = asyncio.create_task(drive_b())
    results = await asyncio.gather(task_a, task_b)
    print(f"joined tasks: {', '.join(results)}")


if __name__ == "__main__":
    asyncio.run(main())
