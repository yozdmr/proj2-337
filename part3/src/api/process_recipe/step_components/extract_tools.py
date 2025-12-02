import nltk
from nltk import pos_tag, word_tokenize, sent_tokenize
from nltk.corpus import wordnet as wn

nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)

def collect_hyponyms(root):
    items = set()
    stack = [root]
    while stack:
        node = stack.pop()
        for h in node.hyponyms():
            items.add(h)
            stack.append(h)
    return items

ROOTS = [
    wn.synset("kitchen_utensil.n.01"),
    wn.synset("tableware.n.01"),
    wn.synset("cookware.n.01"),
    wn.synset("utensil.n.01")
]

def build_kitchen_tool_list():
    synsets = set()
    for root in ROOTS:
        synsets.update(collect_hyponyms(root))

    # Extract lemma names as English words
    words = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            # Convert things like "pie-dish" and "frying_pan" to clean tokens
            words.add(lemma.name().replace("_", " ").lower())

    return sorted(words)

KITCHEN_TOOLS = set(build_kitchen_tool_list())
KITCHEN_TOOLS.add("oven")  # NOTE: Add additional tools as necessary here




def extract_noun_phrases(tagged_sent):
    nps = []
    cur = []
    for tok, tag in tagged_sent:
        # Include all noun types: NN, NNS, NNP, NNPS, and modifiers DT, JJ, JJR, JJS
        if tag.startswith("NN") or tag in ("DT", "JJ", "JJR", "JJS"):
            cur.append((tok, tag))
        else:
            if cur:
                nps.append(cur)
                cur = []
    if cur:
        nps.append(cur)
    return nps

def head_noun(np):
    for tok, tag in reversed(np):
        if tag in ("NN","NNS"):
            return tok.lower()
    return None

def extract_tools(description: str) -> list[str]:
    tools = set()
    sentences = sent_tokenize(description)

    for sentence in sentences:
        tokens = word_tokenize(sentence)
        tagged = pos_tag(tokens)
        nps = extract_noun_phrases(tagged)

        for np in nps:
            hn = head_noun(np)
            if hn and hn in KITCHEN_TOOLS:
                tools.add(hn)

    return sorted(tools)



if __name__ == "__main__":
    description = "Combine the carrots, celery, peas, green beans, corn, onion, red potatoes, and chicken broth in a large pot. Season the vegetable mixture with thyme, salt, and black pepper; bring to a boil. Reduce heat to medium-low, cover, and simmer until the vegetables are tender, about 15 minutes. Drain the vegetables and set aside."
    tools = extract_tools(description)
    print("Tagged sentences for first example:")
    for i, sentence in enumerate(tools, 1):
        print(f"Sentence {i}: {sentence}")

    # Test with another example
    description2 = "Place dry chicken gravy mix into another saucepan and gradually whisk in the water until smooth. Bring the mixture to a boil, reduce heat to medium-low, and simmer until thickened, about 1 minute. Set gravy aside and allow to continue to thicken as it cools."
    tools2 = extract_tools(description2)
    print("\nTagged sentences for second example:")
    for i, sentence in enumerate(tools2, 1):
        print(f"Sentence {i}: {sentence}")

    # Test with the user's example
    description3 = "Press one of the pie crusts into the bottom of a 9-inch pie dish. Spoon a layer of gravy (about 1/3 cup) into the crust. Layer the cooked vegetables and shredded chicken into the crust until the filling is level with the top of the pie dish. Pour the rest of the gravy slowly over the filling until gravy is visible at the top. Scatter butter pieces over the filling; top with second crust. Seal the 2 crusts together and crimp with a fork."
    tools3 = extract_tools(description3)
    print("\nTagged sentences for third example:")
    for i, sentence in enumerate(tools3, 1):
        print(f"Sentence {i}: {sentence}")