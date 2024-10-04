import uvicorn
from fastapi import FastAPI, Query, Body, HTTPException
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

app = FastAPI(docs_url=None, redoc_url=None)

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Dubai", "name": "dubai"},
]


@app.put("/hotels/{hotel_id}")
def put_change_all(
        hotel_id: int,
        title: str = Body(embed=True),
        name: str = Body(embed=True)
):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = title
            hotel["name"] = name
            return {"status": "ok", "updated_hotel": hotel}

    # Если отель с таким id не найден
    raise HTTPException(status_code=404, detail="Hotel not found")


# PATCH: Частичное обновление информации об отеле
@app.patch("/hotels/{hotel_id}")
def patch_change_uniq(
        hotel_id: int,
        title: str | None = Body(None, embed=True),
        name: str | None = Body(None, embed=True)
):
    global hotels
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            # Обновляем только если значение не None и не равно "string"
            if title is not None and title != "string":
                hotel["title"] = title
            if name is not None and name != "string":
                hotel["name"] = name

            return {"status": "ok", "updated_hotel": hotel}

    # Если отель с таким id не найден
    raise HTTPException(status_code=404, detail="Hotel not found")




@app.post("/hotels")
def create_hotel(
        title: str = Body(embed=True),
):
    global hotels
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "title": title
    })
    return {"status": "ok"}


@app.delete("/hotels/{hotel_id}")
def delete_hotels(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]

    return {"status": "ok"}


@app.get("/hotels")
def get_hotels(
        id: int | None = Query(None, description="Айди отеля"),
        title: str | None = Query(None, description="Название отеля"),
):
    hotels_ = []
    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)
    return hotels_


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


if __name__ == "__main__":
    uvicorn.run("main:app")
