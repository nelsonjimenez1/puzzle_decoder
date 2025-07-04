import asyncio
import aiohttp
import random
import time

MAX_ID = 9223372036854775807
PUZZLE_URL = "http://localhost:8080/fragment?id={}"
TOTAL_REQUESTS = 500
QUIET_PERIOD_MS = 50       # time with no new index to consider puzzle stable
EXTRA_REQUESTS = 50         # number of requests launched in each prefetch round
PREFETCH_INTERVAL_MS = 50  # how often to prefetch more requests

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

async def background_prefetcher(session, fragments, max_index_seen, index_event, task_list, stop_event):
    while not stop_event.is_set():
        await asyncio.sleep(PREFETCH_INTERVAL_MS / 1000)
        new_tasks = [
            asyncio.create_task(
                fetch_and_track(session, random.randint(1, MAX_ID), fragments, max_index_seen, index_event)
            )
            for _ in range(EXTRA_REQUESTS)
        ]
        task_list.extend(new_tasks)

async def puzzle_decoder():
    fragments = {}
    max_index_seen = [0]
    index_event = asyncio.Event()
    stop_event = asyncio.Event()
    start_time = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        # Initial batch
        tasks = [
            asyncio.create_task(
                fetch_and_track(session, random.randint(1, MAX_ID), fragments, max_index_seen, index_event)
            )
            for _ in range(TOTAL_REQUESTS)
        ]

        # Start background prefetcher
        prefetch_task = asyncio.create_task(
            background_prefetcher(session, fragments, max_index_seen, index_event, tasks, stop_event)
        )

        last_checked_max_index = -1
        expected_indexes = set()

        while True:
            try:
                await asyncio.wait_for(index_event.wait(), timeout=QUIET_PERIOD_MS / 1000)
                index_event.clear()
            except asyncio.TimeoutError:
                if max_index_seen[0] != last_checked_max_index:
                    expected_indexes = set(range(max_index_seen[0] + 1))
                    last_checked_max_index = max_index_seen[0]

                if set(fragments.keys()) == expected_indexes:
                    break

        stop_event.set()
        prefetch_task.cancel()

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
