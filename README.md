# two-endpoint-service

A small FastAPI service that stores work orders and the locations they happen at, in Postgres.

This is an exercise, not a real product. It started as Part 2 of the TripleTen AI Systems
pre-cohort warm-up: build a service with exactly two endpoints, backed by a real database, with
one automated test. The domain was handed to me so I wouldn't waste time inventing one — work
orders have a title, a status and a timestamp, and that's deliberately all.

It's since grown past two endpoints, because Part 3 asks for a second table and a read that
combines both, and for the whole thing to come up with a single command. The name stuck.

Part 1 of the same exercise was getting the [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
running and changing something in it, so a lot of what's here is modelled on that repo.

## What you need

- Docker
- [uv](https://docs.astral.sh/uv/), if you want to run the service or the tests outside a container

## Running it

Everything comes up with one command, from the repo root:

```bash
docker compose up --build
```

That builds the service image, starts Postgres, waits for it to actually accept connections,
and then starts the service against it. Swagger UI is at <http://localhost:8000/docs>.

The `depends_on: condition: service_healthy` matters more than it looks. Postgres reports the
container as started well before it is ready to answer queries, so without the healthcheck the
service wins the race about half the time and dies on connection refused.

Tables are created from the models at startup, so there's no migration step.

### Running it without compose

Useful when you want the reload loop. Start Postgres on its own:

```bash
docker run --name wo-db -e POSTGRES_PASSWORD=dev -p 5432:5432 -d postgres:16
```

then, from `backend/`:

```bash
uv run fastapi dev app/main.py
```

The default `DATABASE_URL` points at `localhost:5432`, so this needs no configuration.

## Running the tests

The tests drive the app in-process through FastAPI's `TestClient` — no server needs to be
running — but they hit a real database, not a fake one, so Postgres has to be reachable at
`localhost:5432`. From `backend/`:

```bash
uv run pytest
```

Seven tests: the work-order round trip, an unknown id, a malformed body, the location round
trip with its work orders, an unknown location, a malformed location, and work orders for a
location that doesn't exist.

The image is built with `--no-dev`, so pytest isn't installed in it. Tests run on the host.

## The endpoints

### Work orders

**`POST /work-orders`** — takes a `title`, a `status` and the `location_id` of an existing
location. Stores it, returns the record with a generated `id` and `created_at`.

```bash
curl -X POST localhost:8000/work-orders \
  -H "Content-Type: application/json" \
  -d '{"title": "Fix the boiler", "status": "open", "location_id": "<uuid>"}'
```

A `location_id` that doesn't exist returns 400 rather than blowing up. The foreign key would
reject it anyway, but that surfaces as an `IntegrityError` and a 500, which says "the server
broke" when what actually happened is that the client referenced something that isn't there.
The explicit lookup exists to produce a decent error message.

**`GET /work-orders/{id}`** — returns that record, or 404 if there isn't one.

### Locations

**`POST /locations`** — takes a `title` and `coordinates`, returns the record with an `id`.

**`GET /locations/{id}`** — returns that location, or 404.

**`GET /locations/{id}/work-orders`** — every work order at that location. 404 if the location
doesn't exist; an empty list if it exists and has none, which is not an error.

Locations are their own resource rather than something you create inline with a work order. A
location exists before any work order and outlives them all, so creating one as a side effect
would mean a fresh duplicate row per order and a relationship that never actually relates
anything.

### Errors

Bad input returns 400. FastAPI returns 422 for validation failures by default and the brief
asked for 400, so there's a `RequestValidationError` handler in `main.py` that overrides it.

## Configuration

`app/config.py` has a default for every setting, so it runs with no `.env` file. Drop a `.env`
at the repo root to override `DATABASE_URL` or `PROJECT_NAME`. Compose passes `DATABASE_URL` as
an environment variable, which takes precedence over both.

The two URLs differ only in host: `localhost` when the service runs on your machine, `db` when
it runs in compose, because on a compose network you address the other container by its service
name.

One thing worth knowing if you change the database URL: the scheme is `postgresql+psycopg://`,
not `postgresql://`. SQLAlchemy assumes psycopg2 when you leave the driver off, and this uses
psycopg 3. The error you get otherwise is a missing `psycopg2` module, which doesn't point at
the connection string at all.

## Layout

```
compose.yml                     both services, the healthcheck, the volume
backend/
├── Dockerfile                  built from the repo root, not from backend/
└── app/
    ├── main.py                 FastAPI app, the 400 handler, /ping
    ├── models.py               WorkOrder, Location, and the shapes POST accepts
    ├── config.py               settings
    ├── core/db.py              engine, session, table creation
    └── api/
        ├── main.py             aggregates the routers
        └── routes/
            ├── work_orders.py
            └── locations.py
```

The Dockerfile lives in `backend/` but its `COPY` lines expect the repo root as context, since
`pyproject.toml` and `uv.lock` sit at the top level. Hence `dockerfile: backend/Dockerfile` with
`context: .` in compose, and `docker build -f backend/Dockerfile .` by hand.

`app/api/main.py` exists so that `main.py` includes exactly one router forever. Adding a
resource touches the aggregator, not the app.

### The model split

`WorkOrderBase` is what POST accepts — title, status, location_id. `WorkOrder` adds `id` and
`created_at`, which the server sets. Keeping them separate is what stops a caller supplying
their own id and overwriting a record.

`location_id` sits on the base rather than the table class because the client is genuinely the
source of that value. The template this is modelled on does the opposite with `Item.owner_id`,
keeping it off the create model and injecting it from the authenticated user — same rule,
opposite answer, because there the server knows the value and the client must not be trusted
with it.

The `location` and `work_orders` attributes are `Relationship`s, not columns. They don't appear
in any response, because SQLModel serializes fields and keeps relationships in a separate
registry. They exist so the nested read can walk from a location to its orders without a
hand-written join.

## What I'd do differently

Alembic instead of `create_all`. This stopped being theoretical the moment I added
`location_id`: `create_all` only issues `CREATE TABLE` for tables that don't exist, so it
silently left the existing `workorder` table alone and every insert failed on a column the
model had and the database didn't. Dropping the table fixed it because there was no data worth
keeping. That answer expires the first time there is.

`status` is a plain string and will accept anything, including "banana". Same for
`coordinates`, which is a string holding two numbers and validates neither. Both were left
loose on purpose to keep the scope down; a fixed set of statuses and a real lat/long pair are
the obvious next steps.

The nested read is a lazy load, so fetching a location and its work orders is two queries. Fine
for one location. If there were ever a `GET /locations` that returned each location's orders,
that becomes N+1 and wants `selectinload`.

Nothing covers the POST-with-unknown-location branch yet, which is the one piece of error
handling written by hand rather than inherited from the framework.
