import random

def get_random_skin(skin_chances):
   cumulative_chances = []
   total_chance = 0
   for chance in skin_chances.values():
       total_chance += chance
       cumulative_chances.append(total_chance)

   random_value = random.randint(1, total_chance)
   selected_skin = None
   for i, chance in enumerate(cumulative_chances):
       if random_value <= chance:
           selected_skin = list(skin_chances.keys())[i]
           break

   return selected_skin

# Пример использования
skin_chance = {
    "Скин A": 1,
    "Скин B": 2,
    "Скин C": 3,
    "Скин D": 100,
    "Скин E": 0,
    "Скин F": 0
}
select_skin = get_random_skin(skin_chance)
print(f"Выпал скин: {select_skin}")