class SankeyItem:
    def __init__(self, name, level, value, parents, children, main_category=None):
        self.name = name
        self.level = level
        self.value = value
        self.parents = parents
        self.children = children
        self.main_category = main_category

    def add_subcategory(self, subcategory_name, subcategory_item):
        self.subcategories[subcategory_name] = subcategory_item

    def __getitem__(self, key):
        if isinstance(key, int):
            subcategory_names = list(self.subcategories.keys())
            if 0 <= key < len(subcategory_names):
                return self.subcategories[subcategory_names[key]]
            else:
                raise IndexError("Index out of range")
        elif isinstance(key, str):
            return self.subcategories.get(key, None)
        else:
            raise TypeError("Key must be an integer or string")

    def __repr__(self):
        return f"SankeyItem(name={self.name}, level={self.level}, value={self.value}, parents={self.parents}, children={self.children}, main_category={self.main_category})"


class SubCategoryItem:
    def __init__(self, name, details=None):
        self.name = name
        self.details = details

    def __repr__(self):
        return f"SubCategoryItem(name={self.name}, details={self.details})"