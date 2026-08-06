document.addEventListener("DOMContentLoaded",()=>{

console.log("Hostel Management System Loaded");

const forms=document.querySelectorAll("form");

forms.forEach(form=>{

form.addEventListener("submit",()=>{

const button=form.querySelector("button");

if(button){

button.disabled=true;

button.innerHTML="Processing...";

}

});

});

// -----------------------------
// Charts
// -----------------------------

if(document.getElementById("roomChart")){

fetch("/chart-data")

.then(response=>response.json())

.then(data=>{

new Chart(

document.getElementById("roomChart"),

{

type:"pie",

data:{

labels:data.room_labels,

datasets:[{

data:data.room_values,

backgroundColor:[

"#28a745",

"#dc3545"

]

}]

}

}

);

new Chart(

document.getElementById("complaintChart"),

{

type:"bar",

data:{

labels:data.complaint_labels,

datasets:[{

label:"Complaints",

data:data.complaint_values,

backgroundColor:"#0d6efd"

}]

}

}

);

});

}

});