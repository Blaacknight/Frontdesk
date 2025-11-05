Frontdesk AI Supervisor Project

This project is a simulation of a Human-in-the-Loop (HITL) system for a "Frontdesk" AI agent.

agent.py: A Python script that simulates an AI agent. It checks a Firestore database for answers and escalates to a human if it doesn't know the answer.

supervisor.html: A simple, local admin panel (UI) for a human supervisor. It listens for new requests in real-time and allows the supervisor to submit answers.

requirements.txt: The necessary Python libraries.

Setup: Step-by-Step

1. Firebase Setup (The "Backend")

This is the only manual setup step. We need to create the central database and get two sets of credentials.

A. Create the Project:

Go to the Firebase Console.

Click "Add project" and name it (e.g., frontdesk-hitl-demo).

Accept the terms and create the project. You can disable Google Analytics.

B. Create the Firestore Database:

In your project, click "Firestore Database" from the side menu.

Click "Create database".

Start in Test Mode. This is important for development.

Choose a location (e.g., us-central).

Click "Enable".

Click "+ Start collection":

Collection ID: help_requests

Click "Next", then "Auto-ID", add a dummy field (e.g., status: "test"), and "Save".

Click "+ Start collection" again:

Collection ID: knowledge_base

Click "Next", then "Auto-ID", add a dummy field (e.g., query: "test"), and "Save".

C. Get supervisor.html Credentials (Already Done!):

The firebaseConfig object for the web app has already been added to supervisor.html. You don't need to do anything for this file.

D. Get agent.py Credentials (CRITICAL):

In your Firebase project, click the Gear icon (Project Settings) next to "Project Overview".

Go to the "Service Accounts" tab.

Click the button that says "Generate new private key".

A JSON file will download. Rename this file to serviceAccountKey.json.

Place this serviceAccountKey.json file in the exact same folder as your agent.py script.

2. Python Environment Setup

Open your terminal or command prompt in your project folder.

(Recommended) Create a virtual environment:

python -m venv venv
source venv/bin/activate  # On Mac/Linux
.\venv\Scripts\activate   # On Windows


Install the required libraries from requirements.txt:

pip install -r requirements.txt


3. Run the Full Application (The Demo)

You'll need two windows open.

Window 1: The Supervisor UI

Find the supervisor.html file in your project folder.

Double-click it to open it in your web browser (Chrome, Firefox, etc.).

Open the Developer Console (Cmd+Opt+J or Ctrl+Shift+J) so you can see the logs.

The UI will show "No pending requests. Listening...".

Window 2: The AI Agent

Go to your terminal, which should be in the same project folder.

Make sure your serviceAccountKey.json is present.

Run the Python script:

python agent.py


How to Watch the Demo

As soon as you run python agent.py:

Look at your terminal: The agent will run "Simulation 1". It will print that it "Knowledge not found" and is "Escalating to supervisor".

Look at your browser: Almost instantly, a new "Pending" card will appear in your Supervisor UI.

In the browser UI:

Type an answer into the text box for the "balayage" question. (e.g., "Yes, we do! It's $150.")

Click the "Resolve" button.

Look at the browser console: You will see a log SIMULATED TEXT-BACK... confirming the follow-up. The card will move from "Pending" to "Recently Resolved".

Look back at your terminal: The Python script waited 10 seconds. It will now run "Simulation 2" with the same query. This time, it will print "Knowledge found!" and will not escalate.

Finally, it will run "Simulation 3" with a new query, which will create a second "Pending" card in your UI.