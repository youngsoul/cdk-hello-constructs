from pynamodb.models import Model
from pynamodb.expressions.update import AddAction
from pynamodb.attributes import UnicodeAttribute, NumberAttribute

class HitModel(Model):

    class Meta:
        table_name = 'Hits'
        # aws_access_key_id= '*'
        # aws_secret_access_key = '*'

    path = UnicodeAttribute(hash_key=True)
    hits = NumberAttribute(default=0)

if __name__ == '__main__':
    hitmodel = HitModel.get('/pynamodb')
    print("")
    print(hitmodel)
    r = hitmodel.update(actions=[HitModel.hits.add(1)])
    print(hitmodel.hits)


