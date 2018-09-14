from django.db import models


class ProductCategory(models.Model):
    class Meta:
        db_table = 'category'
    
    name = models.CharField(max_length=255)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, category_id):
        return cls.objects.filter(id=category_id).first()

    @classmethod
    def create_category(cls, data):
        return cls.objects.create(**data)

    @classmethod
    def edit_category(cls, product_id, data):
        cls.objects.filter(id=product_id).update(**data)

    @classmethod
    def delete_category(cls, product_id):
        return cls.objects.filter(id=product_id).delete()


class Product(models.Model):
    class Meta:
        db_table = 'product'
        ordering = ['-id']

    product_name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    model_number = models.CharField(max_length=255)
    category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
    jan_code = models.CharField(max_length=255)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, product_id):
        return cls.objects.filter(id=product_id).select_related().first()

    @classmethod
    def get_by_ids(cls, product_ids):
        return cls.objects.filter(id__in=product_ids).select_related()

    @classmethod
    def get_by_barcodes(cls, barcodes: list):
        return cls.objects.filter(jan_code__in=barcodes)

    @classmethod
    def get_by_category_id(cls, category_id):
        return cls.objects.filter(category=category_id)

    @classmethod
    def create_product(cls, data):
        return cls.objects.create(**data)

    @classmethod
    def edit_product(cls, product_id, data):
        cls.objects.filter(id=product_id).update(**data)

    @classmethod
    def delete_product(cls, product_id):
        return cls.objects.filter(id=product_id).delete()
