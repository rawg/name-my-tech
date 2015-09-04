
from flask import Flask, request, render_template
import random
from expansions import expand

app = Flask(__name__, static_url_path="")

@app.route("/", methods=["POST", "GET"])
def render_name():
    themes = []
    expression = ""
    name = ""

    if len(request.values.get("expression", "").strip()) > 0:
        expression = request.values.get("expression")
        name = expand(expression)

    else:
        themes = request.values.getlist("theme")
        if not isinstance(themes, list):
            themes = ["buzzword"]

        buzz_patterns = []
        dict_patterns = []

        for theme in themes:
            buzz_patterns.append("{prefix}{%s|few}" % theme)
            buzz_patterns.append("{%s|few}{suffix}" % theme)
            buzz_patterns.append("{%s|several}" % theme)
            dict_patterns.append("{dict %s|several}" % theme)

        if random.random() > .7:
            pattern = random.choice(dict_patterns)
        else:
            pattern = random.choice(buzz_patterns)

        name = expand(pattern)


    return render_template("index.html", name=name, themes=themes, expression=expression)


if __name__ == "__main__":
    app.run()

