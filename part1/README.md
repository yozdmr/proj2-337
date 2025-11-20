# Part 1

Rules based recipe parser + conversational interface.

Run front-end and back-end simultaneously on ports 3000 and 8080 respectively, per the instructions below. Then use the front-end to query the API and talk with the chatbot.

## Front-end Web App

Simple one-page web app built using NextJS. It will send calls to the backend Flask API and display them to the user.

- **Node.js**: v23.11.0 (or use the version specified in `.nvmrc`)
- **npm**: v9.0.0 or higher (comes with Node.js)

### Setup Instructions

Manually install Node.js v23.11.0 from [nodejs.org](https://nodejs.org/).

#### 1. Install Dependencies

```bash
npm install
```

This will install all dependencies specified in `package.json` and `package-lock.json`.

#### 2. Run Development Server

```bash
npm run dev
```

Open [http://127.0.0.1:3000](http://127.0.0.1:3000) with your browser to see the website.



## Back-end API

**MAKE SURE** you have set up the Conda environment per the main README.

**NOTE** That you will also need to set up the `.env` file in `part1/src/api/`.

The Flask API will run in the background and take a URL as input. It will then process the URL to extract ingredients and steps, and save these within the program. Once this is done the Chat agent (also built into the Flask API) will leverage this information to talk to the user.

Get your API key from [spoonacular.com](spoonacular.com). Store it in the `.env` file in `part1/src/api/`:

```bash
SPOONACULAR_API_KEY=<api_key>
```

Run the Flask app by navigating into the `part1/src/api/` folder, then running `python app.py`. This will run the app on port `8080`. Visit the API at `http://127.0.0.1:8080`, you should see `OK`.

Run a sample call to the ingredient retreival using the command below:
```bash
curl -X POST http://localhost:8080/get-recipe \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.allrecipes.com/recipe/219491/to-die-for-chicken-pot-pie/"}'
```

Or, use the front-end web application on `http://127.0.0.1:3000`


### Debugging

View extracted ingredients by visiting `http://127.0.0.1:8080/get-ingredients`

View extracted steps by visiting `http://127.0.0.1:8080/get-steps`
