import uvicorn
from fastapi import FastAPI, HTTPException
from tortoise.contrib.fastapi import register_tortoise, HTTPNotFoundError
from models.models import Medications, MedicationsCategory, MedicationsPydantic, MedicationsCategoryPydantic
from typing import Optional, List
from pydantic import BaseModel
import random
import string


app = FastAPI()

DATABASE_URL = "postgres://user1:password1@127.0.0.1:5432/medic_db"


class Status(BaseModel):
    message: str


class Category(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]


class CategoryRequest(BaseModel):
    name: Optional[str]
    description: Optional[str]


class Medicament(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]
    category: Optional[int] = 1


class MedicamentRequest(BaseModel):
    name: Optional[str]
    description: Optional[str]
    category: Optional[int] = 1


class MedicamentImport(BaseModel):
    id: int
    name: Optional[str]
    description: Optional[str]
    category: Optional[Category] = 1


class ImportResponse(BaseModel):
    count: int
    result: List[MedicamentImport]


@app.get("/medicaments", response_model=List[Medicament])
async def get_all_medicaments(limit: Optional[int] = 10, offset: Optional[int] = 0, category: Optional[int] = 1):
    if not category:
        return await MedicationsPydantic.from_queryset(Medications.all().limit(limit).offset(offset))
    else:
        return await MedicationsPydantic.from_queryset(Medications.filter(category=category).limit(limit).offset(offset))


@app.post("/medicament", response_model=Medicament)
async def create_medicament(item: MedicamentRequest):
    instance = item.dict()
    category = await MedicationsCategory.filter(id=instance['category']).first()
    if not category:
        raise HTTPException(status_code=404, detail=f'Category not found')
    medication_obj = await Medications.create(name=instance['name'],
                                              description=instance['description'],
                                              category=category)
    return await MedicationsPydantic.from_tortoise_orm(medication_obj)


@app.put("/medicament/", response_model=Medicament,
         responses={404: {"model": HTTPNotFoundError}})
async def update_medicament(medicament_id: int, item: MedicamentRequest):
    instance = item.dict()
    category = await MedicationsCategory.filter(id=instance['category']).first()
    if not category:
        raise HTTPException(status_code=404, detail=f'Category not found')
    await Medications.filter(id=medicament_id).update(name=instance['name'],
                                                      description=instance['description'],
                                                      category=category)
    return await MedicationsPydantic.from_queryset_single(Medications.get(id=medicament_id))


@app.delete("/medicament/", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_medicament(medicament_id: int):
    deleted_medication = await Medications.filter(id=medicament_id).delete()
    if not deleted_medication:
        raise HTTPException(status_code=404, detail=f'Medication {medicament_id} not found')
    return Status(message=f"Medicament {medicament_id} is deleted")


@app.get("/categories", response_model=List[MedicationsCategoryPydantic])
async def get_all_categories(limit: Optional[int] = 10, offset: Optional[int] = 0):
    return await MedicationsCategoryPydantic.from_queryset(MedicationsCategory.all().limit(limit).offset(offset))


@app.post("/category", response_model=MedicationsCategoryPydantic)
async def create_category(item: CategoryRequest):
    category_obj = await MedicationsCategory.create(**item.dict())
    return await MedicationsCategoryPydantic.from_tortoise_orm(category_obj)


@app.put("/category", response_model=MedicationsCategoryPydantic)
async def update_category(category_id: int, item: CategoryRequest):
    await MedicationsCategory.filter(id=category_id).update(**item.dict())
    return await MedicationsCategoryPydantic.from_queryset_single(MedicationsCategory.get(id=category_id))


@app.delete("/category", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_category(category_id: int):
    deleted_medication = await MedicationsCategory.filter(id=category_id).delete()
    if not deleted_medication:
        raise HTTPException(status_code=404,
                            detail=f'Category {category_id} not found')
    return Status(message=f"Category {category_id} is deleted")


@app.get("/import", response_model=ImportResponse)
def import_medicament(limit: Optional[int] = 10):
    return ImportResponse(
        count=random.randint(1, 1000000),
        result=[
            MedicamentImport(
                id=random.randint(1, 1000000),
                name=random.choice(string.ascii_uppercase) + "".join([random.choice(string.ascii_lowercase) for _ in range(10)]),
                description="".join([random.choice(string.ascii_lowercase) for _ in range(100)]),
                category=Category(
                    id=random.randint(1, 1000000),
                    name=random.choice(string.ascii_uppercase) + "".join([random.choice(string.ascii_lowercase) for _ in range(10)]),
                    description="".join([random.choice(string.ascii_lowercase) for _ in range(100)]),
                )
            )
            for _ in range(limit)
        ],
    )


register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": ["models.models", "aerich.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


if __name__ == "__main__":
    uvicorn.run("main:app", debug=True, reload=True)
