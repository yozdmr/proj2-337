class ConversationNode:
    def __init__(self, question, question_type, answer, step):
        self.question = question
        self.question_type = question_type
        self.answer = answer
        self.step = step
        self.next = None
        self.prev = None


class ConversationHistory:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None

    def add_step(self, question, question_type, answer, step_obj):
        node = ConversationNode(question, question_type, answer, step_obj)

        if self.head is None:
            self.head = node
            self.tail = node
            self.current = node
        else:
            # Set up doubly linked list connections
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
            self.current = node

    def last(self):
        return self.tail

    def find_last_with(self, condition):
        curr = self.tail
        while curr:
            if condition(curr):
                return curr
            curr = curr.prev
        return None
    
    def step_forward(self):
        if self.current is None:
            return None, False
        if self.current.next is None:
            return self.current, False
        self.current = self.current.next
        return self.current, True
    
    def step_backward(self):
        if self.current is None:
            return None, False
        if self.current.prev is None:
            return self.current, False
        self.current = self.current.prev
        return self.current, True
    
    def to_list(self):
        out = []
        cur = self.head
        while cur:
            out.append({
                "question": cur.question,
                "type": cur.question_type,
                "answer": cur.answer if isinstance(cur.answer, dict) else {"answer": cur.answer},
                "step_number": cur.step.step_number if cur.step else None
            })
            cur = cur.next
        return out

    def print_history(self):
        cur = self.head
        i = 1
        print("\n=== CONVERSATION HISTORY ===")
        while cur:
            print(f"{i}. Q: {cur.question}  |  type={cur.question_type}")
            print(f"   A: {cur.answer['answer'] if isinstance(cur.answer, dict) else cur.answer}")
            if cur.step:
                print(f"   Step {cur.step.step_number}: {cur.step.description[:40]}...")
            print()
            cur = cur.next
            i += 1
        print("=== END HISTORY ===\n")

