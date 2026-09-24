# Task: Implement & Test the GameFly Rental API (FastAPI)

Source: Tutorial 4 — Test Planning. This file is the full spec — don't ask for
the tutorial PDF, everything needed is below. Fill in `<REPO_URL>` before
starting.

## Objective

Implement the game-rental API on the course's layered FastAPI starter, then
produce unit, integration, and API test coverage plus an evidence report.
Keep changes small and reviewable — don't refactor unrelated code, don't
commit secrets/`.env`.

## Setup

```
git clone <REPO_URL>
cd <repo-folder>
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # if it exists
python manage.py init
python manage.py run
```

Confirm the app boots and `/docs` loads before writing any code.

## Domain model

Reconstructed from the assignment's class diagram — cross-check against the
actual diagram image in the PDF before implementing, especially where `Staff`
sits relative to `User`.

- **User** (base): `id`, `username`, `password` — `toJSON()`, `check_password()`, `set_password()`
- **Customer** (extends User): `payments[]`, `listings[]`, `rentals[]`, `status: Enum(Active|InActive)`
- **Payment**: `paymentId`, `customerId (FK)`, `payment_date`, `Amount` — `toJSON()`
- **RentalPayment** (extends Payment): `rentalId (FK)`
- **Listing**: `listingId`, `gameId (FK)`, `ownerId (FK)`, `condition`, `availability: Enum`, `price`, `rentals[]` — `toJSON()`
- **Game**: `gameId`, `listings[]`, `title`, `rating`, `platform`, `boxart`, `genre` — `toJSON()`
- **Rental**: `rentalId`, `listingId (FK)`, `renterId (FK)`, `rentalDate`, `returnDate`, `payments[]` — `toJSON()`
- **Staff**: `list_game(owner, game, condition, price)`, `confirm_rental(renter, listing)`, `confirm_return(renter, rental)`

## API routes

| Access | Method | Path | Request Body | Success / Errors |
|---|---|---|---|---|
| Public | POST | `/signup` | username, email, password | 201 created; 400 duplicate |
| Public | POST | `/auth` | username, password | 200 token; 400 invalid credentials |
| Customer | POST | `/listings` | game_id, condition, price | 201 created; 401/404/422 |
| Public | GET | `/listings?platform=` | query: NSW\|PS5\|XBOX\|PC | 200 listings w/ nested game data |
| Staff | POST | `/payment` | amount | 201 created + paymentId |
| Staff | POST | `/rentals` | listing_id, customer_id | 201 created; 404 bad listing |
| Staff | PUT | `/rentals/{rental_id}` | payment or payment_id | 201 updated; 404 missing rental/payment |
| Owner | POST | `/listings/{listing_id}/sell` | **undefined — design this** | **undefined — design this** |
| Staff | POST | `/games` | **undefined — design this** (dev/seed helper) | **undefined — design this** |

For the two undefined rows: pick a sensible request/response contract
consistent with the rest of the table and document your choice in the README.

## Business rules to enforce

- Creating a rental changes the listing to unavailable/rented.
- Returning a rental records the payment and makes the listing available again.
- An owner can sell only their own **active** listing.
- Password hashing never returns/stores the plaintext password.
- Invalid listing condition/availability is rejected by schema validation.
- Services refuse action on a missing or unavailable listing.

## Deliverables — all required

### 1. Code
Implement every route above.

### 2. Unit tests (fully mocked, no DB)
At minimum:
- `test_new_user`, `test_toJSON`
- password hashing never returns plaintext
- valid credentials produce a token
- invalid listing condition rejected by schema validation
- service refuses a missing/unavailable listing

Decide whether `Staff.create_listing()` can be a true unit test or requires a
DB — write the answer + one-line reasoning in the README, then put the test
in whichever suite (unit or integration) it actually belongs in.

### 3. Integration tests (isolated SQLite/test DB)
At minimum:
- `test_create_user`, `test_authenticate`, `test_get_all_users_json`, `test_update_user`
- `test_staff_create_listing` (staff creates a listing for a customer's game; verify FK linkage)
- a created game + listing persist with correct IDs
- creating a rental changes the listing to rented
- returning a rental records the payment and makes the listing available again
- an owner can sell only their own active listing
- `test_staff_confirm_rental` and `test_staff_return_rental` — write these; the tutorial leaves them as stubs

### 4. API tests (Postman)
Exercise every route. For protected routes: call `/auth` first, use the
returned token. Include **at least one negative case per protected route**
(missing/bad token, invalid payload, 404, etc). Screenshot request body,
status code, and response for each.

### 5. UAT test case
Add a "Test Sell Game" row to the UAT table below, matching the format of
the existing rows:

| Test Case | Pre-conditions | Test Steps | Test Criteria |
|---|---|---|---|
| Test Sell Game | *(fill in)* | *(fill in)* | *(fill in)* |

### 6. Evidence report (PDF)
Must contain:
- Repo URL + your name
- Readable screenshot of the unit + integration suite running, all passing
- Postman screenshots covering every route, including the negative cases

### 7. Submit
- Push code, tests, README, seed data to the repo.
- Repo must be readable by a marker with zero access requests.
- Submit the repo URL + evidence report (PDF or link) to the course system.

## If anything's ambiguous
Don't silently guess on an API contract that isn't specified above — flag it
in the README under an "Assumptions" section instead of burying the decision
in code.