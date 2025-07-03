import asyncio
import aiohttp
import random
import time

PUZZLE_URL = "http://localhost:8080/fragment?id={}"
TOTAL_REQUESTS = 500
QUIET_PERIOD_MS = 100  # time with no new index to consider puzzle stable
EXTRA_REQUESTS = 100   # new tasks to launch when all current ones are done but puzzle incomplete

async def fetch_and_track(session, id_, fragments, max_index_seen, index_event):
    try:
        async with session.get(PUZZLE_URL.format(id_)) as resp:
            if resp.status != 200:
                return
            data = await resp.json()
    except:
        return

    idx = data["index"]
    text = data["text"]

    if idx not in fragments:
        fragments[idx] = text
        if idx > max_index_seen[0]:
            max_index_seen[0] = idx
        index_event.set()

async def puzzle_decoder():
    fragments = {}
    max_index_seen = [0]
    index_event = asyncio.Event()
    start_time = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(
                fetch_and_track(session, random.randint(1, 10**9), fragments, max_index_seen, index_event)
            )
            for _ in range(TOTAL_REQUESTS)
        ]

        while True:
            try:
                await asyncio.wait_for(index_event.wait(), timeout=QUIET_PERIOD_MS / 1000)
                index_event.clear()
            except asyncio.TimeoutError:
                expected_indexes = set(range(max_index_seen[0] + 1))
                if set(fragments.keys()) == expected_indexes:
                    break  # puzzle is complete
                # if all tasks are done, launch more
                if all(task.done() for task in tasks):
                    print(f"⚠️ Incomplete puzzle — launching {EXTRA_REQUESTS} additional tasks...")
                    new_tasks = [
                        asyncio.create_task(
                            fetch_and_track(session, random.randint(1, 10**9), fragments, max_index_seen, index_event)
                        )
                        for _ in range(EXTRA_REQUESTS)
                    ]
                    tasks.extend(new_tasks)
                # else: continue waiting

        # Cancel any remaining tasks
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000

    ordered_fragments = [fragments[i] for i in sorted(fragments)]
    message = ''.join(ordered_fragments)

    print(f"\n✅ Puzzle complete with {len(fragments)} fragments.")
    print(f"🔍 Message: {message}")
    print("\n🧪 Artificially spaced message:")
    print(' '.join(ordered_fragments))
    print(f"\n⏱️ Total time: {elapsed_ms:.2f} ms")

if __name__ == "__main__":
    asyncio.run(puzzle_decoder())
