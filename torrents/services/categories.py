# -*- coding: utf-8 -*-

class CategoriesCache:
    def init_app(self, categories):
        self.categories = categories
        self.categories_by_url = {category.url:category for category in categories}

    def update_subcategories(self, subcategories):
        for category in self.categories:
            category.subcategories[:] = subcategories.get(category.tag,[])