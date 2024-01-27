from peewee import SqliteDatabase, Model, CharField, IntegerField

db = SqliteDatabase('data.sqlite')


class Estate(Model):
    type = CharField(choices=['buy', 'rent'])
    city = CharField(max_length=255)
    price = IntegerField()
    currency = CharField(max_length=7)
    rooms = IntegerField(null=True)
    space = IntegerField(null=True)
    address = CharField(max_length=255)

    class Meta:
        database = db
        db_table = 'estate'
