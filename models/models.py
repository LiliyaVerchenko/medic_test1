from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Medications(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    category = fields.ForeignKeyField('models.MedicationsCategory', related_name='categories')

    def __str__(self):
        return self.name


class MedicationsCategory(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField()

    def __str__(self):
        return self.name


MedicationsPydantic = pydantic_model_creator(Medications, name="Medications")
MedicationsCategoryPydantic = pydantic_model_creator(MedicationsCategory, name="MedicationsCategory")