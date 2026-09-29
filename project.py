from flask import Flask, render_template_string, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = "fixmyride_secret"

# -----------------------------
# IN-MEMORY DATABASE
# -----------------------------
users = {}
mechanics = []
requests_list = []

# -----------------------------
# HTML TEMPLATE
# -----------------------------
page = """
<!DOCTYPE html>
<html>
<head>
<title>🚗FixMyRide🔧</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body {
    margin:0;
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color:white;
}

nav {
    display:flex;
    justify-content:space-between;
    padding:15px 30px;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
}

nav h2 {margin:0;}

button {
    padding:10px 15px;
    border:none;
    border-radius:8px;
    cursor:pointer;
}

.container {
    padding:20px;
}

.card {
    background: rgba(255,255,255,0.1);
    padding:20px;
    margin:10px 0;
    border-radius:15px;
    backdrop-filter: blur(10px);
}

input, select {
    width:100%;
    padding:10px;
    margin:5px 0;
    border-radius:8px;
    border:none;
}

#map {
    width:100%;
    height:300px;
    border-radius:10px;
}

.chatbox {
    height:200px;
    overflow:auto;
    background:#111;
    padding:10px;
    border-radius:10px;
}

.toast {
    position:fixed;
    bottom:20px;
    right:20px;
    background:#333;
    padding:10px;
    border-radius:8px;
}
</style>
</head>

<body>

<nav>
    <h2>🚗FixMyRide🔧</h2>
    <div>
        <button onclick="show('home')">Home</button>
        <button onclick="show('login')">Login</button>
        <button onclick="show('register')">Register</button>
        <button onclick="show('dashboard')">Dashboard</button>
    </div>
</nav>

<div class="container">

<div id="home">
    <div class="card">
        <h2>Find Nearby Mechanics 🚗</h2>
        <button onclick="getLocation()">Get Location</button>
        <div id="map"></div>
    </div>

    <div class="card">
        <h3>Search Mechanics</h3>
        <input id="district" placeholder="Enter location">
        <button onclick="searchMechanics()">Search</button>
        <div id="mechanics"></div>
    </div>

    <div class="card">
        <h3>Emergency 🚨</h3>
        <button onclick="emergency()">Send Emergency Request</button>
    </div>
</div>

<div id="login" style="display:none">
    <div class="card">
        <h3>Login</h3>
        <input id="luser" placeholder="Username">
        <input id="lpass" type="password" placeholder="Password">
        <button onclick="login()">Login</button>
    </div>
</div>

<div id="register" style="display:none">
    <div class="card">
        <h3>Register</h3>
        <input id="ruser" placeholder="Name">
        <input id="rphone" placeholder="Phone">
        <input id="rpass" placeholder="Password">
        <button onclick="register()">Register</button>
    </div>
</div>

<div id="dashboard" style="display:none">
    <div class="card">
        <h3>AI Chatbot 🤖</h3>
        <div class="chatbox" id="chat"></div>
        <input id="msg">
        <button onclick="sendMsg()">Send</button>
    </div>

    <div class="card">
        <h3>AI Cost Estimator 💰</h3>
        <input id="problem" placeholder="Enter issue">
        <button onclick="estimate()">Estimate</button>
        <p id="cost"></p>
    </div>

    <div class="card">
        <h3>Register Mechanic 🔧</h3>
        <input id="mname" placeholder="Name">
        <input id="mphone" placeholder="Phone">
        <input id="mlocation" placeholder="Location">
        <input id="mspec" placeholder="Specialization">
        <button onclick="addMechanic()">Register</button>
    </div>
</div>

</div>

<div id="toast" class="toast" style="display:none"></div>

<script>

function show(id){
    document.querySelectorAll('.container > div').forEach(x=>x.style.display='none');
    document.getElementById(id).style.display='block';
}

function toast(msg){
    let t=document.getElementById('toast');
    t.innerText=msg;
    t.style.display='block';
    setTimeout(()=>t.style.display='none',2000);
}

function register(){
    fetch('/register',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            user:ruser.value,
            phone:rphone.value,
            pass:rpass.value
        })
    }).then(r=>r.json()).then(d=>toast(d.msg));
}

function login(){
    fetch('/login',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            user:luser.value,
            pass:lpass.value
        })
    }).then(r=>r.json()).then(d=>{
        toast(d.msg);
        if(d.success) show('dashboard');
    });
}

function getLocation(){
    navigator.geolocation.getCurrentPosition(pos=>{
        let lat=pos.coords.latitude;
        let lon=pos.coords.longitude;
        document.getElementById('map').innerHTML=
        `<iframe width="100%" height="300" src="https://maps.google.com/maps?q=${lat},${lon}&z=15&output=embed"></iframe>`;
    });
}

function searchMechanics(){
    fetch('/mechanics?loc='+district.value)
    .then(r=>r.json())
    .then(data=>{
        mechanics.innerHTML="";
        data.forEach(m=>{
            mechanics.innerHTML+=`<div>${m.name} - ${m.spec}</div>`;
        });
    });
}

function emergency(){
    fetch('/emergency',{method:'POST'})
    .then(r=>r.json())
    .then(d=>toast(d.msg));
}

function sendMsg(){
    fetch('/chat',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({msg:msg.value})
    }).then(r=>r.json())
    .then(d=>{
        chat.innerHTML+=`<div>You: ${msg.value}</div>`;
        chat.innerHTML+=`<div>AI: ${d.reply}</div>`;
    });
}

function estimate(){
    fetch('/estimate',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({problem:problem.value})
    }).then(r=>r.json())
    .then(d=>cost.innerText=d.cost);
}

function addMechanic(){
    fetch('/add_mechanic',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            name:mname.value,
            phone:mphone.value,
            location:mlocation.value,
            spec:mspec.value
        })
    }).then(r=>r.json())
    .then(d=>toast(d.msg));
}

</script>

</body>
</html>
"""

# -----------------------------
# ROUTES
# -----------------------------
@app.route('/')
def home():
    return render_template_string(page)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    users[data['user']] = data
    return jsonify({"msg":"Registered Successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data['user'] in users and users[data['user']]['pass']==data['pass']:
        session['user']=data['user']
        return jsonify({"success":True,"msg":"Login Success"})
    return jsonify({"success":False,"msg":"Invalid Credentials"})

@app.route('/add_mechanic', methods=['POST'])
def add_mechanic():
    mechanics.append(request.json)
    return jsonify({"msg":"Mechanic Added"})

@app.route('/mechanics')
def get_mechanics():
    loc = request.args.get('loc','')
    res = [m for m in mechanics if loc.lower() in m['location'].lower()]
    return jsonify(res)

@app.route('/emergency', methods=['POST'])
def emergency():
    if mechanics:
        m = random.choice(mechanics)
        requests_list.append(m)
        return jsonify({"msg":"Request sent to "+m['name']})
    return jsonify({"msg":"No mechanics available"})

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json['msg'].lower()
    if "engine" in msg:
        reply="Check engine oil and battery."
    elif "tyre" in msg:
        reply="Check tyre pressure or puncture."
    else:
        reply="Try restarting or contact a mechanic."
    return jsonify({"reply":reply})

@app.route('/estimate', methods=['POST'])
def estimate():
    problem = request.json['problem'].lower()
    if "engine" in problem:
        cost="₹3000 - ₹8000"
    elif "tyre" in problem:
        cost="₹200 - ₹1000"
    else:
        cost="₹500 - ₹2000"
    return jsonify({"cost":cost})

# -----------------------------
# RUN
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)