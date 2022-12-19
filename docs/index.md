# Asyncz

<p align="center">
  <a href="https://asyncz.tarsil.io"><img src="https://res.cloudinary.com/dymmond/image/upload/v1671461421/asyncz/asyncz-bg_bapqg1.png" alt='Asyncz'></a>
</p>

<p align="center">
    <em>🚀 The scheduler that simply works. 🚀</em>
</p>

<p align="center">
<a href="https://github.com/tarsil/asyncz/workflows/Test%20Suite/badge.svg?event=push&branch=main" target="_blank">
    <img src="https://github.com/tarsil/asyncz/workflows/Test%20Suite/badge.svg?event=push&branch=main" alt="Test Suite">
</a>

<a href="https://pypi.org/project/asyncz" target="_blank">
    <img src="https://img.shields.io/pypi/v/asyncz?color=%2334D058&label=pypi%20package" alt="Package version">
</a>

<a href="https://pypi.org/project/asyncz" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/asyncz.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**Documentation**: [https://asyncz.tarsil.io](https://asyncz.tarsil.io) 📚

**Source Code**: [https://github.com/tarsil/asyncz](https://github.com/tarsil/asyncz)

---

Asyncz is a scheduler for any ASGI application that needs to have those complicated scheduled operations with the
best of what pydantic can offer.

## Motivation

Nowadays using async frameworks with python is somewhat common and becoming even more mainstream. A lot of applications
usually need a complex stack of technologies to fullfil their needs and directly or indirectly, a scheduler.

There are great frameworks out there that do the job extremely well, the best example is APScheduler, which is where
Asyncz is inspired by.

To be even more honest, Asyncz is a revamp of APScheduler. Without the APScheduler there is no Asyncz, so much that
even the APScheduler tests are used within asyncz. That is how great APScheduler is!

So what was the reason why recreating another similar version of APScheduler? Well, it is not entirely the same
thing. Asyncz was designed to work only with ASGI and AsyncIO as well as integrating pydantic and bring the modern
python into the table.

APScheduler is widely used by millions of python developers and Asyncz **does not aim to replace** it, instead
is a more focused and optimised solution for async and ASGI frameworks out there.

## Async and ASGI

What does this mean? Well, Asyncz does not need to run inside any specific framework, actually you can use it
completely indepent from any framework as well as inside ASGI frameworks such as
[Esmerald](https://esmerald.dymmond.com), FastAPI, Starlette, Starlite, Quart... You can pick one and go for it.

Asyncz comes with special support to [Esmerald](https://esmerald.dymmond.com) for the simple reason that the author is
the same but it can be added more support. If you are interested in adding support to your favourite frameworks then
see the [contributing](./contributing.md) section.

## Concepts

Like APScheduler, Asyncz also brings four kinds of components:

* [Schedulers](./schedulers.md)
* [Triggers](./triggers.md)
* [Stores](./stores.md)
* [Executors](./executors.md)

## Requirements

* Python 3.7+

Asyncz wouldn't be possible without two giants:

* <a href="https://apscheduler.readthedocs.io/en/3.x/" class="external-link" target="_blank">APScheduler</a>
* <a href="https://pydantic-docs.helpmanual.io/" class="external-link" target="_blank">Pydantic</a>

## Installation

```shell
$ pip install asyncz
```

## The right decisions

How do you know if you are choosing the right [scheduler](./schedulers.md),
[triggers](./triggers.md), [stores](./stores.md) and [executors](./executors.md)?

Well, Asyncz is intentionally designed for specific systems and already helps you out with some of
those questions.

* **Schedulers** - Natively only supports the [AsyncIOScheduler](./schedulers.md#asyncioscheduler).
* **Triggers** - Here it will depend of the periocidity of our tasks. Example:
    * [CronTrigger](./triggers.md#crontrigger) - UNIX like cron and gives you the same feeling as
scheduling a task on a native UNIX like based system.
    * [DateTrigger](./triggers.md#datetrigger) - When you need to run a job once on a specific
point of time.
    * [IntervalTrigger](./triggers.md#intervaltrigger) - When you need to run jobs in specific
intervals of time.
    * [OrTrigger](./triggers.md#ortrigger)/[AndTrigger](./triggers.md#andtrigger) - If you would
like to combine more than one trigger (cron, interval and date) together.
* **Stores** - Natively only supports [redis](./stores.md#redisstore),
[mongo](./stores.md#mongodbstore) and [memory](./stores.md#memorystore).
* **Executors** - Natively only supports [AsyncIOExecutor](./executors.md#asyncioexecutor),
[ThreadPoolExecutor](./executors.md#threadpoolexecutor) and
[ProcessPoolExecutor](./executors.md#processpoolexecutor).

Sometimes having a lot of options makes the decision making very hard and Asyncz is intentionally
designed and driven to simplify and for specific use cases but is not limited to those. In every
section you have the option of uilding your own stores, executors, triggers and schedulers.

## Configuring the scheduler

Due its simplificy, Asyncz provides some ways of configuring the scheduler for you.

=== "In a nutshell"

    ```python
    from asyncz.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler()
    ```

=== "From the schedulers"

    ```python
    from asyncz.schedulers import AsyncIOScheduler

    scheduler = AsyncIOScheduler()
    ```

Initialize the rest of the application after the `scheduler` initialisation.
More [details](./schedulers.md) can be found with more thorough explanations.

This is in simple terms and in a nutshell how to start with Asyncz quickly. For more information,
details and examples how to leverage Asyncz simply navigate through the documentation and have
fun 😁🎉.

## ASGI support

Asyncz currently supports the [Esmerald framework](./contrib/esmerald/index.md) and brings some
batteries that are currently used by the framwork and leveraging Asyncz.

If you wish to have support to any other framework such as FastAPI, Starlite, Starlette or
literally any other, check the [contributing](./contributing.md) section and see how you can do it.

## Sponsors

Currently there are no sponsors of **Asyncz** but you can financially help and support the author though
[GitHub sponsors](https://github.com/sponsors/tarsil) and become a **Special one** or a **Legend**.