# process_recipe/step_components/extract_methods.py
import nltk
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

def collect_hyponyms(root):
    items = set()
    stack = [root]
    while stack:
        node = stack.pop()
        for h in node.hyponyms():
            items.add(h)
            stack.append(h)
    return items

def safe_synset(name):
    try:
        return wn.synset(name)
    except:
        return None

ROOTS = list(filter(None, [
    safe_synset("cook.v.01"),
    safe_synset("prepare.v.01"),
    safe_synset("mix.v.01"),
    safe_synset("heat.v.01"),
]))

def build_method_list():
    synsets = set()
    for root in ROOTS:
        synsets.update(collect_hyponyms(root))

    verbs = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            word = lemma.name().replace("_", " ").lower()
            if len(word.split()) == 1:
                verbs.add(word)

    verbs.update([
        "bake", "boil", "fry", "grill", "saute", "sear", "roast", "toast",
        "stir", "mix", "combine", "whisk", "pour", "serve", "transfer",
        "knead", "slice", "chop", "mince", "fold", "season", "drain",
        "cover", "uncover", "simmer", "heat", "preheat", "blend", "spread",
        "coat", "melt", "beat", "cool", "press", "add", "remove"
    ])
    return verbs

COOKING_METHODS = set(build_method_list())
lemmatizer = WordNetLemmatizer()

def extract_methods(description: str) -> list[str]:
    """
    Identify cooking/preparation methods (verbs) in a recipe step.
    More robust version with lemmatization and regex fallback.
    """
    if not description:
        return []

    description = description.lower()
    tokens = word_tokenize(description)
    tagged = pos_tag(tokens)

    methods = set()

    for word, tag in tagged:
        if tag.startswith("VB"):
            lemma = lemmatizer.lemmatize(word, "v")
            if lemma in COOKING_METHODS:
                methods.add(lemma)

    # Fallback: look for common cooking verbs that may not be tagged
    for verb in COOKING_METHODS:
        if verb in description:
            methods.add(verb)

    return sorted(methods)
