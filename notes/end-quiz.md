# End quiz

Questions saved up during the lab and the CA, to answer at the very end instead of during each step. Try them without looking, then check the answers at the bottom.

## Questions

### Observer pattern (W05)

1. In `observer.py`, the state is 0. Which observers react, and why can more than one react to the same event?
2. After `subject.detach(observer_a)`, who can still react? Can it happen that nobody reacts?
3. `_observers` is created in the class body, not in `__init__`. What goes wrong if you create two subjects?

### Bulk upload (W10)

4. You upload 1000 Mockaroo rows. Why do fewer than 1000 get in, and what status code do the rejected ones get in your app?
5. The lecturer's script posts to `/items` (no slash). Why does that return 405 in your app, when it worked for the lecturer?

### Serving the front-end and CORS

6. With the page served by FastAPI at `localhost:8000`, why is there no `OPTIONS` request before a `POST`?
7. In the demo, the front-end runs on your laptop and the backend on AWS. Which line in `main.py` makes that allowed, and why must the address start with `http://` and not `https://`?

## Answers

1. Both A (`0 < 3`) and B (`state == 0`). Each observer checks its own rule, and `notify()` calls every observer in the list, so one event can trigger several, one or none.
2. Only B, because A is no longer in the list that `notify()` loops over. Yes: if the state is 1, B's rule is false too, so nobody reacts.
3. The list is shared by every subject, so attaching an observer to one subject also attaches it to the other. Creating the list in `__init__` gives each subject its own.
4. Mockaroo repeats first names, and `name` is unique in `models.py`. The database rejects each duplicate, and `commit_or_409` turns that into **409 Conflict**. (The lecturer's version had no handler, so his app returned 500.)
5. Routes are checked top to bottom and the first full match wins. `/items` doesn't match `/items/`, but the catch-all `app.mount("/", StaticFiles(...))` matches everything, so the request reaches the static file server, which only accepts GET and HEAD, hence **405 Method Not Allowed**. The lecturer had no mount, so FastAPI redirected `/items` to `/items/` instead. The fix is to post to `/items/`.
6. The page and the API have the same origin (protocol, address and port), and the browser only applies CORS to cross-origin requests.
7. `CORSMiddleware` with `allow_origins=["http://localhost:5173"]`: the backend tells the browser that a page from `localhost:5173` may read its replies. The EC2 backend serves plain http on port 80 with no certificate, so an `https://` address finds nothing to connect to.
