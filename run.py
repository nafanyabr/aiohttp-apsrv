import argparse
import asyncio
import json
import jsons
from aiohttp import web
from aptasks import APTask, APTaskManager
from datetime import datetime, timezone


async def bg_worker(app: web.Application, name) -> None:
    while True:

        task_id = await app["aptask_manager"].q.get()
        app["aptask_manager"].tasks[task_id].status = "IN PROGRESS"
        app["aptask_manager"].tasks[task_id].date_start = datetime.now(timezone.utc)

        for n in range(app["aptask_manager"].tasks[task_id].count - 1):
            app["aptask_manager"].tasks[task_id].calc()
            await asyncio.sleep(app["aptask_manager"].tasks[task_id].interval)

        app["aptask_manager"].taskdone(task_id)


async def get_tasks_handler(request: web.Request):
    current_state = []
    for k, v in request.app["aptask_manager"].tasks.items():
        current_state.append(v.json)
    return web.json_response(current_state)


async def post_tasks_handler(request: web.Request):
    try:
        data = await request.json()
        count = int(data["count"])
        delta = float(data["delta"])
        start = float(data["start"])
        interval = float(data["interval"])

        if count > 0:
            if interval >= 0:
                uid = await request.app["aptask_manager"].addtask(
                    count, delta, start, interval
                )
                response_obj = {"status": "success", "task_id": str(uid)}
                return web.json_response(text=json.dumps(response_obj))
            else:
                response_obj = {
                    "status": "failed",
                    "reason": "Parameter 'Interval' must have value >= 0",
                }
                return web.json_response(text=json.dumps(response_obj), status=500)
        else:
            response_obj = {
                "status": "failed",
                "reason": "Parameter 'Count' have value > 0",
            }
            return web.json_response(text=json.dumps(response_obj), status=500)
    except Exception as e:
        response_obj = {"status": "failed", "reason": str(e)}
        return web.json_response(text=json.dumps(response_obj), status=500)


async def task_monitoring(app: web.Application) -> None:
    while True:
        await asyncio.sleep(1)
        if app["aptask_manager"].tasks:
            print("---")
            print("Current tasks queue: ")
            for k, v in app["aptask_manager"].tasks.items():
                print(v)
        else:
            print("No tasks in queue")


async def start_background_tasks(app: web.Application) -> None:
    print(f"starting application with {app['workers_count']} workers...")
    for i in range(app["workers_count"]):
        app["workers"].append(app.loop.create_task(bg_worker(app, f"w{i+1}")))
    if app["monitoring_status"]:
        print("starting monitoring task...")
        app["monitor"] = app.loop.create_task(task_monitoring(app))


async def on_shutdown(app: web.Application) -> None:
    print("shutdown workers...")
    for worker in app["workers"]:
        worker.cancel()
    if app["monitoring_status"]:
        print("shutdown monitoring task...")
        app["monitor"].cancel()


def init(workers_count: int = 3, monitoring_status: bool = False) -> web.Application:
    app = web.Application()
    app["workers_count"] = workers_count
    app["monitoring_status"] = monitoring_status
    app["workers"] = []
    app["aptask_manager"] = APTaskManager(asyncio.Queue(), dict())
    app.router.add_get("/tasks", get_tasks_handler)
    app.router.add_post("/tasks", post_tasks_handler)

    app.on_startup.append(start_background_tasks)
    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-w",
        "--workers",
        help="Setup workers count for async tasks (default and minimum workers = 3)",
        default=3,
        type=int,
    )
    parser.add_argument(
        "-m",
        "--monitor",
        help="Start monitoring tasks queue in cli every 1 second",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()

    if args.workers and args.workers >= 3:
        web.run_app(init(args.workers, args.monitor))
