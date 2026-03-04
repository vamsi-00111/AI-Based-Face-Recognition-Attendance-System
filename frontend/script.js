async function register(){

    let formData = new FormData()

    formData.append("student_id",document.getElementById("student_id").value)
    formData.append("name",document.getElementById("name").value)
    formData.append("file",document.getElementById("image").files[0])

    let response = await fetch("http://127.0.0.1:8000/register",{
        method:"POST",
        body:formData
    })

    let result = await response.json()

    console.log(result)   // VERY IMPORTANT
    alert(JSON.stringify(result))
}



async function startAttendance(){

    let response = await fetch("http://127.0.0.1:8000/start")

    let result = await response.json()

    alert(result.message)

}
async function getAttendance(){

    let date = document.getElementById("date").value

    let response = await fetch(`http://127.0.0.1:8000/attendance/date/${date}`)

    let data = await response.json()

    let resultDiv = document.getElementById("attendance_result")

    resultDiv.innerHTML = ""

    data.records.forEach(student => {

        resultDiv.innerHTML += `
        <p>
        ${student.student_id} - ${student.name} - ${student.time}
        </p>
        `
    })
}


async function totalAttendance(){

    let id = document.getElementById("student_search").value

    let response = await fetch(`http://127.0.0.1:8000/attendance/student/${id}`)

    let data = await response.json()

    document.getElementById("total_result").innerHTML =
        `Total Present Days: ${data.total_present}`
}