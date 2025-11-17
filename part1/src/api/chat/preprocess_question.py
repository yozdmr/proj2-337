import re
from chat.question_bank import QUESTION_BANK

# Extract step number from question
def extract_step_number(question: str) -> int:
    question_lower = question.lower()
    
    # Mapping of written numbers to digits
    written_numbers = {
        "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
        "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10,
        "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14,
        "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18,
        "nineteenth": 19, "twentieth": 20,
        # Also handle without "th" suffix
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
        "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
        "nineteen": 19, "twenty": 20
    }
    
    # First, try to find written numbers
    # Look for patterns like "second step", "step four", "fourth step", etc.
    for word, num in written_numbers.items():
        # Pattern: word followed by "step" or "step" followed by word
        pattern1 = rf"\b{word}\s+step\b"
        pattern2 = rf"\bstep\s+{word}\b"
        if re.search(pattern1, question_lower) or re.search(pattern2, question_lower):
            return num
    
    # Second, try to find numeric digits
    # Look for patterns like "step 5", "step 6", "5th step", "6 step", etc.
    # Pattern: "step" followed by a number, or number followed by "step"
    numeric_patterns = [
        r"\bstep\s+(\d+)\b",  # "step 5", "step 6"
        r"\b(\d+)\s+step\b",  # "5 step", "6 step"
        r"\b(\d+)(?:st|nd|rd|th)\s+step\b",  # "5th step", "6th step"
        r"\bstep\s+(\d+)(?:st|nd|rd|th)\b",  # "step 5th", "step 6th"
    ]
    
    for pattern in numeric_patterns:
        match = re.search(pattern, question_lower)
        if match:
            return int(match.group(1))
    
    # If no pattern matches, try to find any standalone number in the question
    # This is a fallback for edge cases
    numbers = re.findall(r'\b(\d+)\b', question_lower)
    if numbers:
        # Return the first number found (most likely to be the step number)
        return int(numbers[0])
    
    # If nothing found, return None or raise an error
    # For now, return 1 as a default (though this might not be ideal)
    return 1

def classify_question(question: str) -> str:
    # Normalize question: lowercase, remove punctuation, normalize whitespace
    if "method" in question.lower() or "methods" in question.lower() or "technique" in question.lower():
        if "step" in question.lower():
            return "step_methods"
        else:
            return "all_methods"
    question_normalized = question.lower().strip()
    question_normalized = re.sub(r"[^\w\s]", "", question_normalized)
    question_normalized = " ".join(question_normalized.split())
    
    # Get question words (excluding common stop words for better matching)
    stop_words = {"a", "an", "the", "is", "are", "what", "which", "when", "where", "who", "why", "yes", "no"}
    question_words = set(w for w in question_normalized.split() if w not in stop_words)
    
    best_match = None
    best_match_score = 0
    exact_match_found = False
    
    # Check each question bank for matches
    for bank in QUESTION_BANK:
        for key_phrase, category in bank.items():
            # Normalize key phrase the same way
            key_normalized = key_phrase.lower().strip()
            key_normalized = re.sub(r"[^\w\s]", "", key_normalized)
            key_normalized = " ".join(key_normalized.split())
            
            # Get key words (excluding stop words)
            key_words = set(w for w in key_normalized.split() if w not in stop_words)
            
            # Step 1: Exact match (highest priority - should win over everything)
            if key_normalized == question_normalized:
                exact_match_found = True
                best_match = category
                best_match_score = float('inf')  # Highest possible score
                continue
            
            # Step 2: Exact substring match (only if no exact match found yet)
            if not exact_match_found:
                if key_normalized in question_normalized or question_normalized in key_normalized:
                    # For single-word questions, prevent matching against long multi-word keys
                    # This prevents "step" from matching "ingredients are used in this step"
                    question_word_count = len(question_words)
                    key_word_count = len(key_words)
                    
                    # Single-word questions should only match single-word or two-word keys
                    if question_word_count == 1 and key_word_count > 2:
                        continue
                    
                    # Prefer longer matches (more specific)
                    score = len(key_normalized)
                    if score > best_match_score:
                        best_match = category
                        best_match_score = score
                # Step 3: Word overlap (makes it more flexible)
                elif key_words and question_words:
                    # Calculate overlap: how many key words appear in question
                    overlap = len(key_words & question_words)
                    # Score based on overlap ratio (prefer matches with more overlap)
                    overlap_ratio = overlap / len(key_words)
                    # Also consider the length of the key (prefer longer, more specific keys)
                    score = overlap_ratio * len(key_normalized)
                    
                    # Require at least 50% word overlap to consider it a match
                    if overlap_ratio >= 0.5 and score > best_match_score:
                        best_match = category
                        best_match_score = score
    
    return best_match if best_match else "none"