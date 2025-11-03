# Part 1

Rules based recipe parser + conversational interface


## Back-end API

The Flask API will run in the background and take a URL as input. It will then process the URL to extract ingredients and steps, and save these within the program. Once this is done the Chat agent (also built into the Flask API) will leverage this information to talk to the user.

Run the Flask app by navigating into the `part1/src/api/` folder, then running `python app.py`. This will run the app on port `8080`. Visit the site at `http://127.0.0.1:8080`, you should see `OK`.

Run a sample call to the ingredient retreival using the command below:
```
curl -X POST http://localhost:8080/get-recipe \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.allrecipes.com/copycat-cracker-barrel-fried-apples-recipe-11808171"}'
```

Another link: https://www.allrecipes.com/recipe/16049/granny-kats-pumpkin-roll/

View the extracted ingredients by visiting `http://127.0.0.1:8080/get-ingredients`


## Front-end UI

Hopefully a simple ReactJS front-end can be built as well to leverage the API and create an interface to talk to the chatbot. This front-end app should be built inside the directory `src/app/`.