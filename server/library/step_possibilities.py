step_general_possibilities = [
    "yes",
    "sure",
    "of course",
    "I want to order",
    "What do you have?",
    "I'm not sure",
    "what's on the menu?",
    "Yes, I want",
    "Do you have",
    "I want something",
    "I'm looking for something",
    "I want",
    "no, that's all",
    "that's all",
    "nope"
]

step_selecting = [
    "Yes, I want",
    "I want the",
    "Give me the",
    "I would like the",
]

step_yes_menu = [
    "The menu sounds great",
    "today's special",
    "the special"
]

step_just_not = [
    "Just the",
    "I only want the",
    "No, I wanted",
    "Just want the",
    "Keep only the",
    "Not the",
    "Don't want the",
    "Didn't want",
    "I didn't mean",
    "Remove the",
    "Without the"
]

step_food_names = [
    "pizza",
    "soup",
    "meal",
    "italian",
    "japanese",
    "french",
    "mexican",
    "vegan",
    "gluten-free",
    "vegetarian",
    "Japanese ramen noodle soup",
    "Japanese rice/gohan",
    "Miso Soup",
    "Smoked salmon & avocado sushi",
    "Beetroot & avocado nori rolls with wasabi dipping sauce",
    "Gyoza",
    "Yaki udon",
    "Onigiri - Japanese Rice Balls",
    "Mochi",
    "Vegan ramen",
    "Yakisoba - Japanese Stir Fry Noodles",
    "Quiche Lorraine",
    "White chocolate crème brûlée",
    "Caramel soufflés with caramel sauce",
    "Macarons",
    "Ratatouille",
    "Salade niçoise",
    "Pork cassoulet",
    "Coq au vin",
    "Tarte Tatin",
    "Pizza Margherita",
    "Vegan pizza Margherita",
    "Gluten-free pizza",
    "Cheese & bacon pizza",
    "Tuna pizza",
    "Tortellini with pesto & broccoli",
    "Strawberry panna cotta",
    "Carbonara with chicken",
    "Chicken meatballs spaghetti",
    "Calzone",
    "Spaghetti bolognese",
    "Summer courgette risotto",
    "Lasagne",
    "Tiramisu",
    "Ultimate guacamole",
    "sweetcorn & tomato nachos",
    "Chicken quesadillas",
    "Sweet potato, peanut butter & chilli quesadillas",
    "Chicken enchiladas",
    "Chicken burrito",
    "Vegan burritos",
    "Fish tacos",
    "Spicy black bean tacos",
    "Chilli Con Carne",
    "Posole"
]

step_possibilities = {
    "start": step_general_possibilities+step_food_names,
    "ask_mood": step_general_possibilities+step_food_names,
    "menu_or_help": step_general_possibilities+step_yes_menu,
    "help_category": step_food_names,
    "help_country": step_food_names,
    "help_restrictions": step_food_names,
    "list_options": step_selecting+step_food_names,
    "confirm_order": step_just_not+step_food_names,
    "final_order": step_general_possibilities
}
