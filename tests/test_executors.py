import gc
import time
from asyncio import CancelledError
from datetime import datetime
from threading import Event

import pytest
import pytz
from asyncz.events.constants import JOB_ERROR, JOB_EXECUTED, JOB_MISSED
from asyncz.exceptions import MaximumInstancesError
from asyncz.executors.asyncio import AsyncIOExecutor
from asyncz.executors.base import run_coroutine_job, run_job
from asyncz.jobs import Job
from asyncz.schedulers.asyncio import AsyncIOScheduler
from asyncz.schedulers.base import BaseScheduler
from loguru import logger
from mock import MagicMock, Mock, patch


@pytest.fixture
def scheduler_mocked(timezone):
    scheduler_ = Mock(BaseScheduler, timezone=timezone)
    scheduler_.create_lock = MagicMock()
    return scheduler_


@pytest.fixture(params=["threadpool", "other"])
def executor(request, scheduler_mocked):
    if request.param == "threadpool":
        from asyncz.executors.pool import ThreadPoolExecutor

        executor = ThreadPoolExecutor()
    else:
        from asyncz.executors.pool import ProcessPoolExecutor

        executor = ProcessPoolExecutor()

    executor.start(scheduler_mocked, "dummy")
    yield executor
    executor.shutdown()


def wait_event():
    time.sleep(0.2)
    return "test"


def failure():
    raise Exception("test failure")


def success():
    return 5


def test_max_instances(scheduler_mocked, executor, create_job, freeze_time):
    events = []
    scheduler_mocked.dispatch_event = lambda event: events.append(event)
    job = create_job(fn=wait_event, max_instances=2, next_run_time=None)
    executor.send_job(job, [freeze_time.current])
    executor.send_job(job, [freeze_time.current])

    pytest.raises(MaximumInstancesError, executor.send_job, job, [freeze_time.current])
    executor.shutdown()
    assert len(events) == 2
    assert events[0].return_value == "test"
    assert events[1].return_value == "test"


@pytest.mark.parametrize(
    "event_code,fn",
    [(JOB_EXECUTED, success), (JOB_MISSED, failure), (JOB_ERROR, failure)],
    ids=["executed", "missed", "error"],
)
def test_send_job(scheduler_mocked, executor, create_job, freeze_time, timezone, event_code, fn):
    scheduler_mocked.dispatch_event = MagicMock()
    job = create_job(fn=fn, id="foo")
    job.store_alias = "test_store"
    run_time = (
        timezone.localize(datetime(1970, 1, 1))
        if event_code == JOB_MISSED
        else freeze_time.current
    )
    executor.send_job(job, [run_time])
    executor.shutdown()

    assert scheduler_mocked.dispatch_event.call_count == 1
    event = scheduler_mocked.dispatch_event.call_args[0][0]
    assert event.code == event_code
    assert event.job_id == "foo"
    assert event.store == "test_store"

    if event_code == JOB_EXECUTED:
        assert event.return_value == 5
    elif event_code == JOB_ERROR:
        assert str(event.exception) == "test failure"
        assert isinstance(event.traceback, str)


class FakeJob:
    id = "abc"
    max_instances = 1
    store_alias = "foo"


def dummy_run_job(job, store_alias, run_times, logger_name):
    raise Exception("dummy")


def test_run_job_error(monkeypatch, executor):
    """
    Tests that run_job_error is properly called. Since we use loguru, there is no need to parse the exceptions.
    """

    def run_job_error(job_id, exc, traceback):
        assert job_id == "abc"
        exc_traceback[:] = [exc, traceback]
        event.set()

    event = Event()
    exc_traceback = [None, None]
    monkeypatch.setattr("asyncz.executors.base.run_job", dummy_run_job)
    monkeypatch.setattr("asyncz.executors.pool.run_job", dummy_run_job)
    monkeypatch.setattr(executor, "run_job_error", run_job_error)
    executor.send_job(FakeJob(), [])

    event.wait(5)
    assert exc_traceback[0] == None
    assert exc_traceback[1] == None


def test_run_job_memory_leak():
    class FooBar:
        pass

    def fn():
        foo = FooBar()  # noqa: F841
        raise Exception("dummy")

    fake_job = Mock(Job, id="dummy", fn=fn, args=(), kwargs={}, mistrigger_grace_time=1)
    with patch("loguru.logger"):
        for _ in range(5):
            run_job(fake_job, "foo", [datetime.now(pytz.UTC)], logger)

    foos = [x for x in gc.get_objects() if type(x) is FooBar]
    assert len(foos) == 0


@pytest.fixture
def asyncio_scheduler(event_loop):
    scheduler = AsyncIOScheduler(event_loop=event_loop)
    scheduler.start(paused=True)
    yield scheduler
    scheduler.shutdown(False)


@pytest.fixture
def asyncio_executor(asyncio_scheduler):
    executor = AsyncIOExecutor()
    executor.start(asyncio_scheduler, "default")
    yield executor
    executor.shutdown()


async def waiter(sleep, exception):
    await sleep(0.1)
    if exception:
        raise Exception("dummy error")
    else:
        return True


@pytest.mark.parametrize("exception", [False, True])
@pytest.mark.asyncio
async def test_run_coroutine_job(asyncio_scheduler, asyncio_executor, exception):
    from asyncio import Future, sleep

    future = Future()
    job = asyncio_scheduler.add_job(waiter, "interval", seconds=1, args=[sleep, exception])
    asyncio_executor.run_job_success = lambda job_id, events: future.set_result(events)
    asyncio_executor.run_job_error = lambda job_id, exc, tb: future.set_exception(exc)
    asyncio_executor.send_job(job, [datetime.now(pytz.utc)])
    events = await future
    assert len(events) == 1

    if exception:
        assert str(events[0].exception) == "dummy error"
    else:
        assert events[0].return_value is True


@pytest.mark.asyncio
async def test_asyncio_executor_shutdown(asyncio_scheduler, asyncio_executor):
    """Test that the AsyncIO executor cancels its pending tasks on shutdown."""
    from asyncio import sleep

    job = asyncio_scheduler.add_job(waiter, "interval", seconds=1, args=[sleep, None])
    asyncio_executor.send_job(job, [datetime.now(pytz.utc)])
    futures = asyncio_executor.pending_futures.copy()
    assert len(futures) == 1

    asyncio_executor.shutdown()
    with pytest.raises(CancelledError):
        await futures.pop()


@pytest.mark.asyncio
async def test_run_job_memory_leak():
    class FooBar:
        pass

    async def fn():
        foo = FooBar()  # noqa: F841
        raise Exception("dummy")

    fake_job = Mock(Job, id="dummy", fn=fn, args=(), kwargs={}, mistrigger_grace_time=1)

    with patch("loguru.logger"):
        for _ in range(5):
            await run_coroutine_job(fake_job, "foo", [datetime.now(pytz.utc)], logger)

    foos = [x for x in gc.get_objects() if type(x) is FooBar]
    assert len(foos) == 0
