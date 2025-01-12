import flask, time, creds
import google.generativeai as genai
genai.configure(api_key=creds.geminitoken)
model = genai.GenerativeModel("gemini-1.5-flash")
app = flask.Flask(__name__)
formQuestions = ["What is your team number?", "What is your team name?", "What is the weight of your robot? (In pounds)", "How does your robot score?", "What motors propel your drivetrain?", "Where do you intake from?", "Does your robot use pneumatics?", "How many batteries are on your robot?", "How experienced is your driver?", "Have you had this same driver in previous years?", "Is your human player practiced?", "How consistent is your auto?", "Is there anything about your team you think we should be aware of?"]
genCache = 0
theme = {"logo":"ferretlogofrozen.png", "bg":"ferretbgfrozen.png","teamlogo":"placeholder.jpg","loading":"ferretload.gif","tiktok":"placeholder.png","facebook":"placeholder.png","twitter":"placeholder.png","name":"Placeholder Robotics"}
verstring = "Ferret v1.2 PROD"
print(verstring)
def getQuestionCode():
    toReturn = ""
    i2 = 0
    for i in formQuestions:
        i2 += 1
        toReturn = toReturn + f"""<div class="question">{i}<br><input id="{i2}"></input></div><br><br>"""
    return toReturn

def getQuestionJS():
    toReturn = "window.location.href = \"/submit/?"
    i2 = 0
    for i in formQuestions:
        i2 += 1
        toReturn = toReturn + f"{i2}=\"+$(\"#{i2}\").val()+\"&"
    toReturn = toReturn + "a=a\";"
    return toReturn

def parseResponses():
    file = open("responses.txt", "r")
    answers = file.read().split("\n-----\n")
    answers2 = []
    for i in answers:
        if not i.replace(" ", "").replace("-","").replace("\n", "") == "":
            answers3 = []
            for i2 in i.split("\n"):
                if not i2.replace(" ", "").replace("-","").replace("\n", "") == "":
                    answers3.append({"number":i2.split(":::")[0],"name":i2.split(":::")[1],"answer":i2.split(":::")[2]})
            answers2.append({"number":answers3[0]["answer"],"name":answers3[1]["answer"],"answers":answers3})
    file.close()
    return answers2

def genBestTeams():
    responses = parseResponses()
    toSend = "Please choose the best FIRST robotics team in the list below. Please only respond with the team number. Generate 3 teams in order of how good they are. If there isn't enough teams, replace the missing teams with \"N/A\". If there aren't ANY teams, put all three teams as \"N/A\".\n"
    for i in parseResponses():
        toSend = toSend + "\n----------\n\n"
        for i2 in i["answers"]:
            number = i2["number"]
            name = i2["name"]
            answer = i2["answer"]
            toSend = toSend + f"\n{number}: {name}: {answer}"
    response = model.generate_content(toSend).text
    return response.replace("\n\n","\n").split("\n")

def getNameFromNumber(team):
    responses = parseResponses()
    name = None
    for i in responses:
        if i["number"] == team:
            name = i["name"]
    return name

@app.route("/")
def index():
    return flask.render_template("index.html", verstring=verstring)

@app.route("/favicon.ico")
def favicon():
    return flask.send_file("ferretlogo2.ico")

@app.route("/global.css")
def globalcss():
    return flask.send_file("global.css")

@app.route("/logo.png")
def logo():
    return flask.send_file(theme["logo"])

@app.route("/bg.png")
def bg():
    return flask.send_file(theme["bg"])

@app.route("/teamlogo.jpg")
def teamlogo():
    return flask.send_file(theme["teamlogo"])

@app.route("/isFerretServer")
def isFerretServer():
    return "true"

@app.route("/analytics/")
def analytics():
    if not flask.request.args.get("load") == "y":
        bestTeams = genBestTeams()
        try:
            firstTeam = bestTeams[0]
        except:
            firstTeam = "Error"
        try:
            secondTeam = bestTeams[1]
        except:
            secondTeam = "Error"
        try:
            thirdTeam = bestTeams[2]
        except:
            thirdTeam = "Error"
        return flask.render_template("analyticsdashboard.html", firstTeamNumber = firstTeam, firstTeamName = getNameFromNumber(firstTeam), secondTeamNumber = secondTeam, secondTeamName = getNameFromNumber(secondTeam), thirdTeamNumber = thirdTeam, thirdTeamName = getNameFromNumber(thirdTeam), compliment=model.generate_content("Tell me a compliment! Be creative! The only requirement is you are expected to send only the compliment.").text, verstring=verstring)
    else:
        return flask.render_template("loading.html", text="We're preparing your AI-generated analytics!\nPlease wait!<br><br>No WiFi? <a href=\"/teams/\">Go to per-team analytics</a>", url="/analytics/", verstring=verstring)

@app.route("/form/")
def form():
    return flask.render_template("form.html", form=getQuestionCode(), questionJS = getQuestionJS(), verstring=verstring, teamname=theme["name"])

@app.route("/submit/")
def submit():
    i2 = 0
    toWrite = ""
    for i in formQuestions:
        i2 += 1
        answer = flask.request.args.get(str(i2))
        if answer == "":
            answer = "<no response>"
        toWrite=toWrite+f"{i2}:::{i}:::{answer}\n"
    toWrite=toWrite+"-----\n"
    file = open("responses.txt", "a")
    file.write(toWrite)
    file.close()
    return "<script>window.location.href = \"/thankyou/\"</script>"

@app.route("/thankyou/")
def thankyou():
    return flask.render_template("thankyou.html", verstring=verstring, name=theme["name"])

@app.route("/teams/")
def teams():
    if not flask.request.args.get("load") == "y":
        if flask.request.args.get("team") == None:
            responses = parseResponses()
            code = ""
            for i in responses:
                number = i["number"]
                name = i["name"]
                code = code + f"<a href=\"/teams/?team={number}\" class=\"inline\"><span class=\"buttn inline\">{number} - {name}</span></a>"
            return flask.render_template("teams.html", buttonCode = code, verstring=verstring)
        else:
            responses = parseResponses()
            code = ""
            for i in responses:
                number = i["number"]
                name = i["name"]
                code = code + f"<a href=\"/teams/?team={number}\" class=\"inline\"><span class=\"buttn inline\">{number} - {name}</span></a>"
            questionCode = ""
            for i in responses:
                if i["number"] == flask.request.args.get("team"):
                    for i2 in i["answers"]:
                        number = i2["number"]
                        name = i2["name"]
                        answer = i2["answer"]
                        questionCode = questionCode + f"<p>({number}) {name}: {answer}<p>"
            return flask.render_template("teamanalytics.html", buttonCode = code, teamNumber = flask.request.args.get("team"), teamName = getNameFromNumber(flask.request.args.get("team")), questionCode = questionCode, verstring=verstring)
    else:
        return flask.render_template("loading.html", text="We're preparing the list of teams!\nPlease wait!", url="/teams/", verstring=verstring)

@app.route("/bluesky/")
def bluesky():
    return flask.render_template("image.html", image="/bluesky.png", verstring=verstring)

@app.route("/bluesky.png")
def blueskypng():
    return flask.send_file("bluesky.png")

@app.route("/facebook/")
def facebook():
    return flask.render_template("image.html", image="/facebook.png", verstring=verstring)

@app.route("/facebook.png")
def facebookpng():
    return flask.send_file(theme["facebook"])

@app.route("/twitter/")
def twitter():
    return flask.render_template("image.html", image="/twitter.png", verstring=verstring)

@app.route("/twitter.png")
def twitterpng():
    return flask.send_file(theme["twitter"])

@app.route("/tiktok/")
def tiktok():
    return flask.render_template("image.html", image="/tiktok.png", verstring=verstring)

@app.route("/tiktok.png")
def tiktokpng():
    return flask.send_file(theme["tiktok"])

@app.route("/load.gif/")
def ferretload():
    return flask.send_file(theme["loading"])
