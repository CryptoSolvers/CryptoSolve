from flask import Flask

app = Flask(__name__)
app.secret_key = "supersecretkeyformoewombatapplications"

from symcollab.moe.website import routes
