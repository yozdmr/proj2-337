# Part 2

## Setup

You will need your own Gemini API key per the instructions in Canvas, saved as `GEMINI_API_KEY` in a `.env` file.

Run the app using `python app.py` while in the `/part2` directory. You can also reuse the front end from Part 1, per the instructions in `/part1/README.md`. If the front end from Part 1 and the back end from Part 2 is running, they will work together seamlessly. 

## Using Part 2 Without the Frontend

You can use Curl requests in the terminal to communicate with the API without needing a front-end.

### Loading the recipe

```bash
curl -X POST http://localhost:8080/get-recipe \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.allrecipes.com/recipe/219491/to-die-for-chicken-pot-pie/"}'
```

### Asking a question

Include the "nohtml" tag if you want the output to not be formatted using HTML tags. Remove if if you want to see the HTML formatted output.

```bash
curl -X POST http://localhost:8080/ask-question \
  -H "Content-Type: application/json" \
  -d '{"question":"What ingredients do I need for this recipe?", "nohtml": "true"}'
```

### Resetting the chat

```bash
curl -X POST http://localhost:8080/reset
```