"""GameFly rental API (exercise.md spec) on the layered starter.

Routes (exact paths from the spec table):
  POST /signup, POST /auth, POST /listings, GET /listings,
  POST /payment, POST /rentals, PUT /rentals/{rental_id},
  POST /listings/{listing_id}/sell, POST /games
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import CustomerDep, SessionDep, StaffDep
from app.models.game import Platform
from app.repositories.game import GameRepository
from app.repositories.listing import ListingRepository
from app.repositories.payment import PaymentRepository
from app.repositories.rental import RentalRepository
from app.repositories.user import UserRepository
from app.schemas.auth import SigninRequest, SignupRequest
from app.schemas.gamefly import (
    GameCreate,
    GameResponse,
    ListingCreate,
    ListingResponse,
    ListingWithGameResponse,
    PaymentCreate,
    PaymentResponse,
    RentalCreate,
    RentalResponse,
    RentalReturnUpdate,
    SellListingRequest,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.game_service import GameService
from app.services.listing_service import ListingService
from app.services.payment_service import PaymentService
from app.services.rental_service import RentalService

router = APIRouter(tags=["GameFly"])
gamefly_router = router


def _repos(db):
    return (
        UserRepository(db),
        GameRepository(db),
        ListingRepository(db),
        RentalRepository(db),
        PaymentRepository(db),
    )


# ---------- Public: signup / auth ----------

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: SessionDep):
    user_repo, _, _, _, _ = _repos(db)
    if user_repo.get_by_username(body.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    try:
        user = AuthService(user_repo).register_user(body.username, body.email, body.password)
    except Exception as exc:  # duplicate email etc.
        raise HTTPException(status_code=400, detail="Username or email already exists") from exc
    return UserResponse(id=user.id, username=user.username, email=user.email)


@router.post("/auth")
def auth(body: SigninRequest, db: SessionDep):
    user_repo, _, _, _, _ = _repos(db)
    token = AuthService(user_repo).authenticate_user(body.username, body.password)
    if not token:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}


# ---------- Listings ----------

@router.post("/listings", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(body: ListingCreate, db: SessionDep, current: CustomerDep):
    _, game_repo, listing_repo, _, _ = _repos(db)
    service = ListingService(listing_repo, game_repo)
    try:
        listing = service.create_listing(
            owner_id=current.id,
            game_id=body.game_id,
            condition=body.condition.value if hasattr(body.condition, "value") else str(body.condition),
            price=float(body.price),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ListingResponse(
        listingId=listing.listingId,
        gameId=listing.gameId,
        ownerId=listing.ownerId,
        condition=listing.condition,
        availability=listing.availability,
        price=listing.price,
    )


@router.get("/listings", response_model=list[ListingWithGameResponse])
def get_listings(
    db: SessionDep,
    platform: Optional[str] = Query(default=None, description="Filter: NSW|PS5|XBOX|PC"),
):
    _, game_repo, listing_repo, _, _ = _repos(db)
    if platform is not None and platform not in {p.value for p in Platform}:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid platform '{platform}'. Expected one of NSW|PS5|XBOX|PC",
        )
    service = ListingService(listing_repo, game_repo)
    out: list[ListingWithGameResponse] = []
    for listing, game in service.list_with_games(platform=platform):
        game_resp = None
        if game is not None:
            game_resp = GameResponse(
                gameId=game.gameId,
                title=game.title,
                rating=game.rating,
                platform=game.platform,
                boxart=game.boxart,
                genre=game.genre,
            )
        out.append(
            ListingWithGameResponse(
                listingId=listing.listingId,
                gameId=listing.gameId,
                ownerId=listing.ownerId,
                condition=listing.condition,
                availability=listing.availability,
                price=listing.price,
                game=game_resp,
            )
        )
    return out


@router.post("/listings/{listing_id}/sell", response_model=ListingResponse)
def sell_listing(
    listing_id: int,
    db: SessionDep,
    current: CustomerDep,
    body: Optional[SellListingRequest] = None,
):
    _, game_repo, listing_repo, _, _ = _repos(db)
    _ = body  # no extra data needed; accepted for forward-compat
    service = ListingService(listing_repo, game_repo)
    try:
        listing = service.sell_listing(listing_id=listing_id, owner_id=current.id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ListingResponse(
        listingId=listing.listingId,
        gameId=listing.gameId,
        ownerId=listing.ownerId,
        condition=listing.condition,
        availability=listing.availability,
        price=listing.price,
    )


# ---------- Games (staff seed helper) ----------

@router.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(body: GameCreate, db: SessionDep, current: StaffDep):
    _ = current
    _, game_repo, _, _, _ = _repos(db)
    try:
        game = GameService(game_repo).create_game(
            title=body.title,
            platform=body.platform.value if hasattr(body.platform, "value") else str(body.platform),
            genre=body.genre,
            rating=body.rating,
            boxart=body.boxart,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return GameResponse(
        gameId=game.gameId,
        title=game.title,
        rating=game.rating,
        platform=game.platform,
        boxart=game.boxart,
        genre=game.genre,
    )


# ---------- Payments (staff) ----------

@router.post("/payment", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(body: PaymentCreate, db: SessionDep, current: StaffDep):
    _ = current
    _, _, _, _, payment_repo = _repos(db)
    try:
        payment = PaymentService(payment_repo).create_payment(
            amount=float(body.amount),
            customer_id=body.customer_id,
            rental_id=body.rental_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return PaymentResponse(
        paymentId=payment.paymentId,
        customerId=payment.customerId,
        payment_date=payment.payment_date,
        amount=payment.amount,
        rentalId=payment.rentalId,
    )


# ---------- Rentals (staff) ----------

@router.post("/rentals", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def create_rental(body: RentalCreate, db: SessionDep, current: StaffDep):
    _ = current
    user_repo, _, listing_repo, rental_repo, payment_repo = _repos(db)
    service = RentalService(rental_repo, listing_repo, payment_repo, user_repo)
    try:
        rental = service.confirm_rental(listing_id=body.listing_id, renter_id=body.customer_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RentalResponse(
        rentalId=rental.rentalId,
        listingId=rental.listingId,
        renterId=rental.renterId,
        rentalDate=rental.rentalDate,
        returnDate=rental.returnDate,
    )


@router.put("/rentals/{rental_id}", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def return_rental(rental_id: int, body: RentalReturnUpdate, db: SessionDep, current: StaffDep):
    _ = current
    user_repo, _, listing_repo, rental_repo, payment_repo = _repos(db)
    service = RentalService(rental_repo, listing_repo, payment_repo, user_repo)
    try:
        rental = service.confirm_return(
            rental_id=rental_id,
            payment_id=body.payment_id,
            amount=body.amount,
            customer_id=body.customer_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        # Missing payment payload -> 422 (validation-like); already-returned etc -> 400.
        msg = str(exc).lower()
        code = 422 if "requires payment" in msg or "amount" in msg else 400
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    return RentalResponse(
        rentalId=rental.rentalId,
        listingId=rental.listingId,
        renterId=rental.renterId,
        rentalDate=rental.rentalDate,
        returnDate=rental.returnDate,
    )
