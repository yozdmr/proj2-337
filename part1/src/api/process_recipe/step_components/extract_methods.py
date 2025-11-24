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

def _find_best_match(word: str, methods: set[str]) -> str | None:
    word_lower = word.lower()
    
    # First, try exact match
    if word_lower in methods:
        return word_lower
    
    # Try lemmatized form
    lemma = lemmatizer.lemmatize(word_lower, "v")
    if lemma in methods:
        return lemma
    
    # Find best closest match - prefer longer matches
    # This handles cases where a word contains a method as a substring
    best_match = None
    best_score = 0
    
    for method in methods:
        # Check if word starts with method (e.g., "preheating" contains "preheat")
        # We want the longest matching method
        if word_lower.startswith(method) and len(method) > best_score:
            best_match = method
            best_score = len(method)
        # Check if method starts with word (e.g., word is "heat" and method is "preheat")
        # This is less common but possible
        elif method.startswith(word_lower) and len(word_lower) > best_score:
            best_match = method
            best_score = len(word_lower)
    
    # Only return if we found a reasonably good match (at least 3 characters)
    # This prevents false matches on very short substrings
    if best_match and best_score >= 3:
        return best_match
    
    return None

def extract_methods(description: str) -> list[str]:
    if not description:
        return []

    description = description.lower()
    tokens = word_tokenize(description)
    tagged = pos_tag(tokens)

    methods = set()
    processed_words = set()  # Track words we've already processed

    # Process each word individually to avoid multiple matches from one word
    for word, tag in tagged:
        if tag.startswith("VB"):
            # Try exact match first (word itself or lemmatized form)
            match = _find_best_match(word, COOKING_METHODS)
            if match:
                methods.add(match)
                processed_words.add(word)

    # Fallback: check for methods that weren't tagged as verbs but are in our methods list
    # This handles cases where words like "Preheat" or "Season" are mis-tagged
    # (e.g., sometimes tagged as NN/NNP at sentence start, though rare)
    # Check the first two words of each comma-delimited chunk (or just that word if chunk is 1 word)
    # This handles imperative verbs that appear at the start of clauses
    chunks = description.split(',')
    for chunk in chunks:
        chunk_tokens = word_tokenize(chunk.strip())
        # If chunk has 1 word, check that word; otherwise check first two words
        words_to_check = chunk_tokens[:1] if len(chunk_tokens) == 1 else chunk_tokens[:2]
        for word in words_to_check:
            if word not in processed_words:  # Skip if already processed as a verb
                match = _find_best_match(word, COOKING_METHODS)
                if match:
                    methods.add(match)
                    processed_words.add(word)

    return sorted(methods)
