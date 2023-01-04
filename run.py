from datetime import datetime, timezone
from app.category import Category, check_if_in_category
from app.page import Page
import json

page = Page("Informatyka")
rev = page.find_revision(datetime.now(timezone.utc))

i = 0
j = 0
for page in rev.get_subpages_names():
    if check_if_in_category(page, ["Kategoria:Informatyka"]):
        i += 1
    j += 1
print(f"Na stronie Informatyka znajduje się {j} odnośników, z czego {i} należy do kategorii informatyka, czyli {100*i/j}%")

x = Category("Kategoria:Informatyka", "Kategoria:Informatyka")

out = dict.fromkeys(range(2006, 2024))
for key in out.keys():
    out[key] = dict()

for year in range(2006, 2024):
    print(f"{year} -> {len(x.find_categories(datetime(year, 1, 1, 0, 0, tzinfo=timezone.utc)))}")

for year in out.keys():
    revision = datetime(year, 1, 1, 0, 0, tzinfo=timezone.utc)
    for page in x.find_categories(revision):
        page_obj = page.to_page()
        rev = page_obj.find_revision(revision)
        if rev:
            if page_obj.name in out[year]:
                out[year][page_obj.name].extend(rev.get_subpages_names())
            else:
                out[year][page_obj.name] = rev.get_subpages_names()

for year in out.keys():
    with open(f"out/{year}.json", "w") as file:
        json.dump(out[year], file)