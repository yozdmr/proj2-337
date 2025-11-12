class RecipeNode:
    def __init__(self, 
            step_number: int, description: str, 
            ingredients: list[dict], tools: list[dict], 
            methods: list[dict], time: dict, temperature: dict, 
            previous: 'RecipeNode', next: 'RecipeNode'
    ):
        self.step_number = step_number
        self.description = description
        self.ingredients = ingredients
        self.tools = tools
        self.methods = methods
        self.time = time
        self.temperature = temperature
        self.previous = previous
        self.next = next
    

class Recipe:
    def __init__(self, name: str, url: str, ingredients: list[dict], steps: list[dict]):
        self.name = name
        self.url = url
        self.ingredients = ingredients
        self.steps = steps

        self.current_step = self.create_nodes(steps)
        self.first_step = self.current_step

    def create_nodes(self, steps: list[dict]) -> RecipeNode:

        step_one = steps[0]

        root_node = RecipeNode(
            step_number=step_one["step_number"],
            description=step_one["description"],
            ingredients=step_one["ingredients"],
            tools=step_one["tools"],
            methods=step_one["methods"],
            time=step_one["time"],
            temperature=step_one.get("temperature", {}),
            previous=None,
            next=None
        )

        current_node = root_node
        for step in steps[1:]:
            current_node.next = RecipeNode(
                step_number=step["step_number"],
                description=step["description"],
                ingredients=step["ingredients"],
                tools=step["tools"],
                methods=step["methods"],
                time=step["time"],
                temperature=step.get("temperature", {}),
                previous=current_node,
                next=None
            )
            current_node = current_node.next

        return root_node

    def get_name(self) -> str:
        return self.name
    
    def get_url(self) -> str:
        return self.url

    def get_ingredients(self) -> list[dict]:
        return self.ingredients

    def get_steps(self) -> list[dict]:
        return self.steps

    def step_forward(self) -> tuple[RecipeNode, bool]:
        stepped = False
        if self.current_step.next is not None:
            self.current_step = self.current_step.next
            stepped = True
        return self.current_step, stepped

    def step_backward(self) -> tuple[RecipeNode, bool]:
        stepped = False
        if self.current_step.previous is not None:
            self.current_step = self.current_step.previous
            stepped = True
        return self.current_step, stepped
    
    def nth_step(self, step_number: int) -> RecipeNode:
        current_step = self.first_step
        for i in range(step_number - 1):
            if current_step.next is None:
                return None
            current_step = current_step.next
        return current_step