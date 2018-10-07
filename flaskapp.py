from flask import Flask, render_template, request, redirect
import json
import query
app = Flask(__name__)

@app.route("/",methods=['GET'])
def main():
    queryTerm = request.args.get("queryTerm")
    if queryTerm: # only the term is not None, run the automation script
        print("The query term  is '" + queryTerm + "'")
        global query_result
        global query_github
        map_openhub = query.queryOpenHub(queryTerm)
        map_github = query.queryGithub(queryTerm)
        map_score = query.calculateScores(map_github, map_openhub);
        json_openhub = json.dumps({"result":map_openhub})
        json_github = json.dumps({"result":map_github})
        json_score = json.dumps({"result":map_score})
        query_result = json.loads(json_openhub)
        query_github = json.loads(json_github)
        query_score = json.loads(json_score)
          #url = query_github["result"]["github_url"]
          #url = result["result"]["project_html_url"]
          #return url
        return render_template("assess.html", result=query_result["result"], res=query_github["result"], score=query_score["result"])
    else:
        return render_template("index.html")

@app.route('/detail', methods=['GET'])
def detail():
    global query_result
    global query_github
    return render_template("query.html", result=query_result["result"], res=query_github["result"])
		
@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html")

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)