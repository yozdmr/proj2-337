class ConversationNode:
    def __init__(self, question, question_type, answer, step):
        self.question = question
        self.question_type = question_type
        self.answer = answer
        self.step = step
        self.next = None


class ConversationHistory:
    def __init__(self):
        self.head = None
        self.tail = None

    def add_step(self, question, question_type, answer, step_obj):
        node = ConversationNode(question, question_type, answer, step_obj)

        if self.head is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node

    def last(self):
        return self.tail

    def find_last_with(self, condition):
        """Walk backwards by scanning; linked list only tracks forward but tail pointer helps."""
        curr = self.head
        stack = []

        while curr:
            stack.append(curr)
            curr = curr.next
        
        # Walk backward
        while stack:
            node = stack.pop()
            if condition(node):
                return node
        return None
    
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

